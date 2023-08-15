
from django.urls import path
from .views import *


urlpatterns = [
    path('send-message/', send_message),
    path('get-all-messages/', get_all_messages),
    path('get-all-consultants/', get_all_consultants),
    path('get-clients-doctor/', get_clients_doctor),
    path('get-all-sales/', get_all_sales),
    path('get-all-clients/', get_all_clients),
    path('get-all-clients-of-doctor/', get_all_clients_of_doctor),
    path('all-sales-team/',all_sales_team),
    path('all-consultants-list/',all_consultants_list),
    path('generate_message_notification/<int:user_id>/<str:user_pic>/',generate_message_notification, name='generate_message_notification'),
]

