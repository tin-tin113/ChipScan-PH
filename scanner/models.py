from django.db import models

class Technician(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('tech', 'Tech'),
    )
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='tech')

    def __str__(self):
        return f"{self.username} ({self.role})"

class Chip(models.Model):
    STATUS_CHOICES = (
        ('coded', 'Coded'),
        ('noncode', 'Non-Code'),
    )
    code = models.CharField(max_length=50, unique=True, db_index=True)
    grade = models.CharField(max_length=5)
    size = models.CharField(max_length=20)
    type = models.CharField(max_length=50)
    maker = models.CharField(max_length=50)
    note = models.TextField(default='', blank=True)
    is_manual = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='coded')
    alias = models.CharField(max_length=100, blank=True)
    alternate_codes = models.CharField(max_length=200, blank=True)
    ocr_text = models.TextField(default='', blank=True)
    reference_image = models.ImageField(upload_to='chips/', null=True, blank=True)
    image_hash = models.CharField(max_length=64, blank=True)
    image_path = models.CharField(max_length=255, blank=True, db_index=True)

    def __str__(self):
        return self.code

class Price(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('tech', 'Tech'),
    )
    grade = models.CharField(max_length=5)
    price_coded = models.IntegerField(default=0)
    price_noncode = models.IntegerField(default=0)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='tech')

    class Meta:
        unique_together = ('grade', 'role')

    def __str__(self):
        return f"{self.grade} - {self.role} (Coded: {self.price_coded}, NonCode: {self.price_noncode})"

class NonCodePrice(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('tech', 'Tech'),
    )
    size = models.CharField(max_length=20)
    price = models.IntegerField(default=0)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='tech')

    class Meta:
        unique_together = ('size', 'role')

    def __str__(self):
        return f"{self.size} - {self.role} (Price: {self.price})"

class ScanHistory(models.Model):
    code = models.CharField(max_length=50, db_index=True)
    grade = models.CharField(max_length=5)
    size = models.CharField(max_length=20)
    type = models.CharField(max_length=50)
    maker = models.CharField(max_length=50)
    price_coded = models.IntegerField()
    price_noncode = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=50)
    status = models.CharField(max_length=15, default='coded')
    image = models.ImageField(upload_to='scans/', null=True, blank=True)
    ocr_text = models.TextField(default='', blank=True)
    matched_chip = models.ForeignKey(Chip, on_delete=models.SET_NULL, null=True, blank=True)
    scan_status = models.CharField(max_length=20, default='UNKNOWN')

    def __str__(self):
        return f"{self.code} scanned by {self.user} at {self.timestamp}"

class ApprovalRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    code = models.CharField(max_length=50)
    technician = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    image_path = models.CharField(max_length=255, blank=True)
    size = models.CharField(max_length=20, blank=True)
    type = models.CharField(max_length=50, blank=True)
    classification = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"Request: {self.code} ({self.status})"

class Notification(models.Model):
    user = models.CharField(max_length=50)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user}: {self.message[:20]}"
