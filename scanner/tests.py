from django.test import TestCase, Client
from django.urls import reverse
from scanner.models import Technician, Chip, Price, NonCodePrice, ScanHistory, ApprovalRequest, Notification
from scanner.seeder import seed_database_if_empty
from scanner.views import check_tech_password
from scanner.ocr_pipeline import (
    compute_match_score, normalize_text, hamming_distance,
    match_chip_heuristics
)
import hashlib

class ScannerAppTests(TestCase):

    def setUp(self):
        # We start with an empty DB. The seeder will run.
        pass

    def test_database_lazy_seeding(self):
        """
        Verify that seeder properly populates the db when it is empty.
        """
        # Initially empty
        self.assertEqual(Technician.objects.count(), 0)
        self.assertEqual(Chip.objects.count(), 0)
        
        # Trigger seeder
        seeded = seed_database_if_empty()
        self.assertTrue(seeded)
        
        # Verify default accounts
        self.assertTrue(Technician.objects.filter(username='admin', role='admin').exists())
        self.assertTrue(Technician.objects.filter(username='tech1', role='tech').exists())
        
        # Verify standard prices (5 grades * 2 roles = 10 prices)
        self.assertEqual(Price.objects.count(), 10)
        
        # Verify sizes (7 sizes * 2 roles = 14 prices)
        self.assertEqual(NonCodePrice.objects.count(), 14)
        
        # Verify at least 28 standard chips
        self.assertGreaterEqual(Chip.objects.count(), 28)
        
        # Re-running seeder should do nothing and return False
        seeded_again = seed_database_if_empty()
        self.assertFalse(seeded_again)

    def test_custom_password_verification(self):
        """
        Tests fallback password check support (Plaintext, MD5, and Django hashers).
        """
        seed_database_if_empty()
        
        # 1. Test standard seeded user password checking
        tech1 = Technician.objects.get(username='tech1')
        self.assertTrue(check_tech_password(tech1.password, 'tech123'))
        
        # 2. Test plain text fallback
        tech_plain = Technician.objects.create(username='plain_tech', password='plainpassword123', role='tech')
        self.assertTrue(check_tech_password(tech_plain.password, 'plainpassword123'))
        
        # 3. Test raw MD5 hex fallback (32 characters)
        md5_pass = hashlib.md5('md5password123'.encode('utf-8')).hexdigest()
        tech_md5 = Technician.objects.create(username='md5_tech', password=md5_pass, role='tech')
        self.assertTrue(check_tech_password(tech_md5.password, 'md5password123'))
        
        # 4. Test wrong password fails
        self.assertFalse(check_tech_password(tech1.password, 'wrongpassword'))

    def test_ocr_match_scoring_heuristics(self):
        """
        Tests heuristic match scoring on model codes, aliases, and alternate codes.
        """
        seed_database_if_empty()
        
        # Retrieve the pre-seeded chip
        test_chip = Chip.objects.get(code='KM2V7001JM-B517')
        
        # Exact code match
        score = compute_match_score(normalize_text('KM2V7001JM-B517'), test_chip)
        self.assertGreaterEqual(score, 0.95)
        
        # Alias match
        score_alias = compute_match_score(normalize_text('KM128'), test_chip)
        self.assertGreaterEqual(score_alias, 0.85)
        
        # Alternate code match
        score_alt = compute_match_score(normalize_text('KM2V7001JM'), test_chip)
        self.assertGreaterEqual(score_alt, 0.85)
        
        # Noise prefix match (boost check)
        # Scan reads "SAMSUNG KM2V7001JMB517"
        score_noise = compute_match_score(normalize_text('SAMSUNGKM2V7001JMB517'), test_chip)
        self.assertGreaterEqual(score_noise, 0.70)
        
        # Completely different text should score very low
        score_diff = compute_match_score(normalize_text('QUALCOMMSDM845'), test_chip)
        self.assertLess(score_diff, 0.40)

    def test_perceptual_hash_hamming_distance(self):
        """
        Verify visual match criteria using Hamming distance.
        """
        # Distance between identical hashes is 0
        h1 = "f0f0f0f0f0f0f0f0e0e0e0e0e0e0e0e0"
        self.assertEqual(hamming_distance(h1, h1), 0)
        
        # Hamming distance of 1 bit difference
        h2 = "f0f0f0f0f0f0f0f0e0e0e0e0e0e0e0e1" # 0 -> 1 at the end
        self.assertEqual(hamming_distance(h1, h2), 1)
        
        # Distances within the visual match threshold (<= 10)
        h3 = "f0f0f0f0f0f0f0f0e0e0e0e0e0e0e0ff" # 8 bits differ at the end
        self.assertLessEqual(hamming_distance(h1, h3), 10)
        
        # Distances outside visual match threshold (> 10)
        h4 = "00000000000000000000000000000000" # 64 bits differ
        self.assertGreater(hamming_distance(h1, h4), 10)
        
        # Handle invalid hashes gracefully
        self.assertEqual(hamming_distance(h1, "short_hash"), 999)
        self.assertEqual(hamming_distance("", h1), 999)

    def test_api_login_view(self):
        """
        Test the API login endpoint (Credentials and Age-Gated Mock Google Login).
        """
        seed_database_if_empty()
        client = Client()
        
        # 1. Try incorrect credential login
        response = client.post(
            reverse('api_login'),
            data=json.dumps({'username': 'tech1', 'password': 'wrongpassword'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        
        # 2. Try correct credential login
        response = client.post(
            reverse('api_login'),
            data=json.dumps({'username': 'tech1', 'password': 'tech123'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['username'], 'tech1')
        
        # 3. Google mock age gate under 18 rejection
        response = client.post(
            reverse('api_login'),
            data=json.dumps({'provider': 'google', 'birth_year': 2018}), # Under 18
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
        
        # 4. Google mock age gate over 18 success
        response = client.post(
            reverse('api_login'),
            data=json.dumps({'provider': 'google', 'birth_year': 2000}), # Over 18
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['username'], 'google_user')

    def test_api_scan_manual(self):
        """
        Verify that manually searching a chip writes to ScanHistory with the right parameters.
        """
        seed_database_if_empty()
        client = Client()
        
        # Log in first
        client.post(
            reverse('api_login'),
            data=json.dumps({'username': 'tech1', 'password': 'tech123'}),
            content_type='application/json'
        )
        
        # Post manual scan
        response = client.post(
            reverse('api_scan_manual'),
            data=json.dumps({'code': 'KLUEG8UHDB-C2D1'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['scan']['code'], 'KLUEG8UHDB-C2D1')
        self.assertEqual(data['scan']['scan_status'], 'MANUAL')
        
        # Check ScanHistory
        self.assertTrue(ScanHistory.objects.filter(
            code='KLUEG8UHDB-C2D1',
            user='tech1',
            scan_status='MANUAL'
        ).exists())

import json
