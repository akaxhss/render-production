
from Accounts.models import ConsultantInfo
from django.urls import path
from .views import *


urlpatterns = [
    path('consultant-dashboard-details/', consultant_dashboard_details),
    path('add-customized-plan/', add_customized_plan)
]
