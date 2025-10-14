from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, UserForm
from .models import Profile
from django.contrib.auth.models import User

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = UserForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('admin_dashboard' if user.is_superuser else 'admin_dashboard')
            else:
                return render(request, 'login.html', {'form': form, 'error': 'Invalid credentials'})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# --- Dashboards ---
@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

def donour_dashboard(request):
    return render(request, 'donour_dashboard.html')

def patient_dashboard(request):
    return render(request, 'patient_dashboard.html')

def hospital_dashboard(request):
    return render(request, 'hospital_dashboard.html')


def home(request):
    return render(request, 'home.html')

def user_logout(request):
    logout(request)
    return redirect('login')