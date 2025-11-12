from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout,login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.db.models import Sum

# from .forms import RecipientBloodRequestForm
from .forms import HospitalBloodRequestForm
from .forms import LoginForm, UserForm
from .forms import BloodStockForm
from .forms import RecipientDetailsForm
from .forms import DonorDetailsForm
from .forms import HospitalDetailsForm
from .forms import DonorRequestAppointmentForm
from .forms import DonorEligibilityTestForm
from .forms import RecipientBloodRequestForm

from .models import Profile
from .models import BloodStock
from .models import HospitalDetails
from .models import DonorDetails
from .models import RecipientDetails


from .models import HospitalDetails
from .models import AdminNotification

from datetime import date
import json

from .models import (
    HospitalBloodRequest,
    RecipientBloodRequest,
    DonorRequestAppointment,
    HospitalNotification,
    RecipientNotification
)
from django.http import JsonResponse

def home(request):
    return render(request, 'home.html')

# register
def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # ✅ Create user
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            user.save()

            # ✅ Create profile with role
            role = form.cleaned_data['role']
            profile = Profile.objects.create(user=user, role=role)

            # ✅ Auto login
            auth_login(request, user)

            # ✅ Redirect based on role + completion status
            if role == 'donor':
                # If donor details not yet filled → send to details form
                if not DonorDetails.objects.filter(user=user).exists():
                    return redirect('donor_details_form')
                else:
                    return redirect('donor')

            elif role == 'recipient':
                if not RecipientDetails.objects.filter(user=user).exists():
                    return redirect('recipient_details_form')
                else:
                    return redirect('recipient')

            elif role == 'hospital':
                if not HospitalDetails.objects.filter(user=user).exists():
                    return redirect('hospital_details_form')
                else:
                    return redirect('hospital')

            else:
                return redirect('home')

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

                user = authenticate(username=user.username, password=password)
                if user:
                    auth_login(request, user)

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
    """Hospital dashboard with editable profile form (AJAX compatible, no photo)"""
    hospital_profile = HospitalDetails.objects.filter(user=request.user).first()

    unread_notifications_count = HospitalNotification.objects.filter(
        hospital=request.user, is_read=False
    ).count()

    if hospital_profile:
        if request.method == 'POST':
            form = HospitalDetailsForm(request.POST, request.FILES, instance=hospital_profile)
            if form.is_valid():
                form.save()

                # ✅ For AJAX save (spinner update)
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})

                return redirect('hospital')
            else:
                # ❌ Send form errors if AJAX
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'errors': form.errors})
        else:
            form = HospitalDetailsForm(instance=hospital_profile)
    else:
        hospital_profile = None
        form = HospitalDetailsForm()

    return render(request, 'hospital.html', {
        'hospital': hospital_profile,
        'form': form,
        'unread_notifications_count': unread_notifications_count,
    })

@login_required
def recipient(request):
    """Recipient dashboard with editable profile in side panel"""
    recipient_profile = RecipientDetails.objects.filter(user=request.user).first()

    # ✅ Get unread notifications count
    unread_notifications_count = RecipientNotification.objects.filter(
        recipient=request.user, is_read=False
    ).count()

    if recipient_profile:
        if request.method == 'POST':
            form = RecipientDetailsForm(request.POST, request.FILES, instance=recipient_profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully!")
        else:
            form = RecipientDetailsForm(instance=recipient_profile)
    else:
        recipient_profile = None
        form = None  

    return render(request, 'recipient.html', {
        'recipient': recipient_profile,
        'form': form,
        'unread_notifications_count': unread_notifications_count,  # ✅ Added
    })

@login_required
def donor(request):
    """Donor dashboard with editable profile in side panel"""
    donor_profile = DonorDetails.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = DonorDetailsForm(request.POST, request.FILES, instance=donor_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
    else:
        form = DonorDetailsForm(instance=donor_profile)

    return render(request, 'donor.html', {
        'donor': donor_profile,
        'form': form,
    })


# --- Dashboards ---

@login_required
def admin_dashboard(request):
    donors_count = Profile.objects.filter(role='donor').count()
    recipients_count = Profile.objects.filter(role='recipient').count()
    hospitals_count = Profile.objects.filter(role='hospital').count()
    blood_units_count = BloodStock.objects.aggregate(total_units=Sum('unit'))['total_units'] or 0

    unread_notifications_count = AdminNotification.objects.filter(is_read=False).count()

    context = {
        'donors_count': donors_count,
        'recipients_count': recipients_count,
        'hospitals_count': hospitals_count,
        'blood_units_count': blood_units_count,
        'unread_notifications_count': unread_notifications_count,  # ✅ Pass to template
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def blood_stock_dashboard(request):
    blood_stock = BloodStock.objects.all().order_by('-added_at')

    unread_notifications_count = AdminNotification.objects.filter(is_read=False).count()

    context = {
        'blood_stock': blood_stock,
        'unread_notifications_count': unread_notifications_count,  # ✅ Pass to template
    }
    return render(request, 'dashboard/blood_stock_dashboard.html', context)


@login_required
def users(request):
    all_users = User.objects.filter(is_superuser=False, is_staff=False).order_by('-date_joined')

    user_data = []
    for user in all_users:
        if HospitalDetails.objects.filter(user=user).exists():
            role = "Hospital"
        elif DonorDetails.objects.filter(user=user).exists():
            role = "Donor"
        elif RecipientDetails.objects.filter(user=user).exists():
            role = "Recipient"
        else:
            role = "User"

        user_data.append({
            "id": user.id,
            "name": user.username,
            "email": user.email,
            "role": role,
            "date_joined": user.date_joined,  # ✅ Add joined date here
        })

    unread_notifications_count = AdminNotification.objects.filter(is_read=False).count()

    return render(request, 'dashboard/users.html', {
        "user_data": user_data,
        "unread_notifications_count": unread_notifications_count,  # ✅ Pass to template
    })


@login_required
def admin_notifications(request):
    notifications = AdminNotification.objects.all().order_by('-created_at')
    unread_notifications = notifications.filter(is_read=False)
    read_notifications = notifications.filter(is_read=True)

    context = {
        'unread_notifications': unread_notifications,
        'read_notifications': read_notifications,
        'unread_count': unread_notifications.count(),
    }
    return render(request, 'dashboard/admin_notifications.html', context)

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
    return render(request, 'donor/donor_details_form.html', {'form': form})


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

# ______________________________________________________________________________________________________________________________

# Donor_dashboard

@login_required
def donor_details_form(request):
    donor = DonorDetails.objects.filter(user=request.user).first()
    if donor:
        return redirect('donor')

    if request.method == 'POST':
        form = DonorDetailsForm(request.POST, request.FILES)
        if form.is_valid():
            donor = form.save(commit=False)  
            donor.user = request.user      
            donor.save()                    
            return redirect('donor')        
    else:
        form = DonorDetailsForm()

    return render(request, 'donor/donor_details_form.html', {'form': form})


@login_required
def donor_details_edit(request):
    """Edit donor profile (supports both AJAX and normal form)"""
    donor = get_object_or_404(DonorDetails, user=request.user)

    if request.method == 'POST':
        form = DonorDetailsForm(request.POST, request.FILES, instance=donor)
        if form.is_valid():
            form.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            return redirect('donor')
        else:
          
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = DonorDetailsForm(instance=donor)

    return render(request, 'donor/donor_details_edit.html', {'form': form, 'donor': donor})


def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


@login_required
def donor_request_appointment(request):
    donor = DonorDetails.objects.filter(user=request.user).first()
    if not donor:
        messages.warning(request, "Please complete your donor profile before requesting an appointment.")
        return redirect('donor_details_form')

    return render(request, 'donor/donor_request_appointment.html', {
        'donor': donor
    })

@login_required
def donor_eligibility_test_form(request):
    """
    Shows the eligibility test form, evaluates it, updates donor.is_eligible,
    and redirects to the eligibility result page.
    """
    donor = get_object_or_404(DonorDetails, user=request.user)

    if request.method == 'POST':
        form = DonorEligibilityTestForm(request.POST)
        if form.is_valid():
            passed = True
            reasons = []

            dob = form.cleaned_data.get('dob')
            weight = form.cleaned_data.get('weight')
            hemoglobin = form.cleaned_data.get('hemoglobin_level')
            last_date = form.cleaned_data.get('last_donation_date')
            gender = form.cleaned_data.get('gender')
            has_disease = form.cleaned_data.get('has_disease')
            on_medication = form.cleaned_data.get('on_medication')
            had_surgery_recently = form.cleaned_data.get('had_surgery_recently')

            age = calculate_age(dob)

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
                reasons.append("You have had recent surgery.")
            if last_date:
                days_since = (date.today() - last_date).days
                if gender == 'Male' and days_since < 90:
                    passed = False
                    reasons.append("Males must wait at least 90 days after last donation.")
                elif gender == 'Female' and days_since < 120:
                    passed = False
                    reasons.append("Females must wait at least 120 days after last donation.")

            donor.is_eligible = passed
            donor.save()

            request.session['eligibility_reasons'] = reasons

            return redirect(
                reverse('donor_eligibility_result') +
                f"?status={'Eligible' if passed else 'Not Eligible'}"
            )

    else:
        form = DonorEligibilityTestForm()  # initial GET

    return render(request, 'donor/donor_eligibility_test_form.html', {
        'form': form,
        'donor': donor
    })



@login_required
def donor_eligibility_result(request):
    """
    Shows eligibility result. If Eligible -> show Book Appointment button that links to the actual booking form.
    If Not Eligible -> show reasons and a button to retake the test.
    """
    status = request.GET.get('status', None)
    reasons = request.session.pop('eligibility_reasons', [])  # consume reasons from session
    return render(request, 'donor/donor_eligibility_result.html', {
        'status': status,
        'reasons': reasons
    })


@login_required
def donor_request_appointment_form(request):
    """
    The actual booking form. Only allow access if donor.is_eligible is True.
    If not eligible -> redirect back to donor_request_appointment (warning page).
    """
    donor = get_object_or_404(DonorDetails, user=request.user)

    if not donor.is_eligible:
        messages.warning(request, "You must pass the eligibility test before booking an appointment.")
        return redirect('donor_request_appointment')

    if request.method == 'POST':
        form = DonorRequestAppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.donor = request.user  # or donor
            appointment.save()
            messages.success(request, "Appointment booked successfully!")
            return redirect('donor')  # or any success page you prefer
    else:
        form = DonorRequestAppointmentForm()

    return render(request, 'donor/donor_request_appointment_form.html', {
        'form': form,
        'donor': donor
    })


@login_required
def donor_notifications(request):
    sample_notifications = [
        {"title": "Blood Donation Request Approved", "message": "Your recent donation request has been approved.", "created_at": "2025-10-24 12:30"},
        {"title": "Blood Camp Reminder", "message": "There is a blood camp scheduled at City Hospital tomorrow.", "created_at": "2025-10-23 15:10"},
        {"title": "Thank You!", "message": "Thank you for your recent donation. You’ve saved lives!", "created_at": "2025-10-22 09:45"},
    ]
    
    return render(request, "donor/donor_notifications.html", {"notifications": sample_notifications})


def donation_history(request):
    return render(request, 'donor/donation_history.html')

# ____________________________________________________________________________________________________________________________
# Recipient 

@login_required
def recipient_details_form(request):
    recipient = RecipientDetails.objects.filter(user=request.user).first()
    if recipient:
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

    return render(request, 'recipient/recipient_details_form.html', {'form': form})


@login_required
def recipient_details_edit(request):
    """Edit recipient profile (AJAX or normal request)"""
    recipient = get_object_or_404(RecipientDetails, user=request.user)

    if request.method == 'POST':
        form = RecipientDetailsForm(request.POST, request.FILES, instance=recipient)
        if form.is_valid():
            form.save()

            # ✅ For AJAX (used in dashboard side panel)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            # ✅ For normal form submission
            return redirect('recipient')
        else:
            # ❌ Handle form errors for AJAX
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = RecipientDetailsForm(instance=recipient)

    return render(request, 'recipient/recipient_details_edit.html', {'form': form, 'recipient': recipient})


@login_required
def recipient_notifications(request):
    recipient_user = request.user
    notifications = RecipientNotification.objects.filter(
        recipient=recipient_user
    ).order_by('-created_at')

    # Mark all unread notifications as read immediately
    notifications.filter(is_read=False).update(is_read=True)

    return render(request, "recipient/recipient_notifications.html", {
        "notifications": notifications
    })



def received_history(request):
    return render(request, 'recipient/received_history.html')


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


@login_required
def recipient_blood_request_form(request):
    if request.method == 'POST':
        form = RecipientBloodRequestForm(request.POST)
        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.recipient = request.user
            blood_request.save()

            # ✅ Notify admin
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                AdminNotification.objects.create(
                    user=admin_user,
                    message=f"{request.user.username} requested {blood_request.units} units of {blood_request.blood_group} blood (Urgency: {blood_request.urgency})."
                )

            messages.success(request, "Blood request submitted successfully!")
            form = RecipientBloodRequestForm()  # reset form
    else:
        form = RecipientBloodRequestForm()

    return render(request, 'recipient/recipient_blood_request_form.html', {'form': form})




# ____________________________________________________________________________________________________________________

# Hospital 
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

    return render(request, 'hospital/hospital_details_form.html', {'form': form})



@login_required
def hospital_details_edit(request):
    """Edit hospital profile (AJAX and normal form submission supported)"""
    hospital = get_object_or_404(HospitalDetails, user=request.user)

    if request.method == 'POST':
        form = HospitalDetailsForm(request.POST, request.FILES, instance=hospital)
        if form.is_valid():
            form.save()

            # ✅ For AJAX request (spinner update)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            # ✅ Normal submission
            return redirect('hospital')
        else:
            # ❌ Return errors for AJAX form submission
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = HospitalDetailsForm(instance=hospital)

    return render(request, 'hospital/hospital_details_edit.html', {'form': form, 'hospital': hospital})


def hospital_blood_request_form(request):
    if request.method == 'POST':
        form = HospitalBloodRequestForm(request.POST)
        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.hospital = request.user
            blood_request.save()

            # ✅ Create Admin Notification after saving
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                AdminNotification.objects.create(
                    user=admin_user,
                    message=f"{request.user.username} requested {blood_request.units} units of {blood_request.blood_group} blood."
                )

            messages.success(request, "Blood request submitted successfully!")

            # ✅ Show success message and reset form (stay on same page)
            form = HospitalBloodRequestForm()  # clears form fields
    else:
        form = HospitalBloodRequestForm()

    return render(request, 'hospital/hospital_blood_request_form.html', {'form': form})


def hospital_add_blood_stock(request):
    if request.method == 'POST':
        form = BloodStockForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blood stock added successfully!')
            return redirect('hospital_add_blood_stock')
    else:
        form = BloodStockForm()
    
    return render(request, 'hospital/hospital_add_blood_stock.html', {'form': form})


def hospital_blood_stock_chart(request):
    stock_data = (
        BloodStock.objects.values('blood_group')
        .annotate(total_units=Sum('unit'))
        .order_by('blood_group')
    )

    # Prepare data
    labels = [entry['blood_group'] for entry in stock_data]
    values = [entry['total_units'] for entry in stock_data]

    print("Labels:", labels)
    print("Values:", values)

    # Pass data to template
    context = {
        'labels': json.dumps(labels),
        'values': json.dumps(values),
    }
    return render(request, 'hospital/hospital_blood_stock_chart.html', context)

@login_required
def hospital_notifications(request):
    hospital_user = request.user
    notifications = HospitalNotification.objects.filter(
        hospital=hospital_user
    ).order_by('-created_at')
    notifications.filter(is_read=False).update(is_read=True)

    return render(request, 'hospital/hospital_notifications.html', {'notifications': notifications})


# ______________________________________________________________________________________________________________________________


# -------------------- MANAGE REQUESTS (Dashboard) --------------------

@login_required
def manage_requests(request):
    # 🏥 Hospital Requests
    hospital_requests = HospitalBloodRequest.objects.all().order_by('-created_at')

    # 🩸 Donor Requests
    donor_requests = DonorRequestAppointment.objects.all().order_by('-created_at')

    # 💉 Recipient Requests
    recipient_requests = RecipientBloodRequest.objects.all().order_by('-created_at')

    # 🔔 Unread notifications count
    unread_notifications_count = AdminNotification.objects.filter(is_read=False).count()

    context = {
        'hospital_requests': hospital_requests,
        'donor_requests': donor_requests,
        'recipient_requests': recipient_requests,
        'unread_notifications_count': unread_notifications_count,
        'today': date.today(),  # ✅ Added — used in template for expiry check
    }

    return render(request, 'dashboard/manage_requests.html', context)


# -------------------- APPROVE / REJECT REQUESTS --------------------


# ✅ Hospital Requests
# ✅ Hospital Requests
@login_required
def approve_hospital_request(request, request_id):
    hospital_request = get_object_or_404(HospitalBloodRequest, id=request_id)

    hospital_request.status = 'Approved'
    hospital_request.save()

    # Notify admin (optional, for log)
    AdminNotification.objects.create(
        user=request.user,
        message=f"Hospital request from {hospital_request.hospital.username} has been approved."
    )

    # ✅ Notify hospital user
    HospitalNotification.objects.create(
        hospital=hospital_request.hospital,
        message="Your blood request has been approved."
    )

    # ❌ Removed messages.success
    return redirect('manage_requests')


@login_required
def reject_hospital_request(request, request_id):
    hospital_request = get_object_or_404(HospitalBloodRequest, id=request_id)

    hospital_request.status = 'Rejected'
    hospital_request.save()

    # Notify admin (optional)
    AdminNotification.objects.create(
        user=request.user,
        message=f"Hospital request from {hospital_request.hospital.username} has been rejected."
    )

    # ✅ Notify hospital user
    HospitalNotification.objects.create(
        hospital=hospital_request.hospital,
        message="Your blood request has been rejected."
    )

    # ❌ Removed messages.error
    return redirect('manage_requests')



# ✅ Donor Requests (No date restriction)
@login_required
def approve_donor_request(request, request_id):
    donor_request = get_object_or_404(DonorRequestAppointment, id=request_id)
    donor_request.status = 'Approved'
    donor_request.save()

    AdminNotification.objects.create(
        user=request.user,
        message=f"Donor appointment from {donor_request.donor.username} approved."
    )

    messages.success(request, "Donor appointment approved successfully!")
    return redirect('manage_requests')


@login_required
def reject_donor_request(request, request_id):
    donor_request = get_object_or_404(DonorRequestAppointment, id=request_id)
    donor_request.status = 'Rejected'
    donor_request.save()

    AdminNotification.objects.create(
        user=request.user,
        message=f"Donor appointment from {donor_request.donor.username} rejected."
    )

    messages.error(request, "Donor appointment rejected.")
    return redirect('manage_requests')


# ✅ Recipient Requests
@login_required
def approve_recipient_request(request, request_id):
    recipient_request = get_object_or_404(RecipientBloodRequest, id=request_id)
    recipient_request.status = 'Approved'
    recipient_request.save()

    # Notify admin/log
    AdminNotification.objects.create(
        user=request.user,
        message=f"Recipient request from {recipient_request.recipient.username} approved."
    )

    # ✅ Notify recipient
    RecipientNotification.objects.create(
        recipient=recipient_request.recipient,
        message=f"Your blood request for {recipient_request.blood_group} ({recipient_request.units} units) has been approved."
    )

    return redirect('manage_requests')


@login_required
def reject_recipient_request(request, request_id):
    recipient_request = get_object_or_404(RecipientBloodRequest, id=request_id)
    recipient_request.status = 'Rejected'
    recipient_request.save()

    # Notify admin/log
    AdminNotification.objects.create(
        user=request.user,
        message=f"Recipient request from {recipient_request.recipient.username} rejected."
    )

    # ✅ Notify recipient
    RecipientNotification.objects.create(
        recipient=recipient_request.recipient,
        message=f"Your blood request for {recipient_request.blood_group} ({recipient_request.units} units) has been rejected."
    )

    return redirect('manage_requests')

@login_required
def recipient_notifications_mark_read(request):
    if request.method == "POST":
        # Mark all unread notifications for this recipient as read
        request.user.recipientnotification_set.filter(is_read=False).update(is_read=True)
    return JsonResponse({"success": True})


@login_required
def hospital_notifications_mark_read(request):
    if request.method == "POST":
        # Mark all unread notifications for this hospital as read
        request.user.hospitalnotification_set.filter(is_read=False).update(is_read=True)
    return JsonResponse({"success": True})

@login_required
def admin_notifications_mark_read(request):
    if request.method == "POST":
        AdminNotification.objects.filter(is_read=False).update(is_read=True)
    return JsonResponse({"success": True})
