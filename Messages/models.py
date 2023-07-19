from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from Accounts.helper import send_notification

User = get_user_model()
# Create your models here.


class Messages(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Receiver")
    message = models.CharField(max_length=800)

    

@receiver(post_save, sender=Messages)
def appointment_changes(sender, instance, **kwargs):
    try:
        info_data = {
            "notification_type" : "message",
            "sender_id" : instance.sender.id ,
            "receiver_id" : instance.receiver.id,
            "message_id" : instance.id,
        }

        fcm_tokens = instance.receiver.fcm_tokens.all()
        if fcm_tokens.exists():
            fcm_token = [f.fcm_token for f in fcm_tokens]
            print(fcm_token)
            send_notification(
                fcm_token,
                'A new message recieved',
                f'You received  a new message from {(instance.sender.firstname).capitalize()}',
                action = "messages",
                info_data = info_data
            )

    except Exception as e:
        print(e)