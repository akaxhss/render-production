from multiprocessing import context
from Accounts.models import CustomerDetails, DoctorDetails
# from django.shortcuts import render

# from Doctor.models import AppointmentSummary
from .serializers import *
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
# from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework_api_key.permissions import HasAPIKey
from django.db.models import Q
from .models import Appointments
from django.conf import settings
from datetime import date, datetime, timedelta
# from django.utils import timezone
from twilio.rest import Client
import jwt
import requests
import json
from time import time 
from django.utils.timezone import make_aware


# for email
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import requests
# razor pay
from Payments.views import client, payment
from Payments.models import AppointmentPayments
account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
WhatsAppClient = Client(account_sid, auth_token)
from_number = 'whatsapp:{}'.format(settings.WHATSAPP_NUMBER)

# zoom meetings details
meetingdetails = {
                    "topic": "Shebirth meeting",
                    "type": 2,
                    "duration": "200",
                    "timezone": "UTC",
                    "agenda": "test", #description
                    "schedule_for" : "sanathsasi01@gmail.com",
                    "settings": {
                        "host_video": "False",	
                        "participant_video": "true",
                        "join_before_host": "True",
                        "jbh_time" : 0,
                        "waiting_room" : "False",
                        "mute_upon_entry": "true",
                        "watermark": "true",
                        "audio": "voip",
                        "auto_recording": "cloud",
                        "approval_type" : 0,
                    }
                }

def generateToken():
    token = jwt.encode({'iss': settings.ZOOM_API_KEY, 'exp': time() + 5000},settings.ZOOM_API_SEC,algorithm='HS256')
    return token.decode("utf-8") #to convert byte to string 

def createMeeting():
    headers = {'authorization': 'Bearer %s' % generateToken(),'content-type': 'application/json'}
    result = requests.post(f'https://api.zoom.us/v2/users/me/meetings',headers=headers, data=json.dumps(meetingdetails))
    # print(result)
    y = json.loads(result.text)
    try:
        meeting_url = y["join_url"]
        # meeting_password = y["password"]
    except:
        meeting_url = False
    return meeting_url

def get_greetings(date):
    if date.hour < 12:
        greetings = 'Good morning'
    elif 12 <= date.hour < 18:
        greetings = 'Good afternoon'
    else:
        greetings = 'Good evening'
    return greetings

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_doctor_price(request):
    user = request.user
    if user.role != User.CLIENT:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
    doctor = user.customer_details.first().referalId
    return Response({
        "status" : True ,
        "data" : {
            "doctor_name" : doctor.user.firstname ,
            "doctor_speciality" : doctor.speciality,
            "doctor_age" : doctor.age,
            "doctor_price" : doctor.price,
            "doctor_qualification" : doctor.qualification,
            "doctor_interests" : doctor.interests,
            "doctor_experience" : doctor.experience,
            "doctor_languages" : doctor.languages,
            "doctor_location" : doctor.location,
            "doctor_gender" : doctor.gender,
        }
    })

@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def appointment_payments(request):
    try:
        keys = ['appointment_id' ,'uid']

        data = request.data

        for key in keys:
            if data.get(key) is None:
                return Response({
                    "status" : False,
                    "message" : f"{key} is required"
                })
                    
        try:
            queryset = Appointments.objects.get(pk = data.get('appointment_id'))   
            queryset.uid = data.get('uid')
            queryset.save()

            return Response({
                "status" : True,
                "data" : {},
                "message" : "payment done"
         })

        except Exception as e:
            print(e)
            return Response({"status": False, "message": "invalid appointment id"})

        



    except Exception as e :
        print(e)
        return Response({
            "status" : False,
            "data" : {},
            "message" : "something went wrong"
        })






@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def customer_booking(request):
    user = request.user
    if user.role == User.CLIENT:
        doctor = request.data.get('doctor', None)
        date = request.data.get('date', None)
        time = request.data.get('time', None)
        # customer = request.data.get('customer', None)
        customer = request.user.id 

        doctor_info = {}
        doctor_price = None
        if doctor is not None:
            try:
                doctor = DoctorDetails.objects.select_related('user').get(user=doctor)
                doctor_price = doctor.price
                doctor_info =   {
                    "doctor_name" : doctor.user.firstname ,
                    "doctor_speciality" : doctor.speciality,
                    "doctor_age" : doctor.age,
                    "doctor_price" : doctor.price,
                    "doctor_qualification" : doctor.qualification,
                    "doctor_interests" : doctor.interests,
                    "doctor_experience" : doctor.experience,
                    "doctor_languages" : doctor.languages,
                    "doctor_location" : doctor.location,
                    "doctor_gender" : doctor.gender,
                }
            except DoctorDetails.DoesNotExist:
                return JsonResponse({"Error" : "doctor does not exists"}, status=status.HTTP_404_NOT_FOUND)
            try:
                customer = CustomerDetails.objects.get(user=request.user.id)
            except User.DoesNotExist:
                return JsonResponse({"Error" : "Customer does not exists"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return JsonResponse({"Error" : "Customer and doctor is required to make an appointment."})

      




        data = request.data.copy()
        data['customer'] = customer.id
        data['doctor'] = doctor.id

        if doctor_price is not None and doctor_price <=0:
            data['is_paid'] = True

        try:
            schedule = datetime.combine(datetime.fromisoformat(date),datetime.strptime(time.replace(" ", ""), '%H:%M').time()) #without pm
        except:
            schedule = datetime.combine(datetime.fromisoformat(date),datetime.strptime(time.replace(" ", ""), '%H:%M%p').time()) #with am and pm
        data['schedule'] = schedule


        #print(user.customer_details)
        


        customer_appointments = Appointments.objects.filter(customer__user = user,meeting_url__isnull = True)
        for ca in customer_appointments:
            

            serializer = BookingSerializer(ca,data=data, context={'request': request}, partial = True)
            
            #print(serializer.data)
            if serializer.is_valid(raise_exception=True):
              
                appointment = serializer.save()
                print(serializer.data)
            
                print(serializer.errors)
            data = serializer.data
            data['doctor_info'] = doctor_info
            return JsonResponse(data)

        serializer = BookingSerializer(data=data, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            appointment = serializer.save()

            data = serializer.data
            data['doctor_info'] = doctor_info
            return JsonResponse(data)
        else:
            return JsonResponse(serializer.errors)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


# getting approved
@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def approve(request):
    user = request.user
    if user.role == User.DOCTOR:
        appointmentID = request.data.get('appointmentID', None)
        if appointmentID is not None:
            try:
                appointment = Appointments.objects.select_related('customer', 'customer__user').get(id=appointmentID)
            except Appointments.DoesNotExist:
                return JsonResponse({"error" : "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
            meeting_url = createMeeting()
            appointment.approved = True
            appointment.rejected = False
            appointment.rescheduled = False
            appointment.meeting_url = meeting_url
            appointment.save()

            # send mail for appointment to client
            reciever_email = appointment.customer.user.email
            subject = 'Thank you for choosing SHEBIRTH. your appointment is confirmed'
            html_content = render_to_string('Emails/Client/NewAppointment.html', {
                'title' : subject,
                "firstname" : appointment.customer.user.firstname.capitalize(),
                'time' : appointment.time,
                'date' : appointment.date,
            })
            text_content = strip_tags(html_content)
            email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [reciever_email])
            email.attach_alternative(html_content, "text/html")
            # email.send()

            # send mail for appointment to doctor
            greetings = get_greetings(datetime.now())
            reciever_email = appointment.doctor.user.email
            subject = 'Appointment Confirmation'
            html_content = render_to_string('Emails/Doctor/AppointmentApproved.html', {
                'title' : subject,
                'greetings' : greetings,
                "firstname" : appointment.doctor.user.firstname.capitalize(),
                "clientName" : appointment.customer.user.firstname + " " + appointment.customer.user.lastname,
                'time' : appointment.time,
                'date' : appointment.date,
            })
            text_content = strip_tags(html_content)
            email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [reciever_email])
            email.attach_alternative(html_content, "text/html")
            # email.send()

            # whatsapp notification to client
            whatsAppMessage = "*Your Appointment is Successfully Scheduled*\n \nDear {client},your appointment with Dr.{doctor} is booked for {date} at {time}. Kindly contact us on {contact}. if you need to reschedule.".format(
                client=appointment.customer.user.firstname.capitalize(),
                doctor= appointment.doctor.user.firstname.capitalize(),
                date=appointment.date,
                time=appointment.time,
                contact='9207283497'
                )
            to_number = 'whatsapp:91{}'.format(appointment.customer.user.mobile)
            # try:
            #     WhatsAppClient.messages.create(from_=from_number,body=whatsAppMessage,to='whatsapp:919207283497')
            # except:
            #     pass 

            # whatsapp notification to doctor
            whatsAppMessage = "Dear {docName},\nYour appointment with {clientName} is scheduled  on {date} at {time}. Kindly contact us on {contact} if you have any queries.".format(
                docName=appointment.doctor.user.firstname.capitalize(),
                clientName=appointment.customer.user.firstname.capitalize(),
                date=appointment.date,
                time=appointment.time,
                contact='9207283497'
            )
            to_number = 'whatsapp:91{}'.format(appointment.doctor.user.mobile)
            # try:
            #     WhatsAppClient.messages.create(from_=from_number,body=whatsAppMessage,to=to_number)
            # except:
            #     pass

        # serializer = BookingSerializer(appointment)

            return JsonResponse({"Success" : "Appointment approved."})
        else:
            return JsonResponse({"Error" : "appointmentID is required"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['PATCH',])
@permission_classes((IsAuthenticated,))
def reschedule(request):
    user = request.user
    if user.role == User.DOCTOR or user.role == User.CLIENT:
        appointmentID = request.data.get('appointmentID', None)
        data = request.data.copy()
        
    # if request.user.patient:
    #     doctor = request.data.get('doctor', None)
    #     data['doctor'] = doctor
    #     if doctor is None:
    #         return JsonResponse({'error' : 'doctor cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
    # elif request.user.doctor:
    #     customer = request.data.get('customer', None)
    #     data['customer'] = customer
    #     if customer is None:
    #         return JsonResponse({'error' : 'customer cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
    # else:
    #     return JsonResponse({'error' : 'user has no permission'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            appointment = Appointments.objects.get(id=appointmentID)
            date = request.data.get('date', str(appointment.date))
            time = request.data.get('time', str(appointment.time))
        except Appointments.DoesNotExist:
            return JsonResponse({"Error" : "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)
        try:
            schedule = datetime.combine(datetime.fromisoformat(date),datetime.strptime(time.replace(" ", ""), '%H:%M').time()) #without pm
        except:
            schedule = datetime.combine(datetime.fromisoformat(date),datetime.strptime(time.replace(" ", ""), '%H:%M%p').time()) #with am and pm
        data['schedule'] = schedule
        data['is_rescheduled'] = True
        serializer = BookingSerializer(appointment ,data=data, partial=True, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            if user.role == User.DOCTOR:
                serializer.save(rescheduled_by_doctor=True)       
                # send mail for appointment to doctor
                reciever_email = appointment.doctor.user.email
                subject = 'Appointment Reschedule'
                html_content = render_to_string('Emails/Doctor/AppointmentRescheduleDoctor.html', {
                    'title' : subject,
                    'greetings' : get_greetings(datetime.now()),
                    "firstname" : appointment.doctor.user.firstname.capitalize(),
                    "clientName" : appointment.customer.user.firstname + " " + appointment.customer.user.lastname,
                    'time' : appointment.time,
                    'date' : appointment.date,
                })
                text_content = strip_tags(html_content)
                email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [reciever_email])
                email.attach_alternative(html_content, "text/html")
                # email.send()
            else:
                serializer.save(rescheduled_by_client=True)
            return JsonResponse(serializer.data)
        else:
            return JsonResponse(serializer.errors)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def reject(request):
    user = request.user
    if user.role == User.DOCTOR or user.role == User.CLIENT:
        appointmentID = request.data.get('appointmentID', None)
        if appointmentID is not None:
            try:
                appointment = Appointments.objects.get(id=appointmentID)
            except Appointments.DoesNotExist:
                return JsonResponse({"error" : "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # payments = AppointmentPayments.objects.filter(appointment=appointmentID,captured=True)
            # if payments:
            #     payment = payments.first()
            #     client.payments.refund(payment.payment_id,{
            #         "amount": payment.amount,
            #         "speed": "optimum"
            #     })

            appointment.rejected = True
            appointment.approved = False
            appointment.rescheduled_by_doctor = False
            appointment.rescheduled_by_client = False
            appointment.save()
            
            
            # serializer = BookingSerializer(appointment)

            return JsonResponse({"Success" : "appointment rejected"})
        else:
            return JsonResponse({"Error" : "appointmentID is required"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def completed(request):
    user = request.user
    if user.role == User.CLIENT:
        dateTimeCompleted = datetime.now() - timedelta(minutes=60)
        try:
            client = user.customer_details.first()
        except:
            return JsonResponse({"error" : "client not found"}, status=status.HTTP_404_NOT_FOUND)
        # dateTime = datetime.now() - timedelta(minutes=30)
        
        completedAppointments = Appointments.objects.filter(is_paid = True ,customer=client.id,approved=True, schedule__lte=make_aware(dateTimeCompleted)).prefetch_related('doctor', 'doctor__user').order_by('-schedule')
        serializer = CompletedSerializer(completedAppointments, many=True, context={'request' : request})
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def upcoming(request):
    user = request.user
    if user.role == User.CLIENT:
        try:
            client = user.customer_details.first()
        except:
            return JsonResponse({"error" : "client not found"}, status=status.HTTP_404_NOT_FOUND)
        timestamp = datetime.now() - timedelta(minutes=15)
        upcoming_appointments = Appointments.objects.filter(is_paid = True ,customer=client.id, approved=True, schedule__gte=make_aware(timestamp)).prefetch_related('doctor', 'doctor__user')
        serializer = UpcomingAppointmentSerializer(upcoming_appointments, many=True, context={'request':request})
    else:
        return Response({'error' : "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)
    return JsonResponse(serializer.data, safe=False)


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def add_summary(request):
    user = request.user
    if user.role == User.DOCTOR:
        a_id = request.data.get('appointmentID', None)
        summary = request.data.get('summary', None)
        if a_id and summary is not None:
            try:
                appointment = Appointments.objects.get(id=a_id)
            except Appointments.DoesNotExist:
                return JsonResponse({'error' : 'appointment not found'}, status=status.HTTP_404_NOT_FOUND)
            instance, created = AppointmentSummary.objects.get_or_create(appointment=appointment)
            instance.summary = summary
            instance.save()
            return JsonResponse({'success' : 'summary added successfuly'})
        else:
            return JsonResponse({'error' : 'appointmentID/summary not provided'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_summary_client(request):
    user = request.user
    if user.role == User.CLIENT:
        a_id = request.query_params.get('appointmentID', None)
        if a_id is not None:
            try:
                appointment = Appointments.objects.prefetch_related('doctor', 'doctor__user').get(id=a_id)
                serializer = SummarySerializerClientSide(appointment, context={'request' : request})
            except Appointments.DoesNotExist:
                return JsonResponse({'error' : 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
            try:
                summary = AppointmentSummary.objects.get(appointment=a_id).summary
            except AppointmentSummary.DoesNotExist:
                summary = ""
            return Response({
                "doctor_details" : serializer.data,
                "summary" : summary
            })
        else:
            return JsonResponse({'error' : 'appointmentID not provided'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_summary_doctor(request):
    user = request.user
    if user.role == User.DOCTOR:
        a_id = request.query_params.get('appointmentID', None)
        if a_id is not None:
            try:
                appointment = Appointments.objects.prefetch_related('customer', 'customer__user').get(id=a_id)
                serializer = SummarySerializerDoctorSide(appointment, context={'request' : request})
            except Appointments.DoesNotExist:
                return JsonResponse({'error' : 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
            try:
                summary = AppointmentSummary.objects.get(appointment=a_id).summary
            except AppointmentSummary.DoesNotExist:
                summary = ""
            return Response({
                "client_details" : serializer.data,
                "summary" : summary
            })
        else:
            return JsonResponse({'error' : 'appointmentID not provided'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


from django.db.models import Q,Case,When, Value, BooleanField


@api_view(['GET',])
# @permission_classes((IsAuthenticated,))
def get_appointments(request):
    try:
        user_id  = request.GET.get('user_id')

        if user_id is None:
                    
            return JsonResponse({
                "status" : False,
                "data" : {},
                "message" : "user_id is required"
            })


        
        customer = user_id
        appointment_objs = Appointments.objects.filter(customer__user__id = customer)

        payload = []

        for appointment_obj in appointment_objs:
            payload.append({
                "id" : appointment_obj.pk,
                "is_paid" : appointment_obj.is_paid,
                "created_at" : appointment_obj.created_at

            })
        
        return JsonResponse({
            "status" : True,
            "data" : payload,
            "message" : "appointment fetched"
        })

    except Exception as e:
        print("E")

    return JsonResponse({'error' : 'something went wrong'}, status=status.HTTP_401_UNAUTHORIZED)
    


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def full_apointments(request):
    user = request.user
    if user.role == User.DOCTOR:
        doctor = user.id
        try:
            doctor = DoctorDetails.objects.get(user=doctor)
        except DoctorDetails.DoesNotExist:
            return JsonResponse({"error" : "doctor not found"}, status=status.HTTP_404_NOT_FOUND)
        
        current_timestamp = make_aware(datetime.now())
        dateTimeCompleted = datetime.now() - timedelta(minutes=60)

        approved = Appointments.objects.filter(doctor=doctor.id ,is_paid = True,approved=True,schedule__gte=current_timestamp - timedelta(minutes=15)).prefetch_related('customer','customer__user').order_by('-schedule').annotate(
            meeting_open=Case(
                    When(schedule__range=[current_timestamp - timedelta(minutes=15), current_timestamp], then=Value(True)),default=Value(False), output_field=BooleanField()
                )
        )
        
        rejected = Appointments.objects.filter(doctor=doctor.id , is_paid = True,rejected=True).prefetch_related('customer','customer__user').order_by('-schedule')
        completed = Appointments.objects.filter(doctor=doctor.id, is_paid = True,approved=True,schedule__lte=make_aware(dateTimeCompleted)).prefetch_related('customer','customer__user').order_by('-schedule')

        ApprovedSerializer = BookingSerializer(approved, many=True, context={'request': request})
        RejectedSerializer = BookingSerializer(rejected, many=True, context={'request': request})
        CompletedSerializer = BookingSerializer(completed, many=True, context={'request': request})

        return JsonResponse({
            # "Reschuduled" : RescheduleSerializer.data,
            "Approved" : ApprovedSerializer.data,
            "Rejected" : RejectedSerializer.data,
            "Completed" : CompletedSerializer.data
        })
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
    

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def client_appointment_payments(request):
    user = request.user
    try:
        client = user.customer_details.first()
    except:
        return JsonResponse({"error" : "client not found"}, status=status.HTTP_404_NOT_FOUND)
    approved_appointments = Appointments.objects.filter(customer=client.id, approved=True).prefetch_related('doctor', 'doctor__user') #filter(customer=user.id).prefetch_related('doctor')
    # print(approved_appointments)
    serializer = ClientAppointmentPaymentSerializer(approved_appointments, many=True)
    return JsonResponse(serializer.data, safe=False)












# from sms import send_sms

def sms():
    pass
    # ? django-sms code
    # sms = send_sms(
    #     'Here is the message',
    #     '+12813771952',
    #     ['+919207283497'],
    #     fail_silently=False
    # )
    # todo twillio code
    # message = client.messages.create(   
    #     messaging_service_sid='MGdfd99210dbe78682144fb3fc3ae5a509',
    #     body='test message',      
    #     to='+919778204439' 
    # ) 
    # print(sms)
    # ? fast2sms code
    # url = "https://www.fast2sms.com/dev/bulk"
    # payload = "sender_id=FSTSMS&message=AppointmentApproved&language=english&route=p&numbers=9778204439"
    # headers = {
    # 'authorization': "52z0V9sE7jIodJvSuZ8Wg6pmF3PwtNQcRhxeGDlabnfrACOkH1sTStGH45hMnfzykDFxuJc0LwKBlpQO",
    # 'Content-Type': "application/x-www-form-urlencoded",
    # 'Cache-Control': "no-cache",
    # }
    # response = requests.request("POST", url, data=payload, headers=headers)
    # print(response.text)
    # ? way2sms
    # url = "https://smsapi.engineeringtgr.com/send/"
    # params = dict(
    #     Mobile='login username',
    #     Password='login password',
    #     Key='generated from above sms api',
    #     Message='Your message Here',
    #     To='recipient')

    # resp = requests.get(url, params)
    # print(resp, resp.text)



 
 
# Dear [Client Name],
# This is a friendly reminder that your appointment with [Dr name] is scheduled for tomorrow at [Time].

 


