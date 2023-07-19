from django.shortcuts import render
# Create your views here.
from django.core.mail import send_mail
from django.conf import settings
# import datetime
# from datetime import  timedelta, timezone
# from Customer.models import LastUpdateDate
# from django.db.models import Q
# for email
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def sendMail(request):
    subject = "test subject"
    message = "Welcome to shebirth"
    sender = settings.EMAIL_HOST_USER
    reciever = "sanathsasi01@gmail.com"
    sendMailNotification(subject, message, sender, reciever)


def sendMailNotification(subject, message, sender, reciever):
    send = send_mail(subject, message, sender, [reciever], fail_silently=True)


def email(subject, message):
    html_content = render_to_string('Emails/test.html', {
        'title' : subject,
        "content" : message
    })
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, ['sanathsasi01@gmail.com'])
    email.attach_alternative(html_content, "text/html")
    email.send()


