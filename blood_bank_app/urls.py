from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('login/',views.user_login,name='login'),
    path('register/',views.register,name='register'),
    path('logout/', views.user_logout, name='logout'),

    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),

    path('dashboard/hospital/', views.hospital, name='hospital'),
    path('dashboard/hospital/info', views.hospital_dashboard, name='hospital_dashboard'),
    path('dashboard/hospital_details_form', views.hospital_details_form, name='hospital_details_form'),

    path('dashboard/donor_details_form/', views.donor_details_form, name='donor_details_form'),
    path('dashboard/donor/info', views.donor_dashboard, name='donor_dashboard'),

    path('dashboard/recipient_details_form/', views.recipient_details_form, name='recipient_details_form'),
    path('dashboard/recipient/info', views.recipient_dashboard, name='recipient_dashboard'),

    path('dashboard/recipient/', views.recipient, name='recipient'),
    path('dashboard/recipient/edit/', views.recipient_details_edit, name='recipient_edit'),


    path('dashboard/blood_stock/', views.blood_stock_dashboard, name='blood_stock_dashboard'),
    path('dashboard/add_blood/', views.add_blood, name='add_blood'),
    
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('reset_password/<str:email>/', views.reset_password, name='reset_password'),

    path('donor/add/', views.donor_create, name='donor_add'),
    path('donor/edit/<int:donor_id>/', views.donor_edit, name='donor_edit'),


]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)