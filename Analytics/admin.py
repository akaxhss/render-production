from django.contrib import admin
from .models import *


admin.site.register(Complications)
admin.site.register(MedicalHistory)
admin.site.register(CustomerMedicalHistory)
admin.site.register(PersonalDetails)