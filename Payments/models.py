# from os import F_OK
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.deletion import SET_NULL
from Appointments.models import Appointments
User = get_user_model() 
# from datetime import datetime
# Create your models here.

class MemberShip(models.Model):
    membership_name = models.CharField(max_length=100)
    membership_amount = models.IntegerField()

    def __str__(self) -> str:
        return self.membership_name
    

class PurchasedMembership(models.Model):
    user = models.ForeignKey(User , on_delete=models.SET_NULL , null=True , blank=True)
    membership = models.ForeignKey(MemberShip , on_delete=models.SET_NULL,null=True , blank=True)
    is_paid = models.BooleanField(default=False)
    uid = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)



# holds the different membership plans
class MembershipPlans(models.Model):
    name = models.CharField(max_length=500)
    validity = models.IntegerField()
    amount = models.IntegerField()
    recurrence_count = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.name} {str(self.validity)} days validity"


class Payments(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    # membership = models.ForeignKey(MembershipPlans, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField(auto_now_add=True, null=True)
    amount = models.IntegerField(default=0)
    sub_Id = models.CharField(max_length=400,default='') #subscription_id
    paymentId = models.CharField(max_length=400,default='')
    signature = models.CharField(max_length=400,default='')
    captured = models.BooleanField(default=False)


class Subscriptions(models.Model):
    membership = models.ForeignKey(MembershipPlans, on_delete=models.SET_NULL, null=True, related_name="sub_membership") 
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sub_client')
    # payments = models.ForeignKey(Payments ,on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True, null=True)
    valid_till = models.DateTimeField()
    is_active = models.BooleanField(default=True)


# for appointments
class AppointmentPayments(models.Model):
    appointment = models.ForeignKey(Appointments, on_delete=SET_NULL, null=True, related_name="payments_appointment")
    timestamp = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField(default=0)
    order_id = models.CharField(max_length=400,default='')
    payment_id = models.CharField(max_length=400,default='')
    signature = models.CharField(max_length=400,default='')
    captured = models.BooleanField(default=False)

