from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout,login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, UserForm
from .models import Profile
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import BloodStockForm
from .models import BloodStock
from datetime import datetime
from .models import DonorDetails, RecipientDetails, Profile, BloodStock,HospitalDetails,DonorEligibilityTestForm
from .forms import RecipientDetailsForm
from .forms import DonorDetailsForm
from .forms import HospitalDetailsForm
from django.contrib.auth.models import User
from django.db.models import Sum
from .forms import DonorRequestAppointmentForm
import datetime
from .forms import DonorEligibilityForm
from .models import DonorDetails
from datetime import date


def home(request):
    return render(request, 'home.html')


# register

def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            user.first_name = form.cleaned_data['name']
            user.save()

            role = form.cleaned_data['role']
            profile = Profile.objects.create(user=user, role=role)

            # ✅ Automatically log in the user
            auth_login(request, user)

            # ✅ Redirect based on role
            if role == 'donor':
                return redirect('donor')
            elif role == 'recipient':
                return redirect('recipient')
            elif role == 'hospital':
                return redirect('hospital')
            else:
                return redirect('home')  # fallback
    else:
        form = UserForm()
    return render(request, 'register.html', {'form': form})


# login

def user_login(request):
    error_message = None
    form = LoginForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
           
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
    

            if user is not None:
                login(request, user)

                # Ensure Profile exists
                profile, created = Profile.objects.get_or_create(
                    user=user,
                    defaults={'role': 'admin' if user.is_superuser else 'recipient'}
                )
                role = profile.role

                if user.is_superuser:
                    return redirect('admin_dashboard')
                elif user.profile.role == 'hospital':
                    return redirect('hospital_details_form')
                elif user.profile.role == 'donor':
                    return redirect('donor_details_form')
                elif user.profile.role == 'recipient':
                    return redirect('recipient_details_form')
                else:
                    return redirect('home')
            else:
                error_message = "Incorrect username or password."
        else:
            error_message = "Please enter valid credentials."

    return render(request, 'login.html', {'form': form, 'error_message': error_message})

def roles(request):
    return render(request, 'roles.html')


# passwords

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Redirect to reset password page with email as parameter
            return redirect('reset_password', email=user.email)
        except User.DoesNotExist:
            messages.error(request, 'No account found with that email address.')
    return render(request, 'forgot_password.html')


def reset_password(request, email):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        else:
            try:
                user = User.objects.get(email=email)
                user.set_password(password)
                user.save()

                # ✅ Log in immediately
                user = authenticate(username=user.username, password=password)
                if user:
                    auth_login(request, user)

                    # ✅ Ensure profile exists and redirect by role
                    profile, _ = Profile.objects.get_or_create(user=user, defaults={'role': 'recipient'})
                    if profile.role == 'donor':
                        return redirect('donor')
                    elif profile.role == 'recipient':
                        return redirect('recipient')
                    elif profile.role == 'hospital':
                        return redirect('hospital')
                    else:
                        return redirect('home')

                messages.success(request, 'Password reset successful! You have been logged in.')

            except User.DoesNotExist:
                messages.error(request, 'Invalid user.')

    return render(request, 'reset_password.html', {'email': email})


# logout

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

#   __________________________________________________________________________________________________________________________

# pages

@login_required
def hospital(request):
    """Hospital dashboard"""
    try:
        hospital_profile = HospitalDetails.objects.get(user=request.user)
    except HospitalDetails.DoesNotExist:
        hospital_profile = None

    return render(request, 'hospital.html', {'hospital': hospital_profile})


@login_required
def recipient(request):
    """Recipient dashboard"""
    try:
        recipient_profile = RecipientDetails.objects.get(user=request.user)
    except RecipientDetails.DoesNotExist:
        recipient_profile = None

    return render(request, 'recipient.html', {'recipient': recipient_profile})


def donor(request):
    """Donor dashboard"""
    try:
        donor_profile = DonorDetails.objects.get(user=request.user)
    except DonorDetails.DoesNotExist:
        donor_profile = None

    return render(request, 'donor.html', {'donor': donor_profile})



# --- Dashboards ---

from .models import Profile, DonorDetails, RecipientDetails, BloodStock

@login_required
def admin_dashboard(request):
    donors_count = Profile.objects.filter(role='donor').count()
    recipients_count = Profile.objects.filter(role='recipient').count()
    hospitals_count = Profile.objects.filter(role='hospital').count()
    blood_units_count = BloodStock.objects.aggregate(total_units=Sum('unit'))['total_units'] or 0

    context = {
        'donors_count': donors_count,
        'recipients_count': recipients_count,
        'hospitals_count': hospitals_count,
        'blood_units_count': blood_units_count,
    }
    return render(request, 'admin_dashboard.html', context)





@login_required
def donor_dashboard(request):
    donors = DonorDetails.objects.all()
    return render(request, 'donor_dashboard.html', {'donors': donors})

@login_required
def recipient_dashboard(request):
    recipient = RecipientDetails.objects.all()
    return render(request, 'recipient_dashboard.html', {'recipient': recipient})


@login_required
def recipient_dashboard(request):
    # Get all recipients
    recipients = RecipientDetails.objects.all()  # fetch all recipients

    return render(request, 'recipient_dashboard.html', {
        'recipients': recipients
    })


@login_required
def hospital_dashboard(request):
    return render(request, 'hospital_dashboard.html')


@login_required
def blood_stock_dashboard(request):
    # Get all blood stock records, newest first
    blood_stock = BloodStock.objects.all().order_by('-added_at')

    return render(request, 'blood_stock_dashboard.html', {
        'blood_stock': blood_stock
    })

@login_required
def add_blood(request):
    message = None  # success message

    if request.method == 'POST':
        form = BloodStockForm(request.POST)
        if form.is_valid():
            form.save()
            message = "Blood added successfully!"
            form = BloodStockForm()  # reset the form after save
    else:
        form = BloodStockForm()

    return render(request, 'add_blood.html', {
        'form': form,
        'message': message
    })


# detailsform

@login_required
def donor_details_form(request):
     # Check if this recipient already has a profile
    donor = DonorDetails.objects.filter(user=request.user).first()
    if donor:
        # Already filled, go to recipient dashboard
        return redirect('donor')

    if request.method == 'POST':
        form = DonorDetailsForm(request.POST, request.FILES)
        if form.is_valid():
            donor = form.save(commit=False)  # don’t save yet
            donor.user = request.user       # link to logged-in user
            donor.save()                    # now save
            return redirect('donor')        # Redirect to dashboard/profile
    else:
        form = DonorDetailsForm()

    return render(request, 'donor_details_form.html', {'form': form})



@login_required
def recipient_details_form(request):
    # Check if this recipient already has a profile
    recipient = RecipientDetails.objects.filter(user=request.user).first()
    if recipient:
        # Already filled, go to recipient dashboard
        return redirect('recipient')

    if request.method == 'POST':
        form = RecipientDetailsForm(request.POST, request.FILES)
        if form.is_valid():
            recipient = form.save(commit=False)  # don’t save yet
            recipient.user = request.user       # link to logged-in user
            recipient.save()                    # now save
            return redirect('recipient')        # Redirect to dashboard/profile
    else:
        form = RecipientDetailsForm()

    return render(request, 'recipient_details_form.html', {'form': form})


@login_required
def hospital_details_form(request):
    try:
        hospital = HospitalDetails.objects.get(user=request.user)
        return redirect('hospital')  
    except HospitalDetails.DoesNotExist:
        pass

    if request.method == 'POST':
        form = HospitalDetailsForm(request.POST, request.FILES)
        if form.is_valid():
            hospital = form.save(commit=False)
            hospital.user = request.user
            hospital.save()
            return redirect('hospital')
    else:
        form = HospitalDetailsForm()

    return render(request, 'hospital_details_form.html', {'form': form})




# edit

@login_required
def recipient_details_edit(request):
    """Edit profile"""
    recipient = get_object_or_404(RecipientDetails, user=request.user)

    if request.method == 'POST':
        form = RecipientDetailsForm(request.POST, request.FILES, instance=recipient)
        if form.is_valid():
            form.save()
            return redirect('recipient')
    else:
        form = RecipientDetailsForm(instance=recipient)

    return render(request, 'recipient_details_edit.html', {'form': form, 'recipient': recipient})


@login_required
def donor_details_edit(request):
    """Edit profile"""
    donor = get_object_or_404(DonorDetails, user=request.user)

    if request.method == 'POST':
        form = DonorDetailsForm(request.POST, request.FILES, instance=donor)
        if form.is_valid():
            form.save()
            return redirect('donor')
    else:
        form = DonorDetailsForm(instance=donor)

    return render(request, 'donor_details_edit.html', {'form': form, 'donor': donor})



@login_required
def hospital_details_edit(request):
    """Edit profile"""
    hospital = get_object_or_404(HospitalDetails, user=request.user)

    if request.method == 'POST':
        form = HospitalDetailsForm(request.POST, request.FILES, instance=hospital)
        if form.is_valid():
            form.save()
            return redirect('hospital')
    else:
        form = HospitalDetailsForm(instance=hospital)

    return render(request, 'hospital_details_edit.html', {'form': form, 'hospital': hospital})


# ___________________________________________________________________________________________________________________


# ✅ Create new donor
def donor_create(request):
    if request.method == 'POST':
        form = DonorDetailsForm(request.POST, request.FILES)
        if form.is_valid():
            donor = form.save(commit=False)
            donor.user = request.user
            donor.save()
            return redirect('donor') 
    else:
        form = DonorDetailsForm()
    return render(request, 'donor_details_form.html', {'form': form})


def donor_edit(request, donor_id):
    donor = get_object_or_404(DonorDetails, id=donor_id)
    if request.method == 'POST':
        form = DonorDetailsForm(request.POST, request.FILES, instance=donor)
        if form.is_valid():
            form.save()
            return redirect('donor')  
    else:
        form = DonorDetailsForm(instance=donor)
    return render(request, 'edit_donor.html', {'form': form, 'donor': donor})





# users recipient dashboard

@login_required
def recipient_notifications(request):
    sample_notifications = [
        {"title": "Blood Donation Request Approved", "message": "Your recent donation request has been approved.", "created_at": "2025-10-24 12:30"},
        {"title": "Blood Camp Reminder", "message": "There is a blood camp scheduled at City Hospital tomorrow.", "created_at": "2025-10-23 15:10"},
        {"title": "Thank You!", "message": "Thank you for your recent donation. You’ve saved lives!", "created_at": "2025-10-22 09:45"},
    ]
    
    return render(request, "recipient/recipient_notifications.html", {"notifications": sample_notifications})

def recipient_blood_request_form(request):
    return render(request,'recipient/recipient_blood_request_form.html')

def received_history(request):
    return render(request, 'recipient/received_history.html')


def search_blood(request):
    return render(request, 'recipient/search_blood.html')



@login_required
def search_blood(request):
    query = request.GET.get('q', '').strip()
    blood_stock = BloodStock.objects.all().order_by('-added_at')

    if query:
        # Filter by blood group (case-insensitive)
        blood_stock = blood_stock.filter(bloodgroup__icontains=query)

    return render(request, 'recipient/search_blood.html', {
        'blood_stock': blood_stock,
        'query': query,
    })


# users_donor_dashboard

@login_required
def donor_notifications(request):
    sample_notifications = [
        {"title": "Blood Donation Request Approved", "message": "Your recent donation request has been approved.", "created_at": "2025-10-24 12:30"},
        {"title": "Blood Camp Reminder", "message": "There is a blood camp scheduled at City Hospital tomorrow.", "created_at": "2025-10-23 15:10"},
        {"title": "Thank You!", "message": "Thank you for your recent donation. You’ve saved lives!", "created_at": "2025-10-22 09:45"},
    ]
    
    return render(request, "donor/notifications.html", {"notifications": sample_notifications})


def donation_history(request):
    return render(request, 'donor/donation_history.html')


def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def donor_eligibility_test_form(request):
    if request.method == 'POST':
        form = DonorEligibilityForm(request.POST)
        if form.is_valid():
            test = form.save(commit=False)
            if request.user.is_authenticated:
                test.user = request.user

            gender = form.cleaned_data.get('gender')
            dob = form.cleaned_data.get('dob')
            age = calculate_age(dob)
            weight = form.cleaned_data.get('weight')
            hemoglobin = form.cleaned_data.get('hemoglobin_level')
            last_date = form.cleaned_data.get('last_donation_date')
            has_disease = form.cleaned_data.get('has_disease')
            on_medication = form.cleaned_data.get('on_medication')
            had_surgery_recently = form.cleaned_data.get('had_surgery_recently')

            passed = True
            reasons = []

            # ✅ Eligibility logic
            if age < 18 or age > 60:
                passed = False
                reasons.append("You must be between 18 and 60 years old to donate blood.")

            if weight < 50:
                passed = False
                reasons.append("Weight must be at least 50 kg.")

            if hemoglobin < 12.5:
                passed = False
                reasons.append("Hemoglobin level must be 12.5 g/dL or higher.")

            if has_disease:
                passed = False
                reasons.append("You have reported a disease condition.")

            if on_medication:
                passed = False
                reasons.append("You are currently on medication.")

            if had_surgery_recently:
                passed = False
                reasons.append("You have had surgery recently.")

            if last_date:
                days_since = (datetime.date.today() - last_date).days
                if gender == 'Male' and days_since < 90:
                    passed = False
                    reasons.append("Males must wait at least 90 days after their last donation.")
                elif gender == 'Female' and days_since < 120:
                    passed = False
                    reasons.append("Females must wait at least 120 days after their last donation.")

            test.passed = passed
            test.save()

            # ✅ Store result
            request.session['donor_eligibility_result'] = {
                'status': 'Eligible' if passed else 'Not Eligible',
                'reasons': reasons
            }

            return redirect('donor_eligibility_result')
    else:
        form = DonorEligibilityForm()

    return render(request, 'donor/donor_eligibility_test_form.html', {'form': form})


def donor_eligibility_result(request):
    result_data = request.session.get('donor_eligibility_result', None)
    donor = get_object_or_404(DonorDetails, user=request.user)

    if not result_data:
        messages.warning(request, "Please take the eligibility test first.")
        return redirect('donor_eligibility_test_form')

    passed = result_data['status'] == 'Eligible'

    donor.is_eligible = passed
    donor.save()

    return render(request, 'donor/donor_eligibility_result.html', {
        'status': result_data['status'],
        'reasons': result_data['reasons']
    })



@login_required
def donor_request_appointment(request):
    donor = get_object_or_404(DonorDetails, user=request.user)

    if not donor.is_eligible:
        messages.warning(request, "You must pass the eligibility test before requesting an appointment.")
        return redirect('donor_eligibility_test_form')

    if request.method == 'POST':
        form = DonorRequestAppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.donor = request.user
            appointment.save()
            messages.success(request, "Your appointment request has been submitted successfully.")
            return redirect('donor')
    else:
        form = DonorRequestAppointmentForm()

    return render(request, 'donor/donor_request_appointment.html', {'form': form})


def donor_request_appointment_form(request):
    if request.method == 'POST':
        form = DonorRequestAppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_page')  # change to your success URL
    else:
        form = DonorRequestAppointmentForm()  # ✅ must be created here

    return render(request, 'donor/donor_request_appointment_form.html', {'form': form})

