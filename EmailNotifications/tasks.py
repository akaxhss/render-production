# from celery import shared_task
from django.db.models.query import Prefetch    
from EmailNotifications.views import sendMailNotification
from django.conf import settings
import datetime
from datetime import  date, timedelta ,timezone
from Customer.models import LastUpdateDate
from django.db.models import Q
from django.core.mail import send_mail
from Payments.models import Subscriptions
from Accounts.models import CustomerDetails

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from Appointments.models import Appointments
from django.contrib.auth import get_user_model
from Appointments.views import WhatsAppClient, from_number
from Sales.models import Investigation, CriticalityChange
from django.utils.timezone import make_aware
from django.db.models.functions import Concat 
User = get_user_model() 
# from celery.decorators import task

# @task(name="sum_two_numbers")
# def add(x, y):
#     return x + y

# ? task to send mail to clients that havent updated the tracker in 7 days

def NotUpdatedWithin7days(self):
    try:
        time_threshold = datetime.datetime.now().date() - timedelta(days=7)
        diet = Q(diet__date = time_threshold)
        activity = Q(activity__date = time_threshold)
        symptom = Q(symptom__date = time_threshold)
        medicine = Q(medicine__date = time_threshold)
        lastUpdatedPatients = LastUpdateDate.objects.filter(
            diet | activity | symptom | medicine
        ).filter(customer__is_active=True).select_related('customer')
        if lastUpdatedPatients:
            admin = User.objects.filter(admin=True).values_list('email')
            for client in lastUpdatedPatients:
                reciever_email = client.customer.email
                subject = 'Update daily tracker'
                html_content = render_to_string('Emails/Client/DailyTrackerNotUpdated.html', {
                    'title' : subject,
                    "firstname" : client.customer.firstname.capitalize() + " " + client.customer.lastname,
                })
                text_content = strip_tags(html_content)
                email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [reciever_email])
                email.attach_alternative(html_content, "text/html")
                email.send()
                # send whatsApp notification to admin
                whatsAppMessage = "Just reaching out to inform you that there is no update from {clientName} for the past 7 days ,kindly take appropriate actions.\nTo know more :{link}\nThis is a SYSTEM GENERATED MESSAGE".format(
                    clientName=client.customer.firstname.capitalize() + " " + client.customer.lastname,
                    link="link"
                )
                for number in admin:
                    to_number = 'whatsapp:91{number}'.format(number=number)
            # WhatsAppClient.messages.create(from_=from_number,body=whatsAppMessage,to=to_number)


    except Exception as e:
        print(e)

# mails to sales team
# @shared_task
def TrackerNotUpdatedToday():
    time_threshold = make_aware(datetime.datetime.now() - timedelta(days=1))
    diet = Q(diet__year = time_threshold.year) | Q(diet__month = time_threshold.month) | Q(diet__day = time_threshold.day)
    activity = Q(activity__year = time_threshold.year) | Q(activity__month = time_threshold.month) | Q(activity__day = time_threshold.day)
    symptom = Q(symptom__year = time_threshold.year) | Q(symptom__month = time_threshold.month) | Q(symptom__day = time_threshold.day)
    medicine = Q(medicine__year = time_threshold.year) | Q(medicine__month = time_threshold.month) | Q(medicine__day = time_threshold.day)
    lastUpdatedPatients = LastUpdateDate.objects.filter(
        diet | activity | symptom | medicine
    ).filter(customer__is_active=True,customer__is_otp_verified=True).select_related('customer')
    subject = 'Reg-No update'
    for client in lastUpdatedPatients:
        client_id = client.customer.id
        investigation = Investigation.objects.filter(customer=client_id).prefetch_related('sales','sales__user')
        if investigation:
            latest_investigation = investigation.latest('date')
            reciever_email = latest_investigation.sales.user.email
            html_content = render_to_string('Emails/Sales/TrackerNotUpdated.html', {
                'title' : subject,
                "firstname" : client.customer.firstname.capitalize()
            })
            text_content = strip_tags(html_content)
            email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [reciever_email])
            email.attach_alternative(html_content, "text/html")
            email.send()
        # else:
        #     print('no investigations')


# ? task to send mail to clients that are having a plan about to expire

def CurrentPlanExpiry():
    try:
        dateBefore7days = make_aware(datetime.datetime.now() - timedelta(days=7))
        AllSubscriptions = Subscriptions.objects.filter(
            is_active=True, 
            valid_till__year=dateBefore7days.year,
            valid_till__month=dateBefore7days.month,
            valid_till__day=dateBefore7days.day,
        ).select_related('customer')
        sender_email = settings.EMAIL_HOST_USER
        for client in AllSubscriptions:
            reciever_email = client.customer.email
            expiry_date = str(client.valid_till)[0:10]
            message = "Dear {firstname}, \n Your plan of {membership} will expire on {expiry_date}, refresh your subscribtion to enjoy our services.".format(firstname=client.customer.firstname, membership=client.membership.name, expiry_date=expiry_date)
            send_mail('subject', message, sender_email, [reciever_email], fail_silently=True)

    except Exception as e:
        print(e)

# @shared_task
def TrailVersionEnding():
    allSubscriptions = Subscriptions.objects.all()
    customers_ids_with_subscriptions = allSubscriptions.values_list('customer')
    thresholdDate = make_aware(datetime.datetime.now() - timedelta(days=1))
    in_trail_version = CustomerDetails.objects.exclude(user__in=customers_ids_with_subscriptions).filter(
        user__dateJoined__year=thresholdDate.year,
        user__dateJoined__month=thresholdDate.month,
        user__dateJoined__day=thresholdDate.day
    ).select_related('user')
    for client in in_trail_version:
        reciever_email = client.user.email
        subject = 'Your Trial Subscription Ends'
        html_content = render_to_string('Emails/Client/TrailVersionEnds.html', {
            'title' : subject,
            "firstname" : client.user.firstname.capitalize()
        })
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [reciever_email])
        email.attach_alternative(html_content, "text/html")
        email.send()


# @shared_task
def AppointmentRemainder():
    date = datetime.datetime.now().date() + timedelta(days=1)
    appointments = Appointments.objects.filter(date=date, approved=True).select_related('customer', 'customer__user')

    for appointment in appointments:
        # to client
        reciever_email = appointment.customer.user.email
        subject = 'Thank you for choosing SHEBIRTH. Appointment Reminder'
        html_content = render_to_string('Emails/Client/AppointmentRemainder.html', {
            'title' : subject,
            "firstname" : appointment.customer.user.firstname.capitalize(),
            'date' : appointment.date,
            'time' : appointment.time,
        })
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [reciever_email])
        email.attach_alternative(html_content, "text/html")
        email.send()

        # send mail for appointment remaider to doctor
        reciever_email = appointment.doctor.user.email
        subject = 'Appointment Reminder'
        html_content = render_to_string('Emails/Doctor/AppointmentRemainderDoctor.html', {
            'title' : subject,
            "firstname" : appointment.doctor.user.firstname.capitalize(),
            "clientName" : appointment.customer.user.firstname + " " + appointment.customer.user.lastname,
            'time' : appointment.time,
            'date' : appointment.date,
        })
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [reciever_email])
        email.attach_alternative(html_content, "text/html")
        email.send()

        whatsAppMessage = "Dear {docName},\nThis is a friendly reminder that you have a consultation appointment with {clientName}  tomorrow at {time}.".format(
            docName=appointment.doctor.user.firstname.capitalize(),
            clientName=appointment.customer.user.firstname.capitalize(),
            time=appointment.time
        )
        to_number = 'whatsapp:91{}'.format(appointment.doctor.user.mobile)
        # try:
        #     WhatsAppClient.messages.create(from_=from_number,body=whatsAppMessage,to=to_number)
        # except:
        #     pass

# runs every month
# @shared_task
def MonthlyReportForDoctor():
    doctors = User.objects.filter(doctor=True)
    subject = 'Reg- Monthly Report'
    for doctor in doctors:
        html_content = render_to_string('Emails/Client/MonthlyReport.html', {
            'title' : subject,
            "firstname" : doctor.firstname.capitalize()
        })
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [doctor.email])
        email.attach_alternative(html_content, "text/html")
        email.send()

# sends mail to doctor with total number of clients joined this month
# @shared_task
def MonthlyOnBoarding():
    subject = 'User Onboarding' 
    date = datetime.datetime.now()
    doctors = User.objects.filter(doctor=True).prefetch_related(
        Prefetch('docDetails__referal_doc__user',queryset=CustomerDetails.objects.filter(user__dateJoined__month=date.month)),
        'docDetails','docDetails__referal_doc'
    )
    for doctor in doctors:
        doc_details = doctor.docDetails.first() #gets doc details
        clients_count = doc_details.referal_doc.count()
        print(clients_count)
        if clients_count > 0:
            html_content = render_to_string('Emails/Doctor/MonthlyOnBoarding.html', {
                'title' : subject,
                "firstname" : doctor.firstname.capitalize(),
                'count' : clients_count
            })
            text_content = strip_tags(html_content)
            email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [doctor.email])
            email.attach_alternative(html_content, "text/html")
            email.send()


# sends email to sales when subscription ends
# @shared_task
def SubscriptionEnds():
    start_date = make_aware(datetime.datetime.now() - timedelta(hours=1))
    end_date = make_aware(datetime.datetime.now())
    all_active_subscriptions = Subscriptions.objects.filter(is_active=True, valid_till__range=(start_date, end_date)).prefetch_related('customer','membership')
    subject = "Subscription ends"
    for subscription in all_active_subscriptions:
        investigations = Investigation.objects.filter(customer=subscription.customer.id).prefetch_related('sales','sales__user') 
        if investigations:
            latest_investigation = investigations.latest('lastUpdated')
            sales_email = latest_investigation.sales.user.email
            html_content = render_to_string('Emails/Sales/SubscriptionEnds.html', {
                "clientName" : subscription.customer.firstname.capitalize() + " " + subscription.customer.lastname
            })
            text_content = strip_tags(html_content)
            email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [sales_email])
            email.attach_alternative(html_content, "text/html")
            email.send()

#  to sales
# @shared_task
def ClientsUpdatedTracker():
    clients = []
    date = datetime.datetime.now().date()
    tracker_updated_clients = LastUpdateDate.objects.filter(customer__is_active=True).filter(Q(diet__date=date) | Q(medicine__date=date) | Q(activity__date=date) | Q(exercise__date=date) | Q(symptom__date=date)).prefetch_related('customer').annotate(full_name=Concat('customer__firstname', V(' '), 'customer__lastname')).values_list('full_name', flat=True)
    # print(tracker_updated_clients)
    if tracker_updated_clients:
        sales_email = User.objects.filter(sales=True).values_list('email', flat=True)
        # print(sales_email)
        # print(clients)
        html_content = render_to_string('Emails/Sales/TrackerUpdated.html', {
            "clients" : tracker_updated_clients 
        })
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives('Reg-Daily Updates from Clients', text_content, settings.EMAIL_HOST_USER, sales_email)
        email.attach_alternative(html_content, "text/html")
        email.send()



# @shared_task
# ChangedCriticality
def ChangedCriticality():
    changedCriticalities = CriticalityChange.objects.filter(date=datetime.datetime.now()).prefetch_related('customer')
    admin_emails = User.objects.filter(admin=True).values_list('email')
    subject = 'REG-CRITICALITY CHANGE TODAY'
    html_content = render_to_string('Emails/Admin/criticalityChange.html', {
        'clients' : changedCriticalities
    })
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, admin_emails)
    email.attach_alternative(html_content, "text/html")
    email.send()
    

# @shared_task
def Test():
    subject = 'REG-CRITICALITY CHANGE TODAY'
    html_content = render_to_string('Emails/Admin/criticalityChange.html', {
        'clients' : "abc"
    })
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, ["sanathsasi01@gmail.com"])
    email.attach_alternative(html_content, "text/html")
    email.send()

