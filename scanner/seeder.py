from django.contrib.auth.hashers import make_password
from scanner.models import Technician, Chip, Price, NonCodePrice

def seed_database_if_empty():
    # 1. Check if seeded already
    if Technician.objects.exists():
        return False
        
    # 2. Seed Default Accounts
    # Passwords hashed using Django's MD5 hasher (fits in 50 chars: e.g. "md5$salt$hash")
    Technician.objects.create(
        username='admin',
        password=make_password('admin123', hasher='md5'),
        role='admin'
    )
    Technician.objects.create(
        username='tech1',
        password=make_password('tech123', hasher='md5'),
        role='tech'
    )
    
    # 3. Seed Base Price Matrix for A1 - A5 grades
    # Price model: grade, price_coded, price_noncode, role
    price_data = [
        # Grade, price_coded, price_noncode, role
        ('A1', 120, 95, 'admin'),
        ('A2', 180, 140, 'admin'),
        ('A3', 240, 190, 'admin'),
        ('A4', 350, 280, 'admin'),
        ('A5', 600, 480, 'admin'),
        
        ('A1', 100, 80, 'tech'),
        ('A2', 150, 120, 'tech'),
        ('A3', 200, 160, 'tech'),
        ('A4', 300, 240, 'tech'),
        ('A5', 500, 400, 'tech'),
    ]
    for grade, p_coded, p_noncode, role in price_data:
        Price.objects.get_or_create(
            grade=grade,
            role=role,
            defaults={'price_coded': p_coded, 'price_noncode': p_noncode}
        )
        
    # 4. Seed Size-based Non-Code Prices
    # NonCodePrice model: size, price, role
    noncode_data = [
        ('16GB', 15, 'admin'),
        ('32GB', 30, 'admin'),
        ('64GB', 60, 'admin'),
        ('128GB', 120, 'admin'),
        ('256GB', 240, 'admin'),
        ('512GB', 480, 'admin'),
        ('1TB', 960, 'admin'),
        
        ('16GB', 10, 'tech'),
        ('32GB', 25, 'tech'),
        ('64GB', 50, 'tech'),
        ('128GB', 100, 'tech'),
        ('256GB', 200, 'tech'),
        ('512GB', 400, 'tech'),
        ('1TB', 800, 'tech'),
    ]
    for size, price, role in noncode_data:
        NonCodePrice.objects.get_or_create(
            size=size,
            role=role,
            defaults={'price': price}
        )
        
    # 5. Seed 28 Standard Storage Chips
    # Chip model: code, grade, size, type, maker, note, is_manual, status, alias, alternate_codes, ocr_text, image_hash, image_path
    chips_data = [
        {
            'code': 'KLUEG8UHDB-C2D1',
            'grade': 'A1',
            'size': '256GB',
            'type': 'UFS 2.1',
            'maker': 'Samsung',
            'note': 'Standard premium storage chip used in Galaxy S9/S9+',
            'alias': 'KLU256',
            'alternate_codes': 'KLUEG8U1EA-B0C1'
        },
        {
            'code': 'KLUDG4U1EA-B0C1',
            'grade': 'A2',
            'size': '128GB',
            'type': 'UFS 2.1',
            'maker': 'Samsung',
            'note': 'Common Samsung UFS storage found in mid-to-high tier phones',
            'alias': 'KLU128',
            'alternate_codes': 'KLUDG4U1UM-B0E1'
        },
        {
            'code': 'KLUCG4J1ZD-B0CP',
            'grade': 'A2',
            'size': '64GB',
            'type': 'UFS 2.1',
            'maker': 'Samsung',
            'note': 'Highly reliable legacy UFS storage chip',
            'alias': 'KLU64',
            'alternate_codes': 'KLUCG4J1ZD'
        },
        {
            'code': 'KM2V7001JM-B517',
            'grade': 'A3',
            'size': '128GB',
            'type': 'eMMC',
            'maker': 'Samsung',
            'note': 'Budget storage chip with integrated controller',
            'alias': 'KM128',
            'alternate_codes': 'KM2V7001JM'
        },
        {
            'code': 'H9HQ15AECMBDAR-KEM',
            'grade': 'A1',
            'size': '128GB',
            'type': 'UFS 2.1',
            'maker': 'SK Hynix',
            'note': 'High-performance SK Hynix storage chip',
            'alias': 'HYNIX128',
            'alternate_codes': 'H9HQ15AEC'
        },
        {
            'code': 'H9HP52ACPMMDAR-KMM',
            'grade': 'A3',
            'size': '64GB',
            'type': 'eMMC',
            'maker': 'SK Hynix',
            'note': 'Standard eMMC chip for budget Android devices',
            'alias': 'HYNIX64',
            'alternate_codes': 'H9HP52ACP'
        },
        {
            'code': 'H28S70302BMR',
            'grade': 'A2',
            'size': '128GB',
            'type': 'UFS 2.1',
            'maker': 'SK Hynix',
            'note': 'Highly resilient SK Hynix storage solution',
            'alias': 'H28S128',
            'alternate_codes': 'H28S70302'
        },
        {
            'code': 'THGAF8G9T43BAIR',
            'grade': 'A2',
            'size': '64GB',
            'type': 'UFS 2.1',
            'maker': 'Toshiba',
            'note': 'High-speed Toshiba NAND flash storage',
            'alias': 'TOSH64',
            'alternate_codes': 'THGAF8G9T'
        },
        {
            'code': 'THGAF8T0T43BAIR',
            'grade': 'A1',
            'size': '128GB',
            'type': 'UFS 2.1',
            'maker': 'Toshiba',
            'note': 'Reliable premium Toshiba chip',
            'alias': 'TOSH128',
            'alternate_codes': 'THGAF8T0T'
        },
        {
            'code': 'THGAF9G9L4ADAG',
            'grade': 'A1',
            'size': '64GB',
            'type': 'UFS 3.0',
            'maker': 'Toshiba',
            'note': 'Next-gen Toshiba UFS 3.0 chip',
            'alias': 'TOSH3_64',
            'alternate_codes': 'THGAF9G9L'
        },
        {
            'code': 'MTFC64GAKAEEY-4M',
            'grade': 'A4',
            'size': '64GB',
            'type': 'eMMC',
            'maker': 'Micron',
            'note': 'Standard Micron eMMC module',
            'alias': 'MIC64',
            'alternate_codes': 'MTFC64GAK'
        },
        {
            'code': 'MTFC128GAJAECE-5M',
            'grade': 'A3',
            'size': '128GB',
            'type': 'eMMC',
            'maker': 'Micron',
            'note': 'Standard Micron 128GB storage package',
            'alias': 'MIC128',
            'alternate_codes': 'MTFC128GAJ'
        },
        {
            'code': 'MTFDDAK256TBN',
            'grade': 'A2',
            'size': '256GB',
            'type': 'UFS 2.1',
            'maker': 'Micron',
            'note': 'High-capacity Micron UFS storage package',
            'alias': 'MIC256',
            'alternate_codes': 'MTFDDAK256'
        },
        {
            'code': 'SDINBDA4-256G',
            'grade': 'A2',
            'size': '256GB',
            'type': 'UFS 2.1',
            'maker': 'SanDisk',
            'note': 'SanDisk iNAND premium storage series',
            'alias': 'SAND256',
            'alternate_codes': 'SDINBDA4'
        },
        {
            'code': 'SDINADF4-128G',
            'grade': 'A3',
            'size': '128GB',
            'type': 'eMMC',
            'maker': 'SanDisk',
            'note': 'SanDisk eMMC flash module for entry-level devices',
            'alias': 'SAND128',
            'alternate_codes': 'SDINADF4'
        },
        {
            'code': 'KLUDG4U1UM-B0E1',
            'grade': 'A1',
            'size': '128GB',
            'type': 'UFS 3.0',
            'maker': 'Samsung',
            'note': 'High-performance UFS 3.0 module for flagships',
            'alias': 'KLU3_128',
            'alternate_codes': 'KLUDG4U1UM'
        },
        {
            'code': 'KLUEG8U1UM-B0E1',
            'grade': 'A1',
            'size': '256GB',
            'type': 'UFS 3.0',
            'maker': 'Samsung',
            'note': 'Premium UFS 3.0 storage package',
            'alias': 'KLU3_256',
            'alternate_codes': 'KLUEG8U1UM'
        },
        {
            'code': 'HN8T15AEEX6',
            'grade': 'A1',
            'size': '256GB',
            'type': 'UFS 3.1',
            'maker': 'SK Hynix',
            'note': 'Ultra-fast UFS 3.1 SK Hynix storage module',
            'alias': 'HYNIX31_256',
            'alternate_codes': 'HN8T15AEE'
        },
        {
            'code': 'HN8T25AEEKX0',
            'grade': 'A1',
            'size': '512GB',
            'type': 'UFS 3.1',
            'maker': 'SK Hynix',
            'note': 'Massive UFS 3.1 SK Hynix storage package',
            'alias': 'HYNIX31_512',
            'alternate_codes': 'HN8T25AEE'
        },
        {
            'code': 'MTFC256GASAONS-A1',
            'grade': 'A4',
            'size': '256GB',
            'type': 'eMMC',
            'maker': 'Micron',
            'note': 'High-density Micron eMMC chip',
            'alias': 'MIC_EMMC_256',
            'alternate_codes': 'MTFC256GAS'
        },
        {
            'code': 'KLUFG8R1EM-B0C1',
            'grade': 'A3',
            'size': '256GB',
            'type': 'UFS 2.0',
            'maker': 'Samsung',
            'note': 'Legacy UFS 2.0 storage solution',
            'alias': 'KLU2_256',
            'alternate_codes': 'KLUFG8R1EM'
        },
        {
            'code': 'THGBMHG8C4LBAIR',
            'grade': 'A5',
            'size': '32GB',
            'type': 'eMMC',
            'maker': 'Toshiba',
            'note': 'Standard 32GB Toshiba eMMC chip',
            'alias': 'TOSH32',
            'alternate_codes': 'THGBMHG8C'
        },
        {
            'code': 'THGBMHG9C8LBAIG',
            'grade': 'A4',
            'size': '64GB',
            'type': 'eMMC',
            'maker': 'Toshiba',
            'note': 'Standard 64GB Toshiba eMMC flash storage',
            'alias': 'TOSH_EMMC_64',
            'alternate_codes': 'THGBMHG9C'
        },
        {
            'code': 'H9TQ17ABJTMCUR-KUM',
            'grade': 'A5',
            'size': '32GB',
            'type': 'eMMC',
            'maker': 'SK Hynix',
            'note': 'Legacy SK Hynix eMMC flash module',
            'alias': 'HYNIX32',
            'alternate_codes': 'H9TQ17ABJ'
        },
        {
            'code': 'KMRH60014A-B614',
            'grade': 'A4',
            'size': '64GB',
            'type': 'eMMC',
            'maker': 'Samsung',
            'note': 'Samsung eMMC embedded flash memory package',
            'alias': 'KMR64',
            'alternate_codes': 'KMRH60014A'
        },
        {
            'code': 'TY890A111229KC',
            'grade': 'A5',
            'size': '32GB',
            'type': 'eMMC',
            'maker': 'Toshiba',
            'note': 'Common legacy Toshiba module',
            'alias': 'TY32',
            'alternate_codes': 'TY890A111'
        },
        {
            'code': 'MTFC32GAKAECN-3M',
            'grade': 'A5',
            'size': '32GB',
            'type': 'eMMC',
            'maker': 'Micron',
            'note': 'Standard entry-level Micron eMMC flash',
            'alias': 'MIC32',
            'alternate_codes': 'MTFC32GAK'
        },
        {
            'code': 'SDINBDG4-64G',
            'grade': 'A4',
            'size': '64GB',
            'type': 'eMMC',
            'maker': 'SanDisk',
            'note': 'SanDisk iNAND standard eMMC series',
            'alias': 'SAND64',
            'alternate_codes': 'SDINBDG4'
        }
    ]
    
    for c in chips_data:
        Chip.objects.create(
            code=c['code'],
            grade=c['grade'],
            size=c['size'],
            type=c['type'],
            maker=c['maker'],
            note=c['note'],
            alias=c.get('alias', ''),
            alternate_codes=c.get('alternate_codes', ''),
            is_manual=False,
            status='coded'
        )
        
    return True
