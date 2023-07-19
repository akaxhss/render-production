
from django.db.models.fields import BooleanField
from django.db.models.query import Prefetch
from Appointments.models import Appointments
from Accounts.models import CustomerDetails, DoctorDetails
from .serializers import *
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated #, AllowAny
from rest_framework.response import Response
# from rest_framework_api_key.permissions import HasAPIKey
from Sales.serializers import RequestApprovalSerializer
from Accounts.serializers import RegistrationSerializers, CustomerDetailsSerializer 
# from Sales.models import Investigation, PatientDetailsApporval
from Customer.serializer import MedicalDetails
import datetime
from django.db.models import Q
from Appointments.serializers import TodaysAppointmentSerializer
from Appointments.serializers import BookingSerializer
from Admin.serializers import DoctorDetailSerializer , NewDoctorSerializer
from Appointments.serializers import AppointmentSerializer

from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.db.models import Q, Count,Case,When, Value, BooleanField
from django.utils.timezone import make_aware

# import datetime


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def doctor_filter(request):
    user = request.user
    if user.role == User.CLIENT or user.role == User.DOCTOR:
        speciality = request.query_params.get('speciality', None)
        id = request.query_params.get('id', None)
        if speciality is not None:
            doctors = DoctorDetails.objects.filter(user__is_active=True, user__role=User.DOCTOR, speciality__icontains=speciality).prefetch_related('user')
            serializer = DoctorDetailSerializer(doctors, many=True, context={'request' : request})
        elif id is not None:
            doctors = DoctorDetails.objects.filter(user__is_active=True, user__role=User.DOCTOR, user__id=id).prefetch_related('user')
            serializer = DoctorDetailSerializer(doctors, many=True, context={'request' : request})
        else:
            return Response({'error' : "provide filter property"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
    

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_doctors(request):
    doctors = DoctorDetails.objects.filter(user__is_active=True, user__role=User.DOCTOR).prefetch_related('user')
    serializer = DoctorDetailSerializer(doctors, many=True, context={'request' : request})
    return Response({
        'status' : True,
        'data' : serializer.data,
        'message' : 'doctors fetched'
    })


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_doctor_appointments(request ,id):
    try:
        doctor = DoctorDetails.objects.get(user__id = id)
        queryset = Appointments.objects.filter(doctor = doctor,completed = True)
        print(queryset)
        serializer = NewDoctorSerializer(doctor,context={
            'request' : request,
            'sort_by' : request.GET.get('sort_by' ,'asc'),
            'search' : request.GET.get('search' , None)
            
            })
        return Response({
            'status' : True,
            'data' : serializer.data,
            'message' : 'doctors fetched'
        })
    except Exception as e:
        print(e)
        return Response({
            'status' : False,
            'data' : {},
            'message' : 'invalid doctor id'
        })



@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def my_patients(request):
    user = request.user
    if user.role == User.DOCTOR:
        threshold_date = datetime.datetime.now().date() - timedelta(days=294) #42 weeks
        if user is not None:
            try:
                doctorDetailsID = user.docDetails.first().id
            except User.DoesNotExist:
                return JsonResponse({"Error" : "Doctor not found"})

            Patients = CustomerDetails.objects.filter(referalId=doctorDetailsID,Menstruation_date__gte=threshold_date, user__is_active=True).prefetch_related(
                'user',
                Prefetch('user__criticality_change', queryset=CriticalityChange.objects.order_by('-date','-criticallity__criticality'))
                )
            serializer = MyPatientSerializers(Patients, many=True, context={'request' : request})
            return JsonResponse({"customers" : serializer.data})
        else:
            return JsonResponse({"Error" : "Doctor Does not exists"})
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def request_patient_details(request):
    user = request.user
    if user.role == User.DOCTOR:
        customer = request.data.get('customer', None)
        # doctor = request.data.get('doctor', None) 
        doctor = user.id   

        if customer and doctor is not None:
            data = request.data.copy()

            try:
                customerDetail = CustomerDetails.objects.get(user=customer)
            except CustomerDetails.DoesNotExist:
                return JsonResponse({"Error" : "Customer not found."})

            try:
                docDetails = DoctorDetails.objects.get(user=doctor)
            except DoctorDetails.DoesNotExist:
                return JsonResponse({"Error" : "Doctor not found."})

            data['customer'] = customerDetail.id
            data['doctor'] = docDetails.id

            request = RequestApprovalSerializer(data=data)

            if request.is_valid(raise_exception=True):
                request.save()
                return JsonResponse({"Success" : "Request Send."})
        else:
            return JsonResponse({"Error" : "doctor/customer field is None"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def patient_details(request):
    user = request.user
    if user.role == User.DOCTOR:
        is_approved = False
        customer = request.query_params.get('customer', None)
        # try:
        #     doctorDetail = user.docDetails.get(user=user.id)
        # except DoctorDetails.DoesNotExist:
        #     return JsonResponse({"Error" : "doctor does not exist"}, status=status.HTTP_404_NOT_FOUND)

        #commented to prevent reqeust to display detials
        # try:
        #     request = PatientDetailsApporval.objects.get(doctor=doctorDetail.id)
        #     is_approved = request.is_approved
        # except PatientDetailsApporval.DoesNotExist:
        #     is_approved = False

        is_approved = True  # added so that detials will be always display without request.
        # Get requested client details
        try:
            customer = User.objects.get(id=customer)
        except User.DoesNotExist:
            return JsonResponse({"error" : "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            details = CustomerDetails.objects.get(user=customer)
        except CustomerDetails.DoesNotExist:
            return JsonResponse({"error" : "Customer details not found."}, status=status.HTTP_404_NOT_FOUND)

        if is_approved:
            customer = RegistrationSerializers(customer, context={'request':request})
            details = CustomerDetailsSerializer(details)
            context = {
                "is_approved" : True,
                "customer" : customer.data,
                "details" : details.data
            }
        else:
            details = MedicalDetails(details)
            context = {
                "is_approved" : False,
                "detials" : details.data
            }

        return JsonResponse(context, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def doctor_profile(request):
    user = request.user
    if user.role == User.DOCTOR:
        id = user.id
    else:
        id = request.query_params.get('doctor', None)
    if not user.role == User.CONSULTANT:
        if id is not None:
            try:
                profile = DoctorDetails.objects.select_related('user').get(user=id)
            except DoctorDetails.DoesNotExist:
                return JsonResponse({"Error" : "Invalid id"}, status=status.HTTP_404_NOT_FOUND)
            serializer = DoctorProfileSerialzer(profile, context={'request': request})
            return JsonResponse(serializer.data)
        else:
            return JsonResponse({"Error" : "id not provided,if not doctor send via query_params"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def all_appointments(request):
    id = request.query_params.get('id', None)
    if id is not None:
        try:
            docDetails = DoctorDetails.objects.get(user=id)
        except DoctorDetails.DoesNotExist:
            return JsonResponse({"Error" : "Doctor detials not found"}, status=status.HTTP_404_NOT_FOUND) 

        Allappointments = Appointments.objects.filter(doctor=docDetails.id)
        upcoming = Allappointments.filter(approved=True)
        completed = Allappointments.filter(completed=True)

        upcomingSerializer = AppointmentSerializer(upcoming, many=True)
        completedSerializer = AppointmentSerializer(completed, many=True)

        context = {
            "upcoming" : upcomingSerializer.data,
            "completed" : completedSerializer.data
        }    
        return JsonResponse(context)

    else:
        return JsonResponse({"Error" : "Id not provided"})


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def approval_requests(request):
    # doctor = request.query_params.get('doctor', None)
    user = request.user
    dateTime = make_aware(datetime.datetime.now())
    if user.role == User.DOCTOR:
        try:
            doctorDetails = user.docDetails.first()
        except DoctorDetails.DoesNotExist:
            return JsonResponse({"Error" : "consultant not found"}, status=status.HTTP_404_NOT_FOUND)

        data = Appointments.objects.filter(approved=False,rejected=False, doctor=doctorDetails.id, schedule__gte=dateTime)
        needs_approval = BookingSerializer(data, many=True, context={'request':request})
        return Response(needs_approval.data)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def clients_this_month(request):
    # doctor = request.user.id
    user = request.user
    if user.role == User.DOCTOR:
        threshold_date = datetime.datetime.now().date() - timedelta(days=294) #42 weeks
        DocDetails = user.docDetails.first()
        totalCustomers = CustomerDetails.objects.filter(referalId=DocDetails.id,Menstruation_date__gte=threshold_date, user__is_active=True)
        currentDate =  datetime.datetime.today()
        currentMonth = currentDate.month
        customers_thisMonth = totalCustomers.filter(user__dateJoined__month=currentMonth).prefetch_related('user')

        serializer = ClientThisMonthSerializers(customers_thisMonth, many=True, context={'request' : request})

        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def todays_appointments(request):
    user = request.user
    if user.role == User.DOCTOR:
        currentDate =  make_aware(datetime.datetime.now())
        todaysAppointments = Appointments.objects.filter(doctor=user.docDetails.first().id,approved=True, schedule__date=currentDate.date()).prefetch_related('customer', 'customer__user').order_by('-schedule').annotate(
            meeting_open=Case(
                    When(schedule__range=[currentDate, currentDate - timedelta(minutes=15)], then=Value(True)),default=Value(False), output_field=BooleanField()
                )
        )
        serializer = TodaysAppointmentSerializer(todaysAppointments,many=True)
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def doctor_dashboard_details(request):
    user = request.user
    if user.role == User.DOCTOR:
        if id is not None:
            try:
                details = user.docDetails.first()
            except User.DoesNotExist:
                return JsonResponse({"Error" : "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)
            
            threshold_date = datetime.datetime.now().date() - timedelta(days=294) #42 weeks
            totalCustomers = CustomerDetails.objects.filter(referalId=details.id, Menstruation_date__gte=threshold_date, user__is_active=True)
            
            # total patient count
            totalCount = totalCustomers.count()

            # patients in the current month
            date_threshold =  make_aware(datetime.datetime.now() - timedelta(minutes=15))
            approvalTime = make_aware(datetime.datetime.now())

            currentMonth = date_threshold.month
            customers_thisMonth = totalCustomers.filter(user__dateJoined__month=currentMonth).count()

            needsApproval = Appointments.objects.filter(doctor=details.id, approved=False,rejected=False, schedule__gte=approvalTime).count()

            todaysAppointments = Appointments.objects.filter(doctor=details.id, approved=True, schedule__date=date_threshold.date())

            consultationData = todaysAppointments.filter(schedule__gte=date_threshold).prefetch_related('customer').order_by('time').prefetch_related('customer','customer__user')[:2]
            
            todaysAppointmentsCount = todaysAppointments.count() 

            consultation = TodaysAppointmentSerializer(consultationData, many=True)
            
            graphData = Appointments.objects.filter(doctor=details.id, date__year=date_threshold.year).annotate(month=TruncMonth('date')).values('month').annotate(appointments=Count('id')).annotate(cancelled=Count('id', filter=Q(rejected=True))).values('month', 'appointments','cancelled').order_by('month')

            GdSerializer = GraphDataSerializer(graphData, many=True)
            profile_pic = user.profile_img
            print(profile_pic)
            # return "https://" + str(get_current_site(request)) + "/media/" + str(obj.profile_img)
            # else:
            #     return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")
            context = {
                'doctorId' : user.id,
                'approvalRequests' : needsApproval,
                'todaysAppointmentsCount' : todaysAppointmentsCount,
                'profile_pic' : "https://" + str(get_current_site(request)) + "/media/" + str(profile_pic) if profile_pic is not None else "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg"),
                'totalClients' : totalCount,
                'clientsThisMonth' : customers_thisMonth,
                'graphData' : GdSerializer.data,
                'latestConsultation' : consultation.data
            }
            return Response(context, status=status.HTTP_200_OK)
        else:
            return Response({"Error" : "Id not provided"})
    return Response({'error' : "no permission"}, status=status.HTTP_401_UNAUTHORIZED)

