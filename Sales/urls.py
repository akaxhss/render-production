from django.urls import path
from .views import *



urlpatterns = [
    path('request-response/', request_response), #respond to request for client details
    path('view-all-details-request/', view_all_requests), #to view all request for client detail
    path('investigation-report/', investigation_submit),
    path('delete-custom-investigation/', delete_custom_investigation),
    path('custom-investigation-report/', submit_custom_investigation),
    path('sales-dashboard-details/', sales_dashboard_details),
    # Last updated in less than 24 hours
    path('last-update-before-24-hours/', last_updated_before_one_day),
    # call response
    path('call-response/', add_call_response),
    path('get-call-response/', get_call_response),
    path('get-all-call-responses/', get_all_call_responses),
    # clients of a sales team
    path('clients-under-sales-team/', clients_under_sales),


    path('client-this-month/', clients_this_month),
    path('no-update-clients/', no_update_clients),
    
    path('all-clients/', all_clients),
    path('sales-team-called/',sales_team_called_list, name='sales-team-called')


]

