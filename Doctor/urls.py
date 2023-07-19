from django.urls import path
from .views import *

urlpatterns = [
    path('view-my-patients/', my_patients),
    path('request-patient-details/', request_patient_details),
    path('patient-details/', patient_details),

    # clients this month
    path('clients-this-month/', clients_this_month),

    # doctor profile
    path('doctor-profile/', doctor_profile),
    
    # dashboard-detials
    path('doctor-dashboard-details/', doctor_dashboard_details),

    # pending approval request
    path('approval-pending-appointments/', approval_requests),

    # todays appointments
    path('todays-appointments/', todays_appointments),
    
    # All Appointment
    path('all-appointment/', all_appointments),

    # Doctor filtering
    path('doctor-filter/', doctor_filter),

    path('get-doctors/' , get_doctors),
    path('get-doctor-appointments/<id>/' , get_doctor_appointments)
]

