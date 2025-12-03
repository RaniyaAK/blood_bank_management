from django import forms
from datetime import date
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Profile, BloodStock, DonorDetails, RecipientDetails, HospitalDetails
from .models import DonorRequestAppointment, DonorEligibilityTest
from .models import RecipientBloodRequest
from .models import HospitalBloodRequest,HospitalBloodStock

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        help_texts = {'username': None}

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
        fields = ['blood_group', 'units']
        widgets = {
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'units': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

class DonorDetailsForm(forms.ModelForm):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    blood_group = forms.ChoiceField(
        choices=BLOOD_GROUP_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = DonorDetails
        fields = ['name', 'address', 'email', 'phone_number', 'age', 'blood_group', 'photo']

        widgets = {
            'age': forms.NumberInput(attrs={'min': 18, 'max': 65, 'placeholder': 'Enter your age'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email address'}),
        }

        labels = {
            'phone_number': 'Contact Number'
        }


class RecipientDetailsForm(forms.ModelForm):

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    blood_group = forms.ChoiceField(
    choices=BLOOD_GROUP_CHOICES,
    widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = RecipientDetails
        fields = ['name', 'address','email', 'phone_number', 'gender', 'dob', 'blood_group', 'photo']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email address'}),
        }

        labels = {
            'phone_number': 'Contact Number'
        }


class HospitalDetailsForm(forms.ModelForm):
    class Meta:
        model = HospitalDetails
        fields = ['name', 'code','email', 'location', 'phone_number', 'since']

        widgets = {
            'since': forms.DateInput(attrs={'type': 'date'}),
            'location': forms.Textarea(attrs={'rows': 3}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email address'}),
        }

        labels = {
            'name':'Hospital Name',
            'code': 'Hospital Code',
            'phone_number': 'Contact Number'
        }


class DonorRequestAppointmentForm(forms.ModelForm):
    class Meta:
        model = DonorRequestAppointment
        fields = ['preferred_date', 'preferred_time']
        widgets = {
            'preferred_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'preferred_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'preferred_date' in self.fields:
            self.fields['preferred_date'].widget.attrs['min'] = date.today().isoformat()

    def clean_preferred_date(self):
        preferred_date = self.cleaned_data.get('preferred_date')
        if preferred_date and preferred_date < date.today():
            raise ValidationError("You cannot select a past date.")
        return preferred_date


class DonorEligibilityTestForm(forms.ModelForm):
    class Meta:
        model = DonorEligibilityTest
        fields = [
            'gender',
            'dob',
            'weight',
            'last_donation_date',
            'has_disease',
            'on_medication',
            'had_surgery_recently',
        ]
        widgets = {
            'dob': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'last_donation_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'weight': forms.NumberInput(attrs={'min': 40, 'max': 150, 'class': 'form-control', 'placeholder': 'Weight in kg'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(DonorEligibilityTestForm, self).__init__(*args, **kwargs)
        self.fields['dob'].input_formats = ['%Y-%m-%d']
        self.fields['last_donation_date'].input_formats = ['%Y-%m-%d']

        labels = {
            'blood_group': 'Blood Group',
            'units': 'Number of Units',
            'required_date': 'Required Date',
            'urgency': 'Urgency Level',
            'reason': 'Reason for Request',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'required_date' in self.fields:
            self.fields['required_date'].widget.attrs['min'] = date.today().isoformat()

    def clean_required_date(self):
        required_date = self.cleaned_data.get('required_date')
        if required_date and required_date < date.today():
            raise ValidationError("You cannot select a past date.")
        return required_date


class HospitalAddBloodStockForm(forms.ModelForm):
    class Meta:
        model = HospitalBloodStock
        fields = ['blood_group', 'units']
        widgets = {
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'units': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

class HospitalBloodRequestForm(forms.ModelForm):
    class Meta:
        model = HospitalBloodRequest
        fields = ['blood_group', 'units', 'required_date', 'urgency']  
        widgets = {
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'units': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Enter number of units needed',
            }),
            'required_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().strftime('%Y-%m-%d'),
            }),
            'urgency': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_units(self):
        units = self.cleaned_data.get('units')
        if units is None or units <= 0:
            raise ValidationError("Units must be greater than zero.")
        return units        

    def clean_required_date(self):
        required_date = self.cleaned_data.get('required_date')
        if required_date and required_date < date.today():
            raise ValidationError("Required date cannot be in the past.")
        return required_date



class RecipientBloodRequestForm(forms.ModelForm):
    class Meta:
        model = RecipientBloodRequest
        fields = ['blood_group', 'units', 'required_date', 'urgency']
        widgets = {
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'units': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Enter number of units needed',
            }),
            'required_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().strftime('%Y-%m-%d'), 
            }),
            'urgency': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_units(self):
        units = self.cleaned_data.get('units')
        if units is None or units <= 0:
            raise ValidationError("Units must be greater than zero.")
        return units

    
    def clean_required_date(self):
        required_date = self.cleaned_data.get('required_date')
        if required_date and required_date < date.today():
            raise ValidationError("Required date cannot be in the past.")
        return required_date
