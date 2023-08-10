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
                receiver = User.objects.get(id=receiver) # Adding is_active=True condition ,is_active=True
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


##get isactive
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
    recentConsultants = User.objects.filter(role=User.CONSULTANT, id__in=consultants_id, is_active=True)
    remainingConsultants = User.objects.filter(role=User.CONSULTANT, is_active=True).exclude(id__in=consultants_id)
    recent = AllUserSerializer(recentConsultants, many=True, context={'request':request})
    remaining = AllUserSerializer(remainingConsultants, many=True, context={'request':request})
    return Response({'recentChats' : recent.data, 'remainingChats' : remaining.data})


# @api_view(['GET',])
# @permission_classes((IsAuthenticated,))
# def get_all_consultants(request):
#     user = request.user
#     consultants_id = []
#     id = user.id
#     msgs = Messages.objects.filter(Q(sender=id)|Q(receiver=id)).prefetch_related('sender', 'receiver').distinct('sender', 'receiver')
#     for msg in msgs:
#         if msg.sender.role ==  User.CONSULTANT:
#             consultants_id.append(msg.sender.id)
#         else:
#             consultants_id.append(msg.receiver.id)
#     # recentConsultants = User.objects.filter(id__in=consultants_id)
#     recentConsultants = User.objects.filter(role=User.CONSULTANT,id__in=consultants_id)
#     remainingConsultants = User.objects.filter(role=User.CONSULTANT).exclude(id__in=consultants_id)
#     recent = AllUserSerializer(recentConsultants, many=True, context={'request':request})
#     remaining = AllUserSerializer(remainingConsultants, many=True, context={'request':request})
#     return Response({'recentChats' : recent.data, 'remainingChats' : remaining.data})


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

##is active

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def get_all_sales(request):
    user = request.user
    sales_id = []
    id = user.id
    msgs = Messages.objects.filter(Q(sender=id) | Q(receiver=id)).prefetch_related('sender', 'receiver').distinct(
        'sender', 'receiver')

    for msg in msgs:
        if msg.sender.role == User.SALES:
            sales_id.append(msg.sender.id)
        else:
            sales_id.append(msg.receiver.id)

    recentSales = User.objects.filter(role=User.SALES, id__in=sales_id, is_active=True).prefetch_related('salesDetails')
    remainingSales = User.objects.filter(role=User.SALES, is_active=True).exclude(id__in=sales_id).prefetch_related(
        'salesDetails')

    recent = AllUserSerializer(recentSales, many=True, context={'request': request})
    remaining = AllUserSerializer(remainingSales, many=True, context={'request': request})

    return Response({'recentChats': recent.data, 'remainingChats': remaining.data})

# @api_view(['GET',])
# @permission_classes((IsAuthenticated,))
# def get_all_sales(request):
#     user = request.user
#     sales_id = []
#     id = user.id
#     msgs = Messages.objects.filter(Q(sender=id)|Q(receiver=id)).prefetch_related('sender', 'receiver').distinct('sender', 'receiver')
#
#     for msg in msgs:
#         if msg.sender.role == User.SALES:
#             sales_id.append(msg.sender.id)
#         else:
#             sales_id.append(msg.receiver.id)
#
#     recentSales = User.objects.filter(role=User.SALES,id__in=sales_id).prefetch_related('salesDetails')
#     remainingSales = User.objects.filter(role=User.SALES).exclude(id__in=sales_id).prefetch_related('salesDetails')
#
#     recent = AllUserSerializer(recentSales, many=True, context={'request':request})
#     remaining = AllUserSerializer(remainingSales, many=True, context={'request':request})
#
#     return Response({'recentChats' : recent.data, 'remainingChats' : remaining.data})


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_all_clients(request):
    user = request.user
    clients = CustomerDetails.objects.all().prefetch_related("user")
    serializer = AllClientSerializer(clients, many=True, context={'request' : request})
    return JsonResponse(serializer.data, safe=False)



from django.db.models import Max

from django.utils import timezone
from datetime import timedelta
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
            return JsonResponse({"error": "doctor not found"}, status=status.HTTP_404_NOT_FOUND)

        msgs = Messages.objects.filter(Q(sender=id) | Q(receiver=id)).prefetch_related('sender', 'receiver').distinct('sender', 'receiver')
        for msg in msgs:
            if msg.sender.role == User.CLIENT:
                clients_id.append(msg.sender.id)
            else:
                clients_id.append(msg.receiver.id)

        recent_clients = User.objects.filter(role=User.CLIENT, id__in=clients_id, customer_details__referalId=details.id)
        remaining_clients = User.objects.filter(role=User.CLIENT, customer_details__referalId=details.id).exclude(id__in=clients_id)

        recent = AllUserSerializer(recent_clients, many=True, context={'request': request})
        remaining = AllUserSerializer(remaining_clients, many=True, context={'request': request})

        client_messages = (
            Messages.objects.filter(Q(sender=id) | Q(receiver=id))
            .filter(Q(sender__role=User.CLIENT) | Q(receiver__role=User.CLIENT))
            .values('sender', 'receiver')
            .annotate(last_message_time=Max('timestamp'))  # Retrieve the latest message time
        )

        # Collect client IDs from the client_messages queryset
        recent_clients_id = set()
        for msg_info in client_messages:
            sender_id = msg_info['sender']
            receiver_id = msg_info['receiver']
            if sender_id != id and sender_id != user.id:
                recent_clients_id.add(sender_id)
            if receiver_id != id and receiver_id != user.id:
                recent_clients_id.add(receiver_id)

        recent_clients_info = []
        remaining_clients_info = []

        current_time = timezone.now()

        for msg_info in client_messages:
            client_id = msg_info['sender'] if msg_info['sender'] != id else msg_info['receiver']
            last_message_time = msg_info['last_message_time']

            try:
                client = User.objects.get(id=client_id, is_active=True)  # Ensure client is active
            except User.DoesNotExist:
                continue  # Skip this iteration if user doesn't exist or is not active

            serialized_client = AllUserSerializer(client, context={'request': request}).data

            # Include last message time
            time_difference = current_time - last_message_time
            if time_difference < timedelta(days=1):
                formatted_last_message_time = last_message_time.strftime('%Y-%m-%d %I:%M:%S %p')
            else:
                formatted_last_message_time = last_message_time.strftime('%Y-%m-%d')
            serialized_client["last_message_time"] = formatted_last_message_time

            if client_id in recent_clients_id:
                recent_clients_info.append(serialized_client)
            else:
                remaining_clients_info.append(serialized_client)

        for client_info in remaining.data:
            client_id = client_info['id']
            try:
                client = User.objects.get(id=client_id, is_active=True)
            except User.DoesNotExist:
                continue

            serialized_client = AllUserSerializer(client, context={'request': request}).data

            joining_date = client.dateJoined.strftime('%Y-%m-%d') if client.dateJoined else None
            serialized_client["joining_date"] = joining_date

            remaining_clients_info.append(serialized_client)

        return Response({'recentChats': recent_clients_info, 'remainingChats': remaining_clients_info})
    else:
        return JsonResponse({'error': "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)


## this code is working fine as of the 9/aug above code is testing the show date if chat is 24hrs apart
# @api_view(['GET',])
# @permission_classes((IsAuthenticated,))
# def get_all_clients_of_doctor(request):
#     user = request.user
#     if user.role == User.DOCTOR:
#         id = user.id
#         clients_id = []
#         try:
#             details = user.docDetails.first()
#         except DoctorDetails.DoesNotExist:
#             return JsonResponse({"error": "doctor not found"}, status=status.HTTP_404_NOT_FOUND)
#
#         msgs = Messages.objects.filter(Q(sender=id) | Q(receiver=id)).prefetch_related('sender', 'receiver').distinct('sender', 'receiver')
#         for msg in msgs:
#             if msg.sender.role == User.CLIENT:
#                 clients_id.append(msg.sender.id)
#             else:
#                 clients_id.append(msg.receiver.id)
#
#         recent_clients = User.objects.filter(role=User.CLIENT, id__in=clients_id, customer_details__referalId=details.id)
#         remaining_clients = User.objects.filter(role=User.CLIENT, customer_details__referalId=details.id).exclude(id__in=clients_id)
#
#         recent = AllUserSerializer(recent_clients, many=True, context={'request': request})
#         remaining = AllUserSerializer(remaining_clients, many=True, context={'request': request})
#
#         client_messages = (
#             Messages.objects.filter(Q(sender=id) | Q(receiver=id))
#             .filter(Q(sender__role=User.CLIENT) | Q(receiver__role=User.CLIENT))
#             .values('sender', 'receiver')
#             .annotate(last_message_time=Max('timestamp'))  # Retrieve the latest message time
#         )
#
#         # Collect client IDs from the client_messages queryset
#         recent_clients_id = set()
#         for msg_info in client_messages:
#             sender_id = msg_info['sender']
#             receiver_id = msg_info['receiver']
#             if sender_id != id and sender_id != user.id:
#                 recent_clients_id.add(sender_id)
#             if receiver_id != id and receiver_id != user.id:
#                 recent_clients_id.add(receiver_id)
#
#         recent_clients_info = []
#         remaining_clients_info = []
#
#         for msg_info in client_messages:
#             client_id = msg_info['sender'] if msg_info['sender'] != id else msg_info['receiver']
#             last_message_time = msg_info['last_message_time']
#
#             try:
#                 client = User.objects.get(id=client_id, is_active=True)  # Ensure client is active
#             except User.DoesNotExist:
#                 continue  # Skip this iteration if user doesn't exist or is not active
#
#             serialized_client = AllUserSerializer(client, context={'request': request}).data
#
#             # Include last message time
#             formatted_last_message_time = last_message_time.strftime('%Y-%m-%d %H:%M:%S %Z') if last_message_time else None
#             serialized_client["last_message_time"] = formatted_last_message_time
#
#             if client_id in recent_clients_id:
#                 recent_clients_info.append(serialized_client)
#             else:
#                 remaining_clients_info.append(serialized_client)
#
#         return Response({'recentChats': recent_clients_info, 'remainingChats': remaining.data})
#     else:
#         return JsonResponse({'error': "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)


##show this code to vivek

##code is working befroe time issue upper code is new time issue changeing code
# @api_view(['GET',])
# @permission_classes((IsAuthenticated,))
# def get_all_clients_of_doctor(request):
#     user = request.user
#     if user.role == User.DOCTOR:
#         id = user.id
#         clients_id = []
#         try:
#             details = user.docDetails.first()
#         except DoctorDetails.DoesNotExist:
#             return JsonResponse({"error" : "doctor not found"}, status=status.HTTP_404_NOT_FOUND)
#
#         msgs = Messages.objects.filter(Q(sender=id)|Q(receiver=id)).prefetch_related('sender', 'receiver').distinct('sender', 'receiver')
#         for msg in msgs:
#             if msg.sender.role == User.CLIENT:
#                 clients_id.append(msg.sender.id)
#             else:
#                 clients_id.append(msg.receiver.id)
#
#         recent_clients = User.objects.filter(role=User.CLIENT, id__in=clients_id, customer_details__referalId=details.id, is_active=True)
#         remaining_clients = User.objects.filter(role=User.CLIENT, customer_details__referalId=details.id, is_active=True).exclude(id__in=clients_id)
#
#         recent = AllUserSerializer(recent_clients, many=True, context={'request': request})
#         remaining = AllUserSerializer(remaining_clients, many=True, context={'request': request})
#
#         return Response({'recentChats': recent.data, 'remainingChats': remaining.data})
#     else:
#         return JsonResponse({'error': "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)


# @api_view(['GET',])
# @permission_classes((IsAuthenticated,))
# def get_all_clients_of_doctor(request):
#     user = request.user
#     if user.role == User.DOCTOR:
#         id = user.id
#         clients_id = []
#         try:
#             details = user.docDetails.first()
#         except DoctorDetails.DoesNotExist:
#             return JsonResponse({"error" : "doctor not found"}, status=status.HTTP_404_NOT_FOUND)
#
#         msgs = Messages.objects.filter(Q(sender=id)|Q(receiver=id)).prefetch_related('sender', 'receiver').distinct('sender', 'receiver')
#         for msg in msgs:
#             if msg.sender.role == User.CLIENT:
#                 clients_id.append(msg.sender.id)
#             else:
#                 clients_id.append(msg.receiver.id)
#
#         # recentConsultants = User.objects.filter(id__in=consultants_id)
#         recent_clients = User.objects.filter(role=User.CLIENT,id__in=clients_id,customer_details__referalId=details.id)
#         remaining_clients = User.objects.filter(role=User.CLIENT, customer_details__referalId=details.id).exclude(id__in=clients_id)
#
#         recent = AllUserSerializer(recent_clients, many=True, context={'request':request})
#         remaining = AllUserSerializer(remaining_clients, many=True, context={'request':request})
#
#         return Response({'recentChats' : recent.data, 'remainingChats' : remaining.data})
#     else:
#         return JsonResponse({'error' : "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)
#


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def generate_message_notification(request, user_id, user_pic):
    # Here, you can generate the message notification data based on the provided parameters
    # For example, you can construct the JSON payload for the notification
    click_action = "message_screen"
    notification_data = {
        "click_action": click_action,
        "user_id": user_id,
        "user_pic": user_pic,
    }
    return JsonResponse(notification_data)