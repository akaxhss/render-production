from django.urls import path
from .views import *

urlpatterns = [
    path('my-doctor-profile/', my_doctor_profile),
    # Diet
    path('diet-tracker-GET/', diet_tracker_get),
    path('diet-tracker-add-POST/', diet_tracker_post),
    path('all-dates-diet/', all_dates_diet),
    # Medicine
    path('medicine-GET/', medicine_get), #used
    path('medicine-POST/', medicine_post), #used to add medicine
    path('medicine-update/', medicine_update), #used to update taken medicine
    path('medicine-multiple-update/', medicine_multiple_update), #used to update taken medicine
    path('full-medicine-details/', all_medicines), # Medicine display all data of a customer
    # Symptoms
    path('Symptoms-GET/', get_symptoms),
    path('symptoms-submit/', symptom_submit), #single object
    path('symptoms-submit-multiple/', symptom_submit_array),
    path('symptoms-ADD/', add_symptoms),
    path('submit-custom-symptom/', submit_custom_symptoms), #single object
    path('submit-custom-symptom-multiple/', submit_custom_symptoms_array), #multiple
    path('submit-symptoms-with-input/', submit_symptoms_with_input),
    path('get-all-dates-symptoms/', all_dates_symptoms),
    
    # Exercise
    path('exercise-get/', exercise_get),
    path('add-custom-exercise/', add_custom_exercise),
    path('exercise-submit/', submit_exercise),
    path('exercise-submit-multiple/', submit_exercise_array),
    path('custom-exercise-submit/', submit_custom_exercise),
    path('custom-exercise-submit-multiple/', submit_custom_exercise_array),
    path('get-all-dates-exercises/', all_days_exercises),
    path('calories-burnt-add/', add_calories_burnt), # calorie
    path('consent-submit/', submit_exercise_consent),# exercise consent
    
    # Medical
    path('medical-ADD/', add_medical),
    path('medical-get-all/', get_all_medical_details),
    path('get-medical/', get_medical_details),
    path('get-medical-form-data/', get_medical_form_data),

    # contraction
    path('contraction/', add_contraction),
    path('get-contraction/', get_contraction),
    path('all-dates-contractions/', all_dates_contractions),

    # dahsborad details
    path('customer-dashboard-details/', customer_dashboard_details),

    # Calculator
    path('scan-dates/', scan_dates),

    # Activity paths
    path('add-acivity-excersice-modules/', add_modules), #To add Exercise/Activity modules and submodules
    path('submit-activity/', submit_activity),
    path('submit-activity-multiple/', submit_activity_array),
    path('submit-custom-activity/', submit_custom_activity),
    path('submit-custom-activity-multiple/', submit_custom_activity_array),
    path('get-activity-tasks/', get_activity),
    path('add-custom-activity/', add_custom_activity),
    path('get-activity-main-modules/', get_activity_main_modules),
    path('get-all-activity-data/', display_all_activity), # display all data ,
        
    path('get-free-content/' , FreeContentAPI.as_view())
]
