from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User

# Phone validators
hospital_phone_validator = RegexValidator(
    regex=r'^(\+\d{1,3})?(\d{7}|\d{10})$',
    message="Enter a valid phone number"
)

donor_recipient_phone_validator = RegexValidator(
    regex=r'^(\+\d{1,3})?\d{10}$',
    message="Enter a valid phone number."
)

# ----------------------------

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('hospital', 'Hospital'),
        ('donor', 'Donor'),
        ('recipient', 'Recipient'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='recipient')

    def __str__(self):
        return f"{self.user} ({self.role})"


class BloodStock(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    bloodgroup = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    unit = models.PositiveIntegerField()
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bloodgroup} - {self.unit} units"


class HospitalDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)
    since = models.DateField()
    phonenumber = models.CharField(max_length=15, validators=[hospital_phone_validator])
    location = models.TextField()
    photo = models.ImageField(upload_to='hospital_photos/')

    def __str__(self):
        return self.name


class DonorDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    dob = models.DateField()
    phonenumber = models.CharField(max_length=15, validators=[donor_recipient_phone_validator])
    address = models.TextField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    bloodgroup = models.CharField(max_length=5)
    photo = models.ImageField(upload_to='donor_photos/')

    def __str__(self):
        return self.name


class RecipientDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    dob = models.DateField()
    phonenumber = models.CharField(max_length=15, validators=[donor_recipient_phone_validator])
    address = models.TextField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    bloodgroup = models.CharField(max_length=5)
    photo = models.ImageField(upload_to='recipient_photos/')

    def __str__(self):
        return self.name
