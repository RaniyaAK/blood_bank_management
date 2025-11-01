from django import forms
from django.contrib.auth.models import User
from .models import Profile, BloodStock, DonorDetails, RecipientDetails, HospitalDetails
from .models import DonorRequestAppointment
from .models import DonorEligibilityTestForm

class UserForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password']
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
        fields = ['bloodgroup', 'unit']
        widgets = {
            'bloodgroup': forms.Select(attrs={'class': 'form-control'}),
            'unit': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class DonorDetailsForm(forms.ModelForm):
    class Meta:
        model = DonorDetails
        fields = ['name', 'address','email' ,'phonenumber', 'age', 'bloodgroup', 'photo']
        widgets = {
            'age': forms.NumberInput(attrs={'min': 18, 'max': 65, 'placeholder': 'Enter your age'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email address'}),

        }
        labels = {
            'phonenumber': 'Phone Number'
        }
        


class RecipientDetailsForm(forms.ModelForm):
    class Meta:
        model = RecipientDetails
        fields = ['name', 'gender', 'address', 'phonenumber', 'dob', 'bloodgroup', 'weight', 'photo']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'weight': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Weight in kg'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'weight': 'Weight (kg)',
            'phonenumber': 'Phone Number'
        }


class HospitalDetailsForm(forms.ModelForm):
    class Meta:
        model = HospitalDetails
        fields = ['name', 'code', 'location', 'phonenumber', 'since', 'photo']
        labels = {
            'code': 'Hospital Code',
            'phonenumber': 'Contact Number'
        }
        widgets = {
            'since': forms.DateInput(attrs={'type': 'date'}),
            'location': forms.Textarea(attrs={'rows': 3}),
        }



class DonorRequestAppointmentForm(forms.ModelForm):
    class Meta:
        model = DonorRequestAppointment
        fields = ['preferred_date', 'preferred_time']
        widgets = {
            'preferred_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'preferred_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }
class DonorEligibilityForm(forms.ModelForm):
    class Meta:
        model = DonorEligibilityTestForm
        fields = [
            'gender',
            'dob',
            'weight',
            'hemoglobin_level',
            'last_donation_date',
            'has_disease',
            'on_medication',
            'had_surgery_recently',
        ]
        widgets = {
            'dob': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'  # ✅ tell Django the format
            ),
            'last_donation_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'weight': forms.NumberInput(attrs={'min': 40, 'max': 150, 'class': 'form-control', 'placeholder': 'Weight in kg'}),
            'hemoglobin_level': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control', 'placeholder': 'Hemoglobin in g/dL'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(DonorEligibilityForm, self).__init__(*args, **kwargs)
        # ✅ accept browser-submitted date format
        self.fields['dob'].input_formats = ['%Y-%m-%d']
        self.fields['last_donation_date'].input_formats = ['%Y-%m-%d']
