from django.urls import path
from .views import *

urlpatterns = [
    path('dashboard-details/', dashboard_details),
    # ? assign a manager for the doctor
    path('assign-hospital-manager/', assign_hospital_manager),

    path('doctors-under-hospital-manager/', doctors_under_hospital),
    path('clients-under-doctors/', clients_under_doctors),
    path('all-clients/', all_clients),
    path('clients-with-no-subscription/', clients_with_no_subscription)
]

