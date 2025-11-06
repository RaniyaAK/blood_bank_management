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


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = (
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
    email = models.EmailField(unique=True, null=True, blank=True)   
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
    email = models.EmailField(unique=True, null=True, blank=True)   
    phonenumber = models.CharField(max_length=15, validators=[donor_recipient_phone_validator])
    address = models.TextField()
    age = models.PositiveIntegerField(null=True, blank=True) 
    bloodgroup = models.CharField(max_length=5)
    photo = models.ImageField(upload_to='donor_photos/')
    
    is_eligible = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class RecipientDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    phonenumber = models.CharField(max_length=15, validators=[donor_recipient_phone_validator])
    email = models.EmailField(unique=True, null=True, blank=True)   
    address = models.TextField()
    gender = models.CharField(max_length=10)
    dob = models.DateField()
    bloodgroup = models.CharField(max_length=5)
    photo = models.ImageField(upload_to='recipient_photos/')

    def __str__(self):
        return self.name


class DonorRequestAppointment(models.Model):
    donor = models.ForeignKey(User, on_delete=models.CASCADE)
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.username} - {self.preferred_date} {self.preferred_time}"
    

class DonorEligibilityTestForm(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='eligibility_tests'
    )

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    dob = models.DateField(verbose_name="Date of Birth")
    weight = models.FloatField(help_text="Weight must be at least 50 kg.")
    hemoglobin_level = models.FloatField(help_text="Hemoglobin level in g/dL.")
    last_donation_date = models.DateField(null=True, blank=True, help_text="Leave blank if this is your first donation.")

    # Basic health questions
    has_disease = models.BooleanField(default=False, help_text="Do you currently have any infectious or chronic disease?")
    on_medication = models.BooleanField(default=False, help_text="Are you currently on any medication?")
    had_surgery_recently = models.BooleanField(default=False, help_text="Have you undergone any surgery recently?")

    passed = models.BooleanField(default=False)
    test_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_display = self.user.username if self.user else "Anonymous"
        status = "Passed ✅" if self.passed else "Failed ❌"
        return f"{user_display} - {status}"

    class Meta:
        verbose_name = "Donor Eligibility Test"
        verbose_name_plural = "Donor Eligibility Tests"
        ordering = ['-test_date']


class HospitalBloodRequest(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    URGENCY_LEVEL_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]
    
    hospital = models.ForeignKey(User, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    units = models.PositiveIntegerField()
    required_date = models.DateField()
    urgency = models.CharField(max_length=10, choices=URGENCY_LEVEL_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.hospital.username} - {self.blood_group} ({self.units} units)"
    

class AdminNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # ✅ added
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Admin Notification for {self.user.username if self.user else 'admin'} - {self.message[:50]}"
