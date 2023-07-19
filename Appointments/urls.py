from django.urls import path
from .views import *

urlpatterns = [
    path('customer-booking/', customer_booking),
    path('approve-appointment/', approve),
    path('reschedule-appointment/', reschedule),
    path('reject-appointment/', reject),
    path('completed-appointment/', completed),
    path('upcoming-appointments/', upcoming),
    path('appointment-payments/' , appointment_payments),
    # full apoinments
    path('full-appointment/', full_apointments),
    path('get_doctor_info/' ,get_doctor_price),

    path('get_appointments/' , get_appointments),

    # add summary
    path('add-summary/', add_summary),
    path('get-summary/', get_summary_client),
    path('get-summary-doctor/', get_summary_doctor),
    path('clients-appointment-payments/', client_appointment_payments)
]

