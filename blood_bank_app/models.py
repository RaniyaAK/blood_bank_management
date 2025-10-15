
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('hospital', 'Hospital'),
        ('donor', 'Donor'),
        ('recipient', 'Recipient'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES,default='recipient')
    def __str__(self):
        return f"{self.user} ({self.role})"
