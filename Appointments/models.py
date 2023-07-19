from django.db import models
from Accounts.models import CustomerDetails, DoctorDetails
from datetime import datetime
# Create your models here.


class Appointments(models.Model):
    doctor = models.ForeignKey(DoctorDetails, on_delete=models.CASCADE, null=True)
    customer = models.ForeignKey(CustomerDetails, on_delete=models.CASCADE , related_name="customer_appointments")
    date = models.DateField()
    time = models.TimeField()
    schedule = models.DateTimeField(default=datetime.now)
    approved = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    rescheduled_by_doctor = models.BooleanField(default=False)
    rescheduled_by_client = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    meeting_url = models.URLField(null=True)
    is_rescheduled = models.BooleanField(default=False)

    is_paid = models.BooleanField(default=False)
    uid = models.CharField(max_length=100 , null=True , blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # class Meta:
    #     unique_together = ['date', 'customer', 'doctor', 'approved']


    def __str__(self):
        return self.customer.user.firstname


class AppointmentSummary(models.Model):
    appointment = models.ForeignKey(Appointments, on_delete=models.CASCADE)
    summary = models.TextField()



from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from Accounts.helper import send_notification

@receiver(post_save, sender=Appointments)
def appointment_changes(sender, instance, **kwargs):
    print("HELLO")
    try:
        info_data = {
            "notification_type" : "appointment",
            "customer_id" : instance.customer.user.id ,
            "doctor_id" : instance.doctor.user.id,
            "appointment_id" : instance.id,
        }
        if instance.id is None:
            fcm_tokens_for_doctor = instance.doctor.user.fcm_tokens.all()
            if fcm_tokens_for_doctor.exists():
                fcm_token = [f.fcm_token for f in fcm_tokens_for_doctor]
                print(fcm_token)
                send_notification(
                    fcm_token,
                    'New Notification from Shebirth',
                    f'Hello {(instance.doctor.user.firstname).capitalize()} a New Appointment has been scheduled',
                    action = "appointment",
                    info_data =info_data
                
                )
        else:

            fcm_tokens_for_customer = instance.customer.user.fcm_tokens.all()
            fcm_token = [f.fcm_token for f in fcm_tokens_for_customer]

            if instance.is_rescheduled:

                fcm_tokens_for_customer = instance.customer.user.fcm_tokens.all()
                fcm_token = [f.fcm_token for f in fcm_tokens_for_customer]

                customer_name = instance.customer.user.firstname
                doctor_name = instance.doctor.user.firstname

                instance.is_rescheduled = False
                instance.approved = True
                

                reschuled_by = "Doctor"
                if instance.rescheduled_by_client:
                    fcm_tokens_for_doctor = instance.doctor.user.fcm_tokens.all()
                    if fcm_tokens_for_doctor.exists():
                        fcm_token = [f.fcm_token for f in fcm_tokens_for_doctor]
                    
                    instance.approved = False
                    instance.rescheduled_by_client = False
                    reschuled_by = "Client"
               
               
                instance.rescheduled_by_client = False
                instance.rescheduled_by_doctor = False
                instance.save()

                if reschuled_by == "Client":
                    send_notification(
                        fcm_token,
                        'New Notification from Shebirth',
                        f'Hello {doctor_name.capitalize()} an Appointment has been re-scheduled {reschuled_by} - with name {customer_name.capitalize()}',
                        action = "appointment",
                        info_data =info_data

                    )
                else:
                    send_notification(
                        fcm_token,
                        'New Notification from Shebirth',
                        f'Hello {customer_name.capitalize()} an Appointment has been re-scheduled {reschuled_by} - with name {doctor_name.capitalize()}',
                        action = "appointment",
                        info_data =info_data
                    )


            elif instance.approved and fcm_tokens_for_customer.exists():
                send_notification(
                    fcm_token,
                    'New Notification from Shebirth',
                    f'Hello {(instance.customer.user.firstname).capitalize()} your appointment has been approved!',
                    action = "appointment",
                    info_data =info_data
                )






    except Exception as e:
        print(e)
