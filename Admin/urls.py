from django.urls import path
from .views import *



urlpatterns = [
    path('admin-dashboard-details/', admin_dashboard),

    # all doctors list
    path('all-doctors-list/', all_doctors),
    # all sales team
    path('all-salesTeam-list/', all_sales_team ),

    # all clients list
    path('all-clients-list/', all_clients_list),

    # all consultants
    path('all-consultants-list/', all_consultants_list),

    path('all-hospitals/', all_hospitals),

    # change membership plan of customers
    path('membership-plans/', get_membership_plans),
    path('change-client-membership/', change_client_membership),

    # subscriptions tab
    path('subscriptions-tab/', subscriptions_data),

    # clients with basic subscriptions
    path('clients-with-basic-plan/', clients_with_basic_plan),

    # clients with standard plan
    path('clients-with-standard-plan/', clients_with_standard_plan),

    # get call status/response by date
    path('get-call-response-status/', get_call_response),

    path('doctor-approval-requests/', doctor_approval_requests),
    path('approve-doctor/', approve_doctor),

    # delete and edit exercises and activity
    path('all-excercises-per-stage/', all_exercises),
    path('edit-exercise/', edit_exercise),
    path('toggle-exercise/', toggle_exercise),

    # activity
    path('all-activity-main-modules-per-stage/', all_activity_main_modules),
    path('activity-sub-modules/', all_activity_sub_modules),
    path('edit-activity-main-module/', edit_activity_main_module),
    path('edit-activity-sub-module/', edit_activity_sub_module),

    path('toggle-activity-main-module/', toggle_main_module),
    path('toggle-activity-sub-module/', toggle_sub_module),

    # symptoms
    path('all-dates-critical-symptoms/', all_dates_critical_symptoms),
    path('get-critical-symptoms/', get_critical_symptoms),
    path('submit-critical-symptom/', submit_critical_symptom),
         
    path('free-content/' , FreeContentAPI.as_view())
]

