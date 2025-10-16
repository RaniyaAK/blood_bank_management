from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, UserForm
from .models import Profile
from django.contrib.auth.models import User

# Create your views here.

def register(request):
    form = UserForm(request.POST or None)
    error_message = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        role = request.POST.get('role', '')

        # Step 1: Check if username exists
        if User.objects.filter(username=username).exists():
            error_message = "Username already exists."

        # Step 1: Check if email exists
        if User.objects.filter(email=email).exists():
            error_message = "Email already exists."    

        # Step 2: Check if passwords match
        elif password != confirm_password:
            error_message = "Passwords do not match."

        # Step 3: Save user if no errors
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
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

                # Redirect based on role
                if user.is_superuser:
                    return redirect('admin_dashboard')
                elif user.profile.role == 'admin':
                    return redirect('admin_dashboard')
                elif user.profile.role == 'hospital':
                    return redirect('hospital')
                elif user.profile.role == 'donor':
                    return redirect('donor')
                elif user.profile.role == 'recipient':
                    return redirect('recipient')
                else:
                    return redirect('home')
            else:
                error_message = "Incorrect username or password."
        else:
            error_message = "Please enter valid credentials."

    return render(request, 'login.html', {'form': form, 'error_message': error_message})

    

# --- Dashboards ---

def home(request):
    return render(request, 'home.html')


@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


@login_required
def donor(request):
    return render(request, 'donor.html')

@login_required
def donor_dashboard(request):
    return render(request, 'donor_dashboard.html')


@login_required
def recipient(request):
    return render(request, 'recipient.html')


@login_required
def recipient_dashboard(request):
    return render(request, 'recipient_dashboard.html')


@login_required
def hospital(request):
    return render(request, 'hospital.html')


@login_required
def hospital_dashboard(request):
    return render(request, 'hospital_dashboard.html')


@login_required
def blood_stock_dashboard(request):
    return render(request, 'blood_stock_dashboard.html')

@login_required
def add_blood(request):
    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        Profile.objects.create(user=request.user,name=name, phone=phone, email=email)
        return redirect('blood_stock_dashboard')
    return render(request, 'add_blood.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')