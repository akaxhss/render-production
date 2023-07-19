from django.urls import path
from .views import *


urlpatterns = [
    path('get-medical-data/', get_medical_data),
    path('post-medical-data/', post_medical_data),
    path('get-medical-analysis/', get_medical_analysis),
    path('get-symptom-analysis/', get_symptom_analysis),
    path('get-personal-details/', get_personal_details),
    path('submit-personal-details/', submit_personal_details),
    path('client-criticalities/', client_criticalities),
]