from os import stat
from Accounts.models import CustomerDetails, DoctorDetails
from .models import *
from .serializers import *
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q
User = get_user_model()

# Create your views here.
@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def send_message(request):
    user = request.user
    if not user.role == User.ADMIN and not user.role == User.HOSPITAL_MANAGER:
        data = request.data.copy()
        data['sender'] = user
        receiver = request.data.get('receiver', None)
        message = request.data.get('message', None)
        try:
            receiver = User.objects.get(id=receiver)
        except User.DoesNotExist:
            return Response({'error' : 'Reciever not found'}, status=status.HTTP_404_NOT_FOUND)
        if message is not None:
            stripSpaces = message.replace(" ",'')
            if len(stripSpaces) != 0:
                Messages.objects.create(sender=user, receiver=receiver,message=message)
                return Response({'success' : 'message sent'})
        return Response({'error' : 'Empty message'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_all_messages(request):
    user = request.user
    if not user.role == User.ADMIN and not user.role == User.HOSPITAL_MANAGER:
        receiverDetails = {}
        receiver = request.query_params.get('receiver', None)
        if receiver is not None:
            try:
                receiver = User.objects.get(id=receiver)
                receiverDetails['id'] =  receiver.id
                receiverDetails['image_url'] = "https://" + str(get_current_site(request)) + "/media/" + str(receiver.profile_img)
                receiverDetails['name'] = receiver.firstname + " " + receiver.lastname if receiver.lastname is not None else receiver.firstname
                if receiver.role ==  User.DOCTOR:
                    details = receiver.docDetails.first()
                    receiverDetails['speciality'] = details.speciality
            except User.DoesNotExist:
                return Response({'error' : 'Reciever not found'}, status=status.HTTP_404_NOT_FOUND)

            messages = Messages.objects.filter(Q(sender=user.id)|Q(sender=receiver.id),Q(receiver=user.id)|Q(receiver=receiver.id)).prefetch_related('receiver','sender')
            serializer = AllMessageSerializer(messages, many=True)
            return Response({'messages' : serializer.data, 'receiverDetails' : receiverDetails})
        else:
            return Response({"error" : "Receiver empty"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_all_consultants(request):
    user = request.user
    consultants_id = []
    id = user.id
    msgs = Messages.objects.filter(Q(sender=id)|Q(receiver=id)).prefetch_related('sender', 'receiver').distinct('sender', 'receiver')
    for msg in msgs:
        if msg.sender.role ==  User.CONSULTANT:
            consultants_id.append(msg.sender.id)
        else:
            consultants_id.append(msg.receiver.id)
    # recentConsultants = User.objects.filter(id__in=consultants_id)
    recentConsultants = User.objects.filter(role=User.CONSULTANT,id__in=consultants_id)   
    remainingConsultants = User.objects.filter(role=User.CONSULTANT).exclude(id__in=consultants_id)        
    recent = AllUserSerializer(recentConsultants, many=True, context={'request':request})
    remaining = AllUserSerializer(remainingConsultants, many=True, context={'request':request})
    return Response({'recentChats' : recent.data, 'remainingChats' : remaining.data})


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_clients_doctor(request):
    user = request.user
    # doctors_id = []
    if user.role == User.CLIENT:
        details = user.customer_details.first()
        try:
            doctor = DoctorDetails.objects.prefetch_related('user').get(id=details.referalId.id)
        except DoctorDetails.DoesNotExist:
            return JsonResponse({'error' : 'doctor not found'}, status=status.HTTP_404_NOT_FOUND)
        firstname = doctor.user.firstname
        lastname = doctor.user.lastname
        id = doctor.user.id
        speciality = doctor.speciality
        image_url = "https://" + str(get_current_site(request)) + "/media/" + str(doctor.user.profile_img)
        return JsonResponse({
            'id' : id,
            'firstname' : firstname,
            'lastname' : lastname,
            'speciality' : speciality,
            'image_url' : image_url
        })       
    else:
        return Response({'error' : "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_all_sales(request):
    user = request.user
    sales_id = []
    id = user.id
    msgs = Messages.objects.filter(Q(sender=id)|Q(receiver=id)).prefetch_related('sender', 'receiver').distinct('sender', 'receiver')

    for msg in msgs:
        if msg.sender.role == User.SALES:
            sales_id.append(msg.sender.id)
        else:
            sales_id.append(msg.receiver.id)
        
    recentSales = User.objects.filter(role=User.SALES,id__in=sales_id).prefetch_related('salesDetails')
    remainingSales = User.objects.filter(role=User.SALES).exclude(id__in=sales_id).prefetch_related('salesDetails')  

    recent = AllUserSerializer(recentSales, many=True, context={'request':request})
    remaining = AllUserSerializer(remainingSales, many=True, context={'request':request})

    return Response({'recentChats' : recent.data, 'remainingChats' : remaining.data})


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_all_clients(request):
    user = request.user
    clients = CustomerDetails.objects.all().prefetch_related("user")
    serializer = AllClientSerializer(clients, many=True, context={'request' : request})
    return JsonResponse(serializer.data, safe=False)



@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_all_clients_of_doctor(request):
    user = request.user
    if user.role == User.DOCTOR:
        id = user.id
        clients_id = []
        try:
            details = user.docDetails.first()
        except DoctorDetails.DoesNotExist:
            return JsonResponse({"error" : "doctor not found"}, status=status.HTTP_404_NOT_FOUND)

        msgs = Messages.objects.filter(Q(sender=id)|Q(receiver=id)).prefetch_related('sender', 'receiver').distinct('sender', 'receiver')
        for msg in msgs:
            if msg.sender.role == User.CLIENT:
                clients_id.append(msg.sender.id)
            else:
                clients_id.append(msg.receiver.id)

        # recentConsultants = User.objects.filter(id__in=consultants_id)
        recent_clients = User.objects.filter(role=User.CLIENT,id__in=clients_id,customer_details__referalId=details.id)   
        remaining_clients = User.objects.filter(role=User.CLIENT, customer_details__referalId=details.id).exclude(id__in=clients_id)   

        recent = AllUserSerializer(recent_clients, many=True, context={'request':request})
        remaining = AllUserSerializer(remaining_clients, many=True, context={'request':request})

        return Response({'recentChats' : recent.data, 'remainingChats' : remaining.data})
    else:
        return JsonResponse({'error' : "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)