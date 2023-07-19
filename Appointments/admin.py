from django.contrib import admin
from .models import Appointments, AppointmentSummary
# Register your models here.
admin.site.register(Appointments)
admin.site.register(AppointmentSummary)