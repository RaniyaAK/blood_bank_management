from django import forms
from django.contrib.auth.models import User
from .models import Profile
from .models import BloodStock


class UserForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput)
    last_name = forms.CharField(widget=forms.TextInput)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)
    class Meta:
        model = User
        fields = ['first_name','last_name','username', 'email', 'password']
        help_texts = {
            'username': None, 
        }
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
    
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class BloodStockForm(forms.ModelForm):
    class Meta:
        model = BloodStock
        fields = ['bloodgroup', 'unit']
        widgets = {
            'bloodgroup': forms.Select(attrs={'class': 'form-control'}),
            'unit': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }