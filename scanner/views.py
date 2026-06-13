import os
import re
import json
import datetime
import cv2
import numpy as np
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import transaction

from scanner.models import Technician, Chip, Price, NonCodePrice, ScanHistory, ApprovalRequest, Notification
from scanner.seeder import seed_database_if_empty
from scanner.ocr_pipeline import (
    load_image, preprocess_image, compute_phash, hamming_distance,
    get_ocr_engine, traverse_ocr_results, match_chip_heuristics
)

# Helper to verify technician password
def check_tech_password(stored, raw):
    from django.contrib.auth.hashers import check_password as django_check_password
    import hashlib
    if stored == raw:
        return True
    try:
        md5_raw = hashlib.md5(raw.encode('utf-8')).hexdigest()
        if stored == md5_raw:
            return True
    except Exception:
        pass
    try:
        if django_check_password(raw, stored):
            return True
    except Exception:
        pass
    return False

def get_current_user(request):
    username = request.session.get('tech_username')
    role = request.session.get('tech_role', 'tech')
    if not username:
        return None, None
    return username, role

def spa_shell(request):
    """
    Serves the SPA page. Also runs the database pre-seeder lazily.
    """
    seed_database_if_empty()
    return render(request, 'index.html')

@csrf_exempt
def api_login(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
        
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST
        
    provider = data.get('provider')
    
    if provider == 'google':
        # Age-gated Google Login
        birth_year = data.get('birth_year')
        if not birth_year:
            return JsonResponse({'error': 'Age verification required'}, status=400)
        try:
            birth_year = int(birth_year)
            current_year = datetime.datetime.now().year
            age = current_year - birth_year
            if age < 18:
                return JsonResponse({'error': 'You must be at least 18 years old to access this application.'}, status=403)
        except ValueError:
            return JsonResponse({'error': 'Invalid birth year format'}, status=400)
            
        # Authenticate as mock google user
        username = 'google_user'
        role = 'tech'
        
        # Ensure default google_user Technician exists
        tech, created = Technician.objects.get_or_create(
            username=username,
            defaults={'password': 'MOCK_GOOGLE_PASSWORD', 'role': 'tech'}
        )
        
        request.session['tech_username'] = username
        request.session['tech_role'] = role
        return JsonResponse({
            'success': True,
            'user': {
                'username': username,
                'role': role
            }
        })
        
    else:
        # Standard username/password login
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return JsonResponse({'error': 'Username and password required'}, status=400)
            
        try:
            tech = Technician.objects.get(username=username)
            if check_tech_password(tech.password, password):
                request.session['tech_username'] = tech.username
                request.session['tech_role'] = tech.role
                return JsonResponse({
                    'success': True,
                    'user': {
                        'username': tech.username,
                        'role': tech.role
                    }
                })
        except Technician.DoesNotExist:
            pass
            
        return JsonResponse({'error': 'Invalid username or password'}, status=401)

@csrf_exempt
def api_logout(request):
    request.session.flush()
    return JsonResponse({'success': True})

@csrf_exempt
def api_chips(request):
    username, role = get_current_user(request)
    if not username:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    if request.method == 'GET':
        chips = Chip.objects.all().order_by('-id')
        data = []
        for c in chips:
            # Get buy price for this chip based on user role
            try:
                price_obj = Price.objects.get(grade=c.grade, role=role)
                p_coded = price_obj.price_coded
                p_noncode = price_obj.price_noncode
            except Price.DoesNotExist:
                p_coded = 0
                p_noncode = 0
                
            data.append({
                'code': c.code,
                'grade': c.grade,
                'size': c.size,
                'type': c.type,
                'maker': c.maker,
                'note': c.note,
                'is_manual': c.is_manual,
                'status': c.status,
                'alias': c.alias,
                'alternate_codes': c.alternate_codes,
                'image_path': c.image_path,
                'price_coded': p_coded,
                'price_noncode': p_noncode
            })
        return JsonResponse({'chips': data})
        
    elif request.method == 'POST':
        if role != 'admin':
            return JsonResponse({'error': 'Admin permissions required'}, status=403)
            
        # Add new chip
        code = request.POST.get('code')
        grade = request.POST.get('grade')
        size = request.POST.get('size')
        chip_type = request.POST.get('type')
        maker = request.POST.get('maker')
        note = request.POST.get('note', '')
        alias = request.POST.get('alias', '')
        alternate_codes = request.POST.get('alternate_codes', '')
        status = request.POST.get('status', 'coded')
        
        if not code or not grade or not size or not chip_type or not maker:
            return JsonResponse({'error': 'Required fields missing'}, status=400)
            
        if Chip.objects.filter(code=code).exists():
            return JsonResponse({'error': 'Chip code already exists'}, status=400)
            
        reference_image = request.FILES.get('reference_image')
        image_path = ""
        image_hash = ""
        
        if reference_image:
            # Save reference image
            path = default_storage.save(f'chips/{reference_image.name}', ContentFile(reference_image.read()))
            image_path = default_storage.url(path)
            
            # Compute perceptual hash
            try:
                full_path = default_storage.path(path)
                cv_img = load_image(full_path)
                image_hash = compute_phash(cv_img)
            except Exception as e:
                image_hash = ""
                
        chip = Chip.objects.create(
            code=code,
            grade=grade,
            size=size,
            type=chip_type,
            maker=maker,
            note=note,
            alias=alias,
            alternate_codes=alternate_codes,
            status=status,
            is_manual=True,
            reference_image=reference_image,
            image_hash=image_hash,
            image_path=image_path
        )
        
        # Notify technicians of new inventory chip
        Notification.objects.create(
            user='all',
            message=f"New chip added: {chip.maker} {chip.code} ({chip.size})"
        )
        
        return JsonResponse({'success': True, 'chip': {'code': chip.code}})

@csrf_exempt
def api_delete_chip(request, code):
    username, role = get_current_user(request)
    if not username:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    if role != 'admin':
        return JsonResponse({'error': 'Admin permissions required'}, status=403)
        
    try:
        chip = Chip.objects.get(code=code)
        if not chip.is_manual:
            return JsonResponse({'error': 'Cannot delete pre-seeded system chips'}, status=400)
        chip.delete()
        return JsonResponse({'success': True})
    except Chip.DoesNotExist:
        return JsonResponse({'error': 'Chip not found'}, status=404)

def api_check_chip(request, code):
    username, role = get_current_user(request)
    if not username:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    try:
        c = Chip.objects.get(code=code)
        try:
            price_obj = Price.objects.get(grade=c.grade, role=role)
            p_coded = price_obj.price_coded
            p_noncode = price_obj.price_noncode
        except Price.DoesNotExist:
            p_coded = 0
            p_noncode = 0
            
        return JsonResponse({
            'success': True,
            'chip': {
                'code': c.code,
                'grade': c.grade,
                'size': c.size,
                'type': c.type,
                'maker': c.maker,
                'note': c.note,
                'status': c.status,
                'alias': c.alias,
                'alternate_codes': c.alternate_codes,
                'price_coded': p_coded,
                'price_noncode': p_noncode
            }
        })
    except Chip.DoesNotExist:
        return JsonResponse({'error': 'Chip not found'}, status=404)

@csrf_exempt
def api_prices(request):
    username, role = get_current_user(request)
    if not username:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    if request.method == 'GET':
        # Return all prices
        prices = Price.objects.all().order_by('role', 'grade')
        size_prices = NonCodePrice.objects.all().order_by('role', 'size')
        
        prices_list = [{
            'id': p.id,
            'grade': p.grade,
            'price_coded': p.price_coded,
            'price_noncode': p.price_noncode,
            'role': p.role
        } for p in prices]
        
        size_prices_list = [{
            'id': sp.id,
            'size': sp.size,
            'price': sp.price,
            'role': sp.role
        } for sp in size_prices]
        
        return JsonResponse({
            'prices': prices_list,
            'size_prices': size_prices_list
        })
        
    elif request.method == 'POST':
        if role != 'admin':
            return JsonResponse({'error': 'Admin permissions required'}, status=403)
            
        try:
            data = json.loads(request.body)
            with transaction.atomic():
                # Update Grades Prices
                for p in data.get('prices', []):
                    Price.objects.filter(grade=p['grade'], role=p['role']).update(
                        price_coded=int(p['price_coded']),
                        price_noncode=int(p['price_noncode'])
                    )
                # Update Size Prices
                for sp in data.get('size_prices', []):
                    NonCodePrice.objects.filter(size=sp['size'], role=sp['role']).update(
                        price=int(sp['price'])
                    )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

def api_scan_history(request):
    username, role = get_current_user(request)
    if not username:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    # Return scan logs (Admins see all, techs see their own)
    if role == 'admin':
        scans = ScanHistory.objects.all().order_by('-timestamp')[:50]
    else:
        scans = ScanHistory.objects.filter(user=username).order_by('-timestamp')[:50]
        
    data = []
    for s in scans:
        data.append({
            'id': s.id,
            'code': s.code,
            'grade': s.grade,
            'size': s.size,
            'type': s.type,
            'maker': s.maker,
            'price_coded': s.price_coded,
            'price_noncode': s.price_noncode,
            'timestamp': s.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'user': s.user,
            'status': s.status,
            'image_url': s.image.url if s.image else "",
            'scan_status': s.scan_status
        })
    return JsonResponse({'scans': data})

@csrf_exempt
def api_scan_image(request):
    username, role = get_current_user(request)
    if not username:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
        
    uploaded_image = request.FILES.get('image')
    if not uploaded_image:
        return JsonResponse({'error': 'No image file uploaded'}, status=400)
        
    # Save scanned image to media
    scan_file_path = default_storage.save(f'scans/{uploaded_image.name}', ContentFile(uploaded_image.read()))
    full_scan_path = default_storage.path(scan_file_path)
    image_url = default_storage.url(scan_file_path)
    
    # 1. Load image and compute perceptual hash
    try:
        cv_img = load_image(full_scan_path)
        scan_hash = compute_phash(cv_img)
    except Exception as e:
        return JsonResponse({'error': f'Failed to parse image: {str(e)}'}, status=400)
        
    matched_chip = None
    scan_status = 'UNKNOWN'
    ocr_text = ""
    match_score_val = 0.0
    
    # 2. Check perceptual hash matching first
    # Find chips that have image_hash populated
    candidate_hash_chips = Chip.objects.exclude(image_hash="")
    best_hash_chip = None
    min_distance = 999
    
    for c in candidate_hash_chips:
        dist = hamming_distance(scan_hash, c.image_hash)
        if dist < min_distance:
            min_distance = dist
            best_hash_chip = c
            
    if min_distance <= 10:
        # Close match visually, bypass OCR
        matched_chip = best_hash_chip
        scan_status = 'MATCHED'
        ocr_text = "[Perceptual Hash Match]"
        match_score_val = 1.0
        
    else:
        # 3. OCR Pipeline & Heuristics Matching
        try:
            # Run image pre-processing
            preprocessed_img = preprocess_image(cv_img)
            
            # Save preprocessed image to temporary file to read via OCR
            temp_pre_path = full_scan_path + "_pre.png"
            cv2.imwrite(temp_pre_path, preprocessed_img)
            
            # Run PaddleOCR
            ocr = get_ocr_engine()
            results = ocr.ocr(temp_pre_path)
            
            # Clean up temp file
            if os.path.exists(temp_pre_path):
                os.remove(temp_pre_path)
                
            # Parse OCR tokens
            tokens = traverse_ocr_results(results)
            ocr_text = " ".join([t[0] for t in tokens])
            
            # Apply heuristics database matcher
            matched_chip_candidate, match_score_val = match_chip_heuristics(tokens)
            
            if matched_chip_candidate and match_score_val >= 0.80:
                scan_status = 'MATCHED'
                matched_chip = matched_chip_candidate
            else:
                scan_status = 'UNKNOWN'
                matched_chip = None
                if matched_chip_candidate and match_score_val >= 0.40:
                    nearly_matched_chip = matched_chip_candidate
                    nearly_matched_score = match_score_val
                
        except Exception as e:
            # Fallback in case of errors in OCR (e.g. if libraries not fully configured)
            ocr_text = f"OCR Error: {str(e)}"
            matched_chip = None
            scan_status = 'UNKNOWN'
            
    # Compute buying prices based on the user's role
    if scan_status == 'MATCHED':
        code = matched_chip.code
        grade = matched_chip.grade
        size = matched_chip.size
        chip_type = matched_chip.type
        maker = matched_chip.maker
        status = matched_chip.status
        
        # Retrieve role-specific buying prices
        try:
            price_obj = Price.objects.get(grade=grade, role=role)
            price_coded = price_obj.price_coded
            price_noncode = price_obj.price_noncode
        except Price.DoesNotExist:
            price_coded = 0
            price_noncode = 0
    else:
        # Visual Match or OCR failed, mark as unrecognized
        # Attempt to scrape any model-looking string from OCR text as a guess
        code = "UNRECOGNIZED"
        # Search for words of size in OCR text (e.g. 64GB, 128G)
        size_match = re.search(r'\b(\d+)(GB|G)\b', ocr_text, re.IGNORECASE)
        size = size_match.group(0).upper() if size_match else "Unspecified"
        
        # Search for maker name
        maker = "Unspecified"
        for m in ['Samsung', 'Hynix', 'Toshiba', 'Kioxia', 'Micron', 'SanDisk']:
            if m.lower() in ocr_text.lower():
                maker = m
                break
                
        chip_type = "Unspecified"
        for t in ['UFS', 'eMMC', 'NAND']:
            if t.lower() in ocr_text.lower():
                chip_type = t
                break
                
        grade = "N/A"
        status = "noncode"
        
        # Set buying prices to size-based NonCodePrice if size is matched, else 0
        try:
            nc_price = NonCodePrice.objects.get(size=size, role=role)
            price_coded = nc_price.price
            price_noncode = nc_price.price
        except NonCodePrice.DoesNotExist:
            price_coded = 0
            price_noncode = 0
            
    # Save Scan to History
    history_entry = ScanHistory.objects.create(
        code=code,
        grade=grade,
        size=size,
        type=chip_type,
        maker=maker,
        price_coded=price_coded,
        price_noncode=price_noncode,
        user=username,
        status=status,
        image=scan_file_path,
        ocr_text=ocr_text,
        matched_chip=matched_chip,
        scan_status=scan_status
    )
    
    # Return match results
    response_data = {
        'success': True,
        'scan': {
            'id': history_entry.id,
            'code': code,
            'grade': grade,
            'size': size,
            'type': chip_type,
            'maker': maker,
            'status': status,
            'price_coded': price_coded,
            'price_noncode': price_noncode,
            'image_url': image_url,
            'ocr_text': ocr_text,
            'scan_status': scan_status,
            'match_score': round(match_score_val, 2)
        }
    }
    
    if scan_status == 'UNKNOWN' and 'nearly_matched_chip' in locals() and nearly_matched_chip:
        try:
            nm_price_obj = Price.objects.get(grade=nearly_matched_chip.grade, role=role)
            nm_price_coded = nm_price_obj.price_coded
            nm_price_noncode = nm_price_obj.price_noncode
        except Price.DoesNotExist:
            nm_price_coded = 0
            nm_price_noncode = 0
            
        response_data['scan']['nearly_matched'] = {
            'code': nearly_matched_chip.code,
            'maker': nearly_matched_chip.maker,
            'size': nearly_matched_chip.size,
            'type': nearly_matched_chip.type,
            'grade': nearly_matched_chip.grade,
            'price_coded': nm_price_coded,
            'price_noncode': nm_price_noncode,
            'score': round(nearly_matched_score, 2),
            'note': nearly_matched_chip.note
        }
        
    return JsonResponse(response_data)

@csrf_exempt
def api_submit_approval(request):
    username, role = get_current_user(request)
    if not username:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
        
    code = request.POST.get('code')
    size = request.POST.get('size', '')
    chip_type = request.POST.get('type', '')
    classification = request.POST.get('classification', 'coded')
    image_url = request.POST.get('image_url', '')
    
    if not code:
        return JsonResponse({'error': 'Code is required'}, status=400)
        
    # Create request
    req = ApprovalRequest.objects.create(
        code=code,
        technician=username,
        status='pending',
        image_path=image_url,
        size=size,
        type=chip_type,
        classification=classification
    )
    
    # Notify Admins
    Notification.objects.create(
        user='admin',
        message=f"New approval request submitted by {username} for code: {code}"
    )
    
    return JsonResponse({'success': True, 'id': req.id})

@csrf_exempt
def api_approvals(request):
    username, role = get_current_user(request)
    if not username:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    if request.method == 'GET':
        if role == 'admin':
            reqs = ApprovalRequest.objects.all().order_by('-created_at')
        else:
            reqs = ApprovalRequest.objects.filter(technician=username).order_by('-created_at')
            
        data = [{
            'id': r.id,
            'code': r.code,
            'technician': r.technician,
            'status': r.status,
            'created_at': r.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'image_path': r.image_path,
            'size': r.size,
            'type': r.type,
            'classification': r.classification
        } for r in reqs]
        
        return JsonResponse({'approvals': data})
        
    elif request.method == 'POST':
        if role != 'admin':
            return JsonResponse({'error': 'Admin permissions required'}, status=403)
            
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.POST
            
        req_id = data.get('id')
        action = data.get('action') # 'approved' or 'rejected'
        grade = data.get('grade', 'A1') # Grade assigned on approval
        maker = data.get('maker', 'Unspecified')
        
        if not req_id or not action:
            return JsonResponse({'error': 'Required fields missing'}, status=400)
            
        try:
            req = ApprovalRequest.objects.get(id=req_id)
            req.status = action
            req.save()
            
            if action == 'approved':
                # Create a new Chip in database
                chip, created = Chip.objects.get_or_create(
                    code=req.code,
                    defaults={
                        'grade': grade,
                        'size': req.size or 'Unspecified',
                        'type': req.type or 'Unspecified',
                        'maker': maker,
                        'status': req.classification or 'coded',
                        'is_manual': True,
                        'image_path': req.image_path
                    }
                )
                
                # If image exists in scans, we can copy its hash to the Chip model
                if req.image_path:
                    try:
                        # Extract the clean file path from the url (e.g. /media/scans/xyz.jpg -> scans/xyz.jpg)
                        media_prefix = '/media/'
                        if media_prefix in req.image_path:
                            rel_path = req.image_path.split(media_prefix)[1]
                            full_path = default_storage.path(rel_path)
                            cv_img = load_image(full_path)
                            chip.image_hash = compute_phash(cv_img)
                            chip.save()
                    except Exception:
                        pass
                
                # Notify the technician
                Notification.objects.create(
                    user=req.technician,
                    message=f"Your request for code {req.code} has been APPROVED as Grade {grade}."
                )
            else:
                Notification.objects.create(
                    user=req.technician,
                    message=f"Your request for code {req.code} has been REJECTED."
                )
                
            return JsonResponse({'success': True})
        except ApprovalRequest.DoesNotExist:
            return JsonResponse({'error': 'Request not found'}, status=404)

def api_notifications(request):
    username, role = get_current_user(request)
    if not username:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    # Fetch user's notification list
    from django.db.models import Q
    notifs = Notification.objects.filter(
        Q(user=username) | Q(user='all') | (Q(user='admin') if role == 'admin' else Q(pk=None))
    ).order_by('-created_at')[:10]
    
    data = [{
        'id': n.id,
        'message': n.message,
        'is_read': n.is_read,
        'created_at': n.created_at.strftime('%H:%M:%S')
    } for n in notifs]
    
    # Mark them as read
    Notification.objects.filter(id__in=[n.id for n in notifs]).update(is_read=True)
    
    return JsonResponse({'notifications': data})

def api_stats(request):
    username, role = get_current_user(request)
    if not username:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    if role != 'admin':
        return JsonResponse({'error': 'Admin permissions required'}, status=403)
        
    total_scans = ScanHistory.objects.count()
    matched_scans = ScanHistory.objects.filter(scan_status='MATCHED').count()
    accuracy = (matched_scans / total_scans * 100) if total_scans > 0 else 100.0
    
    pending_approvals = ApprovalRequest.objects.filter(status='pending').count()
    manual_chips = Chip.objects.filter(is_manual=True).count()
    total_inventory = Chip.objects.count()
    
    return JsonResponse({
        'success': True,
        'stats': {
            'total_scans': total_scans,
            'matched_scans': matched_scans,
            'accuracy': round(accuracy, 1),
            'pending_approvals': pending_approvals,
            'manual_chips': manual_chips,
            'total_inventory': total_inventory
        }
    })

@csrf_exempt
def api_scan_manual(request):
    username, role = get_current_user(request)
    if not username:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
        
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST
        
    code = data.get('code')
    if not code:
        return JsonResponse({'error': 'Chip code is required'}, status=400)
        
    try:
        c = Chip.objects.get(code=code)
        
        # Calculate pricing
        try:
            price_obj = Price.objects.get(grade=c.grade, role=role)
            p_coded = price_obj.price_coded
            p_noncode = price_obj.price_noncode
        except Price.DoesNotExist:
            p_coded = 0
            p_noncode = 0
            
        # Create ScanHistory with scan_status='MANUAL'
        history_entry = ScanHistory.objects.create(
            code=c.code,
            grade=c.grade,
            size=c.size,
            type=c.type,
            maker=c.maker,
            price_coded=p_coded,
            price_noncode=p_noncode,
            user=username,
            status=c.status,
            ocr_text="[Manual Entry Search]",
            matched_chip=c,
            scan_status='MANUAL'
        )
        
        return JsonResponse({
            'success': True,
            'scan': {
                'id': history_entry.id,
                'code': c.code,
                'grade': c.grade,
                'size': c.size,
                'type': c.type,
                'maker': c.maker,
                'status': c.status,
                'price_coded': p_coded,
                'price_noncode': p_noncode,
                'image_url': '',
                'ocr_text': '[Manual Entry Search]',
                'scan_status': 'MANUAL',
                'match_score': 1.0
            }
        })
    except Chip.DoesNotExist:
        return JsonResponse({'error': 'Chip not found'}, status=404)

def camera_stream(request):
    """
    Mock web camera stream endpoint. Serves an MJPEG video stream.
    """
    def generate_frames():
        # Load a default text overlay frame in case camera is not present
        cap = None
        try:
            cap = cv2.VideoCapture(0)
        except Exception:
            pass
            
        frame_idx = 0
        while True:
            # Try to grab a frame from webcam
            ret = False
            if cap and cap.isOpened():
                ret, frame = cap.read()
                
            if not ret:
                # Fallback: Generate a nice moving simulation background frame
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                # Draw grid moire patterns
                for x in range(0, 640, 40):
                    cv2.line(frame, (x, 0), (x, 480), (20, 20, 20), 1)
                for y in range(0, 480, 40):
                    cv2.line(frame, (0, y), (640, y), (20, 20, 20), 1)
                    
                # Moving scan indicator bar
                scan_y = (frame_idx * 5) % 480
                cv2.line(frame, (0, scan_y), (640, scan_y), (0, 255, 0), 2)
                
                cv2.putText(frame, "CHIP SCANNER LIVE SIMULATOR", (100, 200),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "Scan Box [Align Chip Here]", (170, 240),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                
                # Draw mock chip rect
                cv2.rectangle(frame, (220, 140), (420, 340), (0, 255, 0), 2)
                cv2.putText(frame, "SAMSUNG", (270, 220),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)
                cv2.putText(frame, "KLUEG8UHDB", (255, 250),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)
                cv2.putText(frame, "C2D1", (295, 280),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)
            else:
                # Add overlays to actual camera feed
                cv2.rectangle(frame, (220, 140), (420, 340), (0, 255, 0), 2)
                cv2.putText(frame, "Align Chip Inside Box", (210, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                            
            # Encode frame to JPEG
            ret_enc, jpeg = cv2.imencode('.jpg', frame)
            if not ret_enc:
                continue
                
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            frame_idx += 1
            # Control frame rate
            import time
            time.sleep(0.04) # ~25 FPS
            
    return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')
