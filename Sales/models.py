# from typing import Callable
# from django.core.checks.messages import Critical
from enum import unique
from django.db import models
from django.db.models.base import Model
from Accounts.models import DoctorDetails, CustomerDetails, SalesTeamDetails
from django.contrib.auth import get_user_model
User = get_user_model() 
# Create your models here.


class PatientDetailsApporval(models.Model):
    doctor = models.ForeignKey(DoctorDetails, on_delete=models.CASCADE)
    customer = models.ForeignKey(CustomerDetails, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True,null=True)
    
    class Meta:
        unique_together = ['doctor', 'customer']
        ordering = ['-date']


    def __str__(self) :
        return self.doctor.user.firstname + " " + self.customer.user.firstname


class InvestigationCriticallity(models.Model):
    name = models.CharField(max_length=100, null=True)
    criticality = models.IntegerField(default=0)

    def __str__(self) -> str:
        return str(self.criticality)




class Investigation(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_investigation')
    sales = models.ForeignKey(SalesTeamDetails, on_delete=models.CASCADE)
    lastUpdated = models.DateTimeField(auto_now_add=True)
    date = models.DateField(null=False)
    # dateAdded

    hb_value = models.CharField(max_length=200, null=True, blank=True)
    hb_normal = models.CharField(max_length=200, null=True, blank=True)

    ict_value = models.CharField(max_length=200, null=True, blank=True)
    ict_normal = models.CharField(max_length=200, null=True, blank=True)

    urineRE_value = models.CharField(max_length=200, null=True, blank=True)
    urineRE_normal = models.CharField(max_length=200, null=True, blank=True)

    urineCS_value = models.CharField(max_length=200, null=True, blank=True)
    urineCS_normal = models.CharField(max_length=200, null=True, blank=True)

    vdrl_value = models.CharField(max_length=200, null=True, blank=True)
    vdrl_normal = models.CharField(max_length=200, null=True, blank=True)

    hiv_value = models.CharField(max_length=200, null=True, blank=True)
    hiv_normal = models.CharField(max_length=200, null=True, blank=True)

    hiv_value = models.CharField(max_length=200, null=True, blank=True)
    hiv_normal = models.CharField(max_length=200, null=True, blank=True)

    rbs_first_trimester_value = models.CharField(max_length=200, null=True, blank=True)
    rbs_first_trimester_normal = models.CharField(max_length=200, null=True, blank=True)

    ogct_second_trimester_value = models.CharField(max_length=200, null=True, blank=True)
    ogct_second_trimester_normal = models.CharField(max_length=200, null=True, blank=True)

    ogtt_second_trimester_value = models.CharField(max_length=200, null=True, blank=True)
    ogtt_second_trimester_normal = models.CharField(max_length=200, null=True, blank=True) 

    hcv_value = models.CharField(max_length=200, null=True, blank=True)
    hcv_normal = models.CharField(max_length=200, null=True, blank=True)

    creatine_value = models.CharField(max_length=200, null=True, blank=True)
    creatine_normal = models.CharField(max_length=200, null=True, blank=True)

    double_marker_value = models.CharField(max_length=200, null=True, blank=True)
    double_marker_normal = models.CharField(max_length=200, null=True, blank=True)

    tft_value = models.CharField(max_length=200, null=True, blank=True)
    tft_normal = models.CharField(max_length=200, null=True, blank=True)
    tft_description = models.CharField(max_length=200, null=True, blank=True)

    others_value = models.CharField(max_length=200, null=True, blank=True)
    others_normal = models.CharField(max_length=200, null=True, blank=True)
    others_description = models.CharField(max_length=200, null=True, blank=True)

    criticallity = models.ForeignKey(InvestigationCriticallity, on_delete=models.CASCADE, null=True)

    scan = models.CharField(max_length=200, null=True, blank=True)
    scanDescription = models.TextField(null=True, blank=True)


    def __str__(self):
        return self.customer.firstname

    class Meta:
        get_latest_by = ['date']
        unique_together = ['date', 'customer']




from django.db.models.signals import post_save
from django.dispatch import receiver
from Accounts.helper import send_notification

@receiver(post_save, sender=Investigation)
def investigation_created(sender, instance, **kwargs):
    try:

        info_data =  {
            "notification_type" : "criticality",
            "sender_id" : instance.sender.id ,
            "receiver_id" : instance.receiver.id,
            "message_id" : instance.id,
        }

        customer = CustomerDetails.objects.get(user = instance.customer)
        fcm_tokens =  customer.referalId.user.fcm_tokens.all()

        if fcm_tokens.exists():
            fcm_token = [f.fcm_token for f in fcm_tokens]
            criticallity = instance.criticallity.name
            print(fcm_token)
            send_notification(
                fcm_token,
                'New Notification from Shebirth',
                f'Patient {(instance.user.firstname).capitalize()} criticality level changed to {criticallity}',
                action = "criticality"
            )


    except Exception as e:
        print(e)




# ! not used/removed (moved all fields to above model investigation)
class InvestigationWithDescriptions(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    sales = models.ForeignKey(SalesTeamDetails, on_delete=models.CASCADE, null=True)
    lastUpdated = models.DateTimeField(auto_now_add=True)
    date = models.DateField()

    tft_value = models.CharField(max_length=200, null=True, blank=True)
    tft_normal = models.CharField(max_length=200, null=True, blank=True)
    tft_description = models.CharField(max_length=200, null=True, blank=True)

    others_value = models.CharField(max_length=200, null=True, blank=True)
    others_normal = models.CharField(max_length=200, null=True, blank=True)
    others_description = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.customer.firstname


class CustomInvestigation(models.Model):
    # investigation = models.ForeignKey(Investigation, on_delete=models.CASCADE, null=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date = models.DateField(null=True)
    sales = models.ForeignKey(SalesTeamDetails, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=500, null=True, blank=True)
    value = models.CharField(max_length=500, null=True, blank=True)
    normal_range = models.CharField(max_length=500, null=True, blank=True)


class CallResponses(models.Model):
    response = models.CharField(max_length=200)

    def __str__(self):
        return self.response
    class Meta:
        verbose_name = "CallResponses (Manual)"

# to keep the response by customers 
class CustomerCallReposnses(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    response = models.ForeignKey(CallResponses, on_delete=models.CASCADE, null=True)
    sales = models.ForeignKey(SalesTeamDetails, on_delete=models.CASCADE, null=True, blank=True)
    note = models.TextField(blank=True, null=True)
    date = models.DateField()

    class Meta:
        unique_together = ['customer', 'date']


class CriticalityChange(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='criticality_change')
    criticallity = models.ForeignKey(InvestigationCriticallity, on_delete=models.CASCADE, null=True)
    date = models.DateField()
    consent = models.BooleanField(default=False)



@receiver(post_save, sender=CriticalityChange)
def criticality_change(sender, instance, **kwargs):
    from Accounts.models import FirebaseFcm ,ConsultantInfo
    try:
        info_data = {
            "notification_type" : "criticality",
            "customer_id" : instance.customer.id 
        }
        customer_detail = CustomerDetails.objects.get(user = instance.customer)
        fcm_tokens = customer_detail.referalId.user.fcm_tokens.all()
        sales_team = SalesTeamDetails.objects.all()
        consultant_team = ConsultantInfo.objects.all()
        fcm_tokens_for_sales = []
        fcm_tokens_for_consultant = []


        for st in sales_team:
            firebase_token_objs = FirebaseFcm.objects.filter(user = st.user)
            print(firebase_token_objs)
            fcm_tokens_for_sales.extend(
                firebase_toke_obj.fcm_token
                for firebase_toke_obj in firebase_token_objs
            )

        for ct in consultant_team:
            firebase_token_objs = FirebaseFcm.objects.filter(user = ct.user)
            print(firebase_token_objs)
            fcm_tokens_for_consultant.extend(
                firebase_toke_obj.fcm_token
                for firebase_toke_obj in firebase_token_objs
            )


        fcm_token = [f.fcm_token for f in fcm_tokens]
        fcm_token = fcm_token + fcm_tokens_for_sales + fcm_tokens_for_consultant

        if len(fcm_token):
            criticallity = instance.criticallity.name

            send_notification(
                fcm_token,
                'New Notification from Shebirth',
                f'Patient {(instance.customer.firstname).capitalize()} criticality level changed to {criticallity}',
                action = "criticallity",
                info_data = info_data
            )
    except Exception as e:
        import sys, os
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


class SalesTeamCalled(models.Model):
    customer = models.ForeignKey(CustomerDetails, on_delete=models.CASCADE,default=None)
