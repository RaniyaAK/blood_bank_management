
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = (
        ('hospital', 'Hospital'),
        ('donor', 'Donor'),
        ('recipient', 'Recipient'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES,default='recipient')
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
