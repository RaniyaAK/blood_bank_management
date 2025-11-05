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


# dashboard
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/users/', views.users, name='users'),
    path('dashboard/blood_stock_dashboard/', views.blood_stock_dashboard, name='blood_stock_dashboard'),
    path('dashboard/admin_notifications/', views.admin_notifications, name='admin_notifications'),



# hospital
    path('hospital/', views.hospital, name='hospital'),
    path('hospital_registration_form/', views.hospital_details_form, name='hospital_details_form'),
    path('hospital/hospital_details_edit/', views.hospital_details_edit, name='hospital_details_edit'),
    path('hospital/notifications/', views.hospital_notifications, name='hospital_notifications'),
    path('hospital/hospital_add_blood_stock/', views.hospital_add_blood_stock, name='hospital_add_blood_stock'),
    path('hospital/hospital_blood_stock_chart/', views.hospital_blood_stock_chart, name='hospital_blood_stock_chart'),
    path('hospital/hospital_blood_request_form/', views.hospital_blood_request_form, name='hospital_blood_request_form'),


# donor
    path('donor/', views.donor, name='donor'),
    path('donor_registration_form/', views.donor_details_form, name='donor_details_form'),
    path('donor/donor_details_edit/', views.donor_details_edit, name='donor_details_edit'),
    path('donor/notifications/', views.donor_notifications, name='donor_notifications'),

    path('donor/donation_history/', views.donation_history, name='donation_history'),

    path('donor/donor_request_appointment/', views.donor_request_appointment, name='donor_request_appointment'),
    path('donor/donor_request_appointment_form/', views.donor_request_appointment_form, name='donor_request_appointment_form'),
    path('donor/donor_eligibility_test_form/', views.donor_eligibility_test_form, name='donor_eligibility_test_form'),
    path('donor/donor_eligibility_result/', views.donor_eligibility_result, name='donor_eligibility_result'),



# recipient
    path('recipient/', views.recipient, name='recipient'),

    path('recipient_registration_form/', views.recipient_details_form, name='recipient_details_form'),
    path('recipient/recipient_details_edit/', views.recipient_details_edit, name='recipient_details_edit'),
    path('recipient/notifications/', views.recipient_notifications, name='recipient_notifications'),

    path('recipient/received_history/', views.received_history, name='received_history'),
    path('recipient/recipient_blood_request_form/', views.recipient_blood_request_form, name='recipient_blood_request_form'),
    path('recipient/search_blood/', views.search_blood, name='search_blood'),


    # path('dashboard/add_blood/', views.add_blood, name='add_blood'),



# passwords
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password/<str:email>/', views.reset_password, name='reset_password'),

    path('donor/add/', views.donor_create, name='donor_add'),
    path('donor/edit/<int:donor_id>/', views.donor_edit, name='donor_edit'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)