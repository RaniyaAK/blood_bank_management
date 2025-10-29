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
    path('dashboard/hospital_dashboard/', views.hospital_dashboard, name='hospital_dashboard'),
    path('dashboard/donor_dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('dashboard/recipient_dashboard/', views.recipient_dashboard, name='recipient_dashboard'),

    path('hospital/', views.hospital, name='hospital'),
    path('hospital_registration_form/', views.hospital_details_form, name='hospital_details_form'),
    path('hospital/details_edit/', views.hospital_details_edit, name='hospital_edit'),

    path('donor/', views.donor, name='donor'),
    path('donor_registration_form/', views.donor_details_form, name='donor_details_form'),
    path('donor/details_edit/', views.donor_details_edit, name='donor_edit'),
    path('donor/notifications/', views.donor_notifications, name='donor_notifications'),
    path('donor/donation_history/', views.donation_history, name='donation_history'),
    path('donor/eligibility_test/', views.donor_eligibility_test, name='donor_eligibility_test'),
    path('donor/request_appointment/', views.donor_request_appointment, name='donor_request_appointment'),
    path('eligibility_result/', views.eligibility_result, name='eligibility_result'),
    path('donor_request_appointment/', views.donor_request_appointment, name='donor_request_appointment'),



    path('recipient/', views.recipient, name='recipient'),
    path('recipient_registration_form/', views.recipient_details_form, name='recipient_details_form'),
    path('recipient/details_edit/', views.recipient_details_edit, name='recipient_edit'),
    path('recipient/notifications/', views.recipient_notifications, name='recipient_notifications'),
    path('recipient/recipient_blood_request_form/', views.recipient_blood_request_form, name='recipient_blood_request_form'),
    path('recipient/received_history/', views.received_history, name='received_history'),
    path('recipient/search_blood/', views.search_blood, name='search_blood'),


    path('dashboard/blood_stock/', views.blood_stock_dashboard, name='blood_stock_dashboard'),
    path('dashboard/add_blood/', views.add_blood, name='add_blood'),
    
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password/<str:email>/', views.reset_password, name='reset_password'),

    path('donor/add/', views.donor_create, name='donor_add'),
    path('donor/edit/<int:donor_id>/', views.donor_edit, name='donor_edit'),

    



]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)