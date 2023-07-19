
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
]

