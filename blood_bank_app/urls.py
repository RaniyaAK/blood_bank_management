from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/',views.user_login,name='login'),
    path('register/',views.register,name='register'),
    path('logout/', views.user_logout, name='logout'),

    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/recipient/', views.recipient_dashboard, name='recipient_dashboard'),
    path('dashboard/donour/', views.donour_dashboard, name='donour_dashboard'),
    path('dashboard/hospital/', views.hospital_dashboard, name='hospital_dashboard'),

]