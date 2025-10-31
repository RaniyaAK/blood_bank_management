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
    
    # 🩸 New field to store eligibility
    is_eligible = models.BooleanField(default=False)

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


class DonorRequestAppointment(models.Model):
    donor = models.ForeignKey(User, on_delete=models.CASCADE)
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    hospital = models.CharField(max_length=150)
    additional_notes = models.TextField(blank=True, null=True)
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
    age = models.PositiveIntegerField(help_text="Age must be between 18 and 60 years.")
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


