# from __future__ import absolute_import, unicode_literals  
# import os  
# from celery import Celery  
# from celery.schedules import crontab  

# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags
# from django.conf import settings
  
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Shebirth.settings')  
# # celery settings
# app = Celery('Shebirth')  
# app.config_from_object('django.conf:settings', namespace='CELERY')  

# @app.task
# def testing_function():
#     subject = 'REG-CRITICALITY CHANGE TODAY'
#     html_content = render_to_string('Emails/Admin/criticalityChange.html', {
#         'clients' : "abc"
#     })
#     text_content = strip_tags(html_content)
#     email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, ["sanathsasi01@gmail.com"])
#     email.attach_alternative(html_content, "text/html")
#     email.send()

# app.conf.beat_schedule = {  
    # 'NotUpdatedWithin7days': {  
    #     'task': 'EmailNotifications.tasks.NotUpdatedWithin7days',  
    #     'schedule': crontab(hour=14, minute='00'),  #hour=14, minute='00'
    # }, 
    # 'CurrentPlanExpiry' : {
    #     'task': 'EmailNotifications.tasks.CurrentPlanExpiry',  
    #     'schedule': crontab(hour=22, minute='00'), 
    # },
    # 'TrailVersionEnding' : {
    #     'task': 'EmailNotifications.tasks.TrailVersionEnding',  
    #     'schedule': crontab(hour=21, minute='00'), 
    # },
    # 'AppointmentRemainder' : {
    #     'task': 'EmailNotifications.tasks.AppointmentRemainder',  
    #     'schedule': crontab(hour=20, minute='00'),
    #     # 'schedule': 10,
    # },
    # 'MonthlyReportForDoctor' : {
    #     'task': 'EmailNotifications.tasks.MonthlyReportForDoctor',  
    #     'schedule': crontab(0, 0, day_of_month='1'),
    # },
    # 'MonthlyOnBoarding' : {
    #     'task': 'EmailNotifications.tasks.MonthlyOnBoarding',  
    #     'schedule': crontab(0, 0, day_of_month='28'),
    # },
    # 'SubscriptionEnds' : {
    #     'task': 'EmailNotifications.tasks.SubscriptionEnds',  
    #     'schedule': crontab(minute=0, hour='*/1'),
    # },
    # "ChangedCriticality" : {
    #     'task' : 'EmailNotifications.tasks.ChangedCriticality',
    #     'schedule': crontab(hour=18, minute='00'),
    # } 
# }  

# app.conf.timezone = 'Asia/Kolkata'  
# app.autodiscover_tasks() 

