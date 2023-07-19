from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(PatientDetailsApporval)

admin.site.register(Investigation)
admin.site.register(InvestigationWithDescriptions)
admin.site.register(CustomInvestigation)

admin.site.register(InvestigationCriticallity)

admin.site.register(CallResponses)
admin.site.register(CustomerCallReposnses)

admin.site.register(CriticalityChange)
admin.site.register(SalesTeamCalled)
