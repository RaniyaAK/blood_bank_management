from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/',views.user_login,name='login'),
    path('register/',views.register,name='register'),
    path('logout/', views.user_logout, name='logout'),

    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),

    path('dashboard/hospital/', views.hospital, name='hospital'),
    path('dashboard/hospital/info', views.hospital_dashboard, name='hospital_dashboard'),

    path('dashboard/donor/', views.donor, name='donor'),
    path('dashboard/donor/info', views.donor_dashboard, name='donor_dashboard'),

    path('dashboard/recipient/', views.recipient, name='recipient'),
    path('dashboard/recipient/info', views.recipient_dashboard, name='recipient_dashboard'),

    path('dashboard/blood_stock/', views.blood_stock_dashboard, name='blood_stock_dashboard'),
    path('dashboard/add_blood/', views.add_blood, name='add_blood'),
    
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('reset_password/<str:email>/', views.reset_password, name='reset_password'),


]