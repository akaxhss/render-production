from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(CustomerDetails)
admin.site.register(DoctorDetails)

admin.site.register(SalesTeamDetails)
admin.site.register(ConsultantInfo)

admin.site.register(hospitalManagerDetails)
admin.site.register(Otp)

admin.site.register(DadInfo)
admin.site.register(Banner)

admin.site.register(SymptomsRemedy)

admin.site.register(FirebaseFcm)