from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Payments)



# admin.site.register(MembershipPlans)
# admin.site.register(Subscriptions)
admin.site.register(AppointmentPayments)
admin.site.register(MemberShip)
admin.site.register(PurchasedMembership)