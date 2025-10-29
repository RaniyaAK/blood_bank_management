from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, UserForm
from .models import Profile
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import BloodStockForm
from .models import BloodStock
from datetime import datetime
from .models import DonorDetails, RecipientDetails, Profile, BloodStock,HospitalDetails
from .forms import RecipientDetailsForm
from .forms import DonorDetailsForm
from .forms import HospitalDetailsForm
from django.contrib.auth.models import User
from django.db.models import Sum
from django.contrib import messages
from .forms import DonorRequestAppointmentForm


def home(request):
    return render(request, 'home.html')

def register(request):
    form = UserForm(request.POST or None)
    error_message = None

    if request.method == 'POST':
        first_name = request.POST.get("first_name",'').strip()
        last_name = request.POST.get("last_name",'').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        role = request.POST.get('role', '')

       
        if User.objects.filter(username=username).exists():
            error_message = "Username already exists."

        if User.objects.filter(email=email).exists():
            error_message = "Email already exists."    


        elif password != confirm_password:
            error_message = "Passwords do not match."

        else:
            user = User.objects.create_user(first_name=first_name, last_name=last_name,username=username, email=email, password=password)
            Profile.objects.create(user=user, role=role)
            return redirect('login')

    return render(request, 'register.html', {
        'form': form,
        'error_message': error_message
    })


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

@login_required
def admin_dashboard(request):
    donors_count = DonorDetails.objects.count()
    recipients_count = RecipientDetails.objects.count()
    blood_units_count = BloodStock.objects.aggregate(total_units=Sum('unit'))['total_units'] or 0

    context = {
        'donors_count': donors_count,
        'recipients_count': recipients_count,
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


# @login_required
# def hospital_dashboard(request):
#     hospitals = HospitalDetails.objects.all()  # get all registered hospitals
#     hospital_count = hospitals.count()  # total hospitals

#     return render(request, 'hospital_dashboard.html', {
#         'hospitals': hospitals,
#         'hospital_count': hospital_count
#     })



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
    success = False  # to control message display

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
                success = True
                messages.success(request, 'Password reset successful! You can now log in.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid user.')

    return render(request, 'reset_password.html', {'email': email, 'success': success})



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



# logout

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


# users_donor_dashboard

@login_required
def donor_notifications(request):
    # temporary sample data (no database needed yet)
    sample_notifications = [
        {"title": "Blood Donation Request Approved", "message": "Your recent donation request has been approved.", "created_at": "2025-10-24 12:30"},
        {"title": "Blood Camp Reminder", "message": "There is a blood camp scheduled at City Hospital tomorrow.", "created_at": "2025-10-23 15:10"},
        {"title": "Thank You!", "message": "Thank you for your recent donation. You’ve saved lives!", "created_at": "2025-10-22 09:45"},
    ]
    
    return render(request, "donor/notifications.html", {"notifications": sample_notifications})

def donation_history(request):
    return render(request, 'donor/donation_history.html')

def donor_eligibility_test(request):
    return render(request, 'donor/donor_eligibility_test.html')

def donor_request_appointment(request):
    return render(request, 'donor/donor_request_appointment.html')


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



def donor_eligibility_test(request):
    if request.method == 'POST':
        age = int(request.POST.get('age'))
        weight = int(request.POST.get('weight'))
        hemoglobin = float(request.POST.get('hemoglobin'))
        recent_donation = request.POST.get('recent_donation')
        illness = request.POST.get('illness')
        medication = request.POST.get('medication')
        surgery_vaccine = request.POST.get('surgery_vaccine')

        # Eligibility logic
        if age < 18 or age > 60:
            result = "Not Eligible: Age must be between 18 and 60."
        elif weight < 50:
            result = "Not Eligible: Weight must be at least 50 kg."
        elif hemoglobin < 12.5:
            result = "Not Eligible: Hemoglobin level is too low."
        elif recent_donation == "yes" or illness == "yes" or medication == "yes" or surgery_vaccine == "yes":
            result = "Not Eligible: Health conditions do not permit donation currently."
        else:
            result = "Eligible: You can donate blood!"

        # Redirect to result page with result in session
        request.session['eligibility_result'] = result
        return redirect('eligibility_result')

    return render(request, 'donor/donor_eligibility_test.html')

def eligibility_result(request):
    result = request.session.get('eligibility_result', None)
    return render(request, 'donor/eligibility_result.html', {'result': result})


def donor_request_appointment(request):
    if request.method == 'POST':
        form = DonorRequestAppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.donor = request.user
            appointment.save()
            messages.success(request, "Your appointment request has been submitted successfully.")
            return redirect('donor_request_appointment')
    else:
        form = DonorRequestAppointmentForm()

    return render(request, 'donor/donor_request_appointment.html', {'form': form})






