from django.urls import path
from .views import *

urlpatterns = [
    # client subscription 
    path('get-client-subscription/', get_client_subscription),

    path('get_memberships/' , get_memberships),
    path('purchase_memberships/' , purchase_memberships),
    path('get_purchased_memberships/' , get_purchased_memberships),
    path('webhook2/' , WebHook.as_view()),
    path('webhook3/' , AppointmentWebHook.as_view()),

    

    path('all-plans/', get_all_plans),
    path('get-subscription/', payment),
    path('checkout/', checkout),
    path('failed/', halted),
    path('success/', success),

    # get free subscription
    path('free-subscription/', get_free_subscription),

    # for appointments
    path('appointment-payment/', appointment_payment),
    path('appointment-payment-handler/', appointment_payment_handler),
    path('test/', test),

    # get user data for payment pop-up
    path('get-user-data/', get_user_data)
]
