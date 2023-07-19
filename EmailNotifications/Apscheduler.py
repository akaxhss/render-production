# from apscheduler.schedulers.background import BackgroundScheduler # ? for apscheduler
# from django.conf import settings
# import datetime
# from datetime import  timedelta ,timezone
# from Customer.models import LastUpdateDate
# from django.db.models import Q
# from django.core.mail import send_mail
# from Payments.models import Subscriptions
# sender_email = settings.EMAIL_HOST_USER


# def update_something():
#     # send_mail('Apscheduler testing', 'message', sender_email, ['sanathsasi01@gmail.com'], fail_silently=True)
#     print('runs')


# def NotUpdatedWithin7days():
#     time_threshold = datetime.datetime.now(timezone.utc) - timedelta(days=7)
#     lastUpdatedPatients = LastUpdateDate.objects.filter(Q(diet__lt = time_threshold) | Q(activity__lt = time_threshold) | Q(symptom__lt = time_threshold) | Q(medicine__lt = time_threshold)).filter(customer__is_active=True).select_related('customer')
#     # sender_email = settings.EMAIL_HOST_USER
#     for client in lastUpdatedPatients:
#         reciever_email = client.customer.email
#         send_mail('subject', 'update daily tracker, soon your account will be disabled . ![message]', sender_email, [reciever_email], fail_silently=True)

# def CurrentPlanExpiry():
#     dateBefore7days = datetime.datetime.now(timezone.utc) - timedelta(days=7)
#     AllSubscriptions = Subscriptions.objects.filter(is_active=True, valid_till__lte=dateBefore7days).select_related('customer')
#     for client in AllSubscriptions:
#         reciever_email = client.customer.email
#         message = "Dear {firstname}, \n Your plan of {membership} will expire on {date}, refresh your subscribtion to enjoy our services.".format(firstname=client.customer.firstname, membership=client.membership.name, date=client.valid_till)
#         send_mail('subject', message, sender_email, [reciever_email], fail_silently=True)


# def start():
#     scheduler = BackgroundScheduler()
#     # scheduler.add_job(NotUpdatedWithin7days, 'interval', minutes=1)
#     scheduler.add_job(NotUpdatedWithin7days, 'interval', hours=24)
#     scheduler.add_job(CurrentPlanExpiry, 'interval', hours=23)
#     # scheduler.add_job(update_something, 'interval', seconds=10)
#     scheduler.start()