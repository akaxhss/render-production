from Accounts.models import CustomerDetails, DoctorDetails, hospitalManagerDetails
# from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response
from .models import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from .serializers import DoctorDetailSerializer
from Admin.serializers import totalClientSerializer, DoctorDetailSerializer
from Doctor.serializers import MyPatientSerializers
from django.db.models.query import Prefetch
from Payments.models import Subscriptions
from Sales.models import  Investigation
# from django.db.models import Q
User = get_user_model() 


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def dashboard_details(request):
    user = request.user
    if user.role == User.HOSPITAL_MANAGER:
        hospitalDetails = user.hospitalManagerDetails.first()
        doctors =  DoctorDetails.objects.filter(hospitalManager=hospitalDetails.id).prefetch_related('user', 'hospitalManager')
        doctorSerializer = DoctorDetailSerializer(doctors, many=True, context={'request' : request})
        # ? get ids of every doctor in the queryset and query for the clients with that.
        doctors_ids = doctors.values_list('id')
        clients = CustomerDetails.objects.filter(referalId__in=doctors_ids).prefetch_related('user')
        clients = totalClientSerializer.pre_loader(clients)
        clientSerializer = totalClientSerializer(clients, many=True)
        return JsonResponse({
            "DoctorsCount" : doctors.count(),
            "clientsCount" : clients.count(),
            "clientDetails" : clientSerializer.data,
            'doctorDetails' : doctorSerializer.data
        })        
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def assign_hospital_manager(request):
    user = request.user
    if user.role == User.ADMIN:
        doctor = request.data.get('doctor', None)
        hospitalManager = request.data.get('manager', None)
        try:
            docDetails = DoctorDetails.objects.get(user=doctor)
        except DoctorDetails.DoesNotExist:
            return JsonResponse({"Error" : "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            manager = hospitalManagerDetails.objects.get(user=hospitalManager)
        except hospitalManagerDetails.DoesNotExist:
            return JsonResponse({"Error" : "Manager not found"}, status=status.HTTP_404_NOT_FOUND)

        docDetails.hospitalManager = manager
        docDetails.save()
        return JsonResponse({"Success" : "Successfuly added"})
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def doctors_under_hospital(request):
    user = request.user
    if user.role == User.HOSPITAL_MANAGER:
        try:
            manager_details = user.hospitalManagerDetails.first()
        except hospitalManagerDetails.DoesNotExist:
            return Response({'error' : 'manager details not available'}, status=status.HTTP_404_NOT_FOUND)

        doctors = DoctorDetails.objects.filter(hospitalManager=manager_details.id).prefetch_related('hospitalManager','hospitalManager__user')

        serializer = DoctorDetailSerializer(doctors, many=True, context={"request" : request})
        return Response(serializer.data)

    else:
        return Response({"error" : "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def all_clients(request):
    user = request.user
    if user.role == User.HOSPITAL_MANAGER:
        hospitalDetails = user.hospitalManagerDetails.first()
        doctors_ids =  DoctorDetails.objects.filter(hospitalManager=hospitalDetails.id).values_list('id')
        clients = CustomerDetails.objects.filter(referalId__in=doctors_ids).prefetch_related('user')
        clients = totalClientSerializer.pre_loader(clients)
        clientSerializer = totalClientSerializer(clients, many=True)
        return Response(clientSerializer.data)        
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def clients_under_doctors(request):
    user = request.user
    if user.role == User.HOSPITAL_MANAGER:
        threshold_date = datetime.now().date() - timedelta(days=294) #42 weeks
        doctor_id = request.query_params.get('doctor_id', None)
        if doctor_id is not None:
            try:
                doctorDetailsID = DoctorDetails.objects.get(user=doctor_id).id
            except User.DoesNotExist:
                return JsonResponse({"Error" : "Doctor not found"})

            Patients = CustomerDetails.objects.filter(referalId=doctorDetailsID,Menstruation_date__gte=threshold_date).prefetch_related(
                'user',
                # Prefetch('user__criticality_change', queryset=CriticalityChange.objects.order_by('-date')),
                Prefetch('user__client_investigation', queryset=Investigation.objects.filter(criticallity__isnull=False).order_by('-date'))
                )
            serializer = MyPatientSerializers(Patients, many=True)
            return Response(serializer.data)
        else:
            return Response({"Error" : "pass doctor_id in params"})
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def clients_with_no_subscription(request):
    user = request.user
    if user.role == User.HOSPITAL_MANAGER:
        hospitalDetails = user.hospitalManagerDetails.first()
        date = datetime.now().date()
        threshold_date = date - timedelta(days=294) #42 weeks
        # get all users with subscription
        users_with_subs = Subscriptions.objects.filter(is_active=True).values_list('customer')
        doctors_ids =  DoctorDetails.objects.filter(hospitalManager=hospitalDetails.id).values_list('id')
        clientDetails = CustomerDetails.objects.filter(user__is_verified=True,Menstruation_date__gte=threshold_date,referalId__in=doctors_ids).exclude(user__id__in=users_with_subs)
        clientDetails = totalClientSerializer.pre_loader(clientDetails)
        serializer = totalClientSerializer(clientDetails, many=True)
        return Response(serializer.data)
    else:
        return Response({'error' : "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)