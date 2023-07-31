# from datetime import date,datetime

from django.conf import settings
from django.shortcuts import render
from .serializers import *
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework_api_key.permissions import HasAPIKey
# from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from .models import *
from django.core import exceptions
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model, password_validation as password_validators
from django.conf import settings
from django.utils import timezone
from Payments.models import PurchasedMembership
# from rest_framework.decorators import parser_classes
import requests
import json
# verify email
from django_email_verification import send_email

User = get_user_model()


# from Appointments.views import from_number, WhatsAppClient


def landingPage(request):
    return render(request, 'landingpage.html')


@api_view(['POST'])
# @parser_classes([FormParser,MultiPartParser])
# @permission_classes((HasAPIKey,))
@permission_classes((AllowAny,))
def registration(request):
    context = {}
    # to find the user type
    patient = request.data.get('patient', False)
    doctor = request.data.get('doctor', False)
    sales = request.data.get('sales', False)
    consultant = request.data.get('consultant', False)
    hospitalManager = request.data.get('hospitalManager', False)
    password = request.data.get('password', None)
    password2 = request.data.get('password2', None)

    userSerializer = RegistrationSerializers(data=request.data, context={'request': request})
    if patient:
        # check if an account with this email exists that is not otp verified.
        client = User.objects.filter(email=request.data.get('email', None), is_verified=False)
        if client:
            client.delete()

        referalId = request.data.get('referalId', None)
        if referalId is not None:
            try:
                doctorDetails = DoctorDetails.objects.get(referalId=referalId)
            except DoctorDetails.DoesNotExist:
                return JsonResponse({"Invalid referalId": "Doctor with the given Icmr does not exists"},
                                    status=status.HTTP_404_NOT_FOUND)
        else:
            return JsonResponse({"referalId": "referalId cannot be blank"}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['referalId'] = doctorDetails.id
        details = CustomerDetailsSerializer(data=data)
    elif doctor:
        details = DoctorRegSerializer(data=request.data)
    elif sales:
        data = request.data.copy()
        data['passwordString'] = request.data.get('password', None)
        details = SalesTeamSerializer(data=data)
    elif consultant:
        data = request.data.copy()
        data['passwordString'] = request.data.get('password', None)
        details = ConsultantInfoSerializer(data=data)
    elif hospitalManager:
        data = request.data.copy()
        data['passwordString'] = request.data.get('password', None)
        details = HospitalDetailSerializer(data=data)
    else:
        return JsonResponse({"Error": "Specify the type of user"}, status=status.HTTP_400_BAD_REQUEST)

    # validations
    userSerializerValidation = userSerializer.is_valid(raise_exception=True)
    detailSerializerValidation = details.is_valid(raise_exception=True)
    PasswordErrors = dict()
    try:
        password_validators.validate_password(password=userSerializer.initial_data['password'], user=User)
    except exceptions.ValidationError as e:
        PasswordErrors.update({'password': list(e.messages)})
    if not sales and not consultant and not hospitalManager and password != password2:
        PasswordErrors.update({'password': 'Passwords does not match.'})

    if userSerializerValidation and detailSerializerValidation and not PasswordErrors:
        user = userSerializer.save()
        if user is not None:
            fcm_token = request.data.get('fcm_token', None)
            if fcm_token:
                user.fcm_token = fcm_token
                user.save()
            details.save(user=user)
            context['otpId'] = user.id
            context['user'] = userSerializer.data
            context['details'] = details.data
            if user.role == User.DOCTOR:
                # send email on confirmation/creation of account
                subject = 'Account confirmation'
                html_content = render_to_string('Emails/Doctor/AccountConfirmation.html', {
                    'title': subject,
                    "firstname": user.firstname.capitalize()
                })
                text_content = strip_tags(html_content)
                email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [user.email])
                email.attach_alternative(html_content, "text/html")
                # email.send()
                # whatsAppMessage = "Just reaching out to inform you that {drName} is waiting for his account verification to join shebirth family,kindly take appropriate actions.\nTo know more :{link}\nThis is a SYSTEM GENERATED MESSAGE".format(
                #     drName=user.firstname.capitalize() + " " + user.lastname,
                #     link="link"
                # )
                # admin_numbers = User.objects.filter(admin=True,mobile__isnull=False).values_list('mobile')
                # for number in admin_numbers:
                #     number = 'whatsapp:91{number}'.format(number=doctor.mobile)
                #     WhatsAppClient.messages.create(from_=from_number,body=whatsAppMessage,to=number)
            return JsonResponse(context, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse({'error': userSerializer.errors})
    else:
        context = userSerializer.errors
        context.update(details.errors)
        context.update(PasswordErrors)
        return JsonResponse(context, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((HasAPIKey,))
def client_registration(request):
    context = {}
    password = request.data.get('password', None)
    password2 = request.data.get('password2', None)
    data = request.data.copy()
    data['role'] = User.CLIENT

    # Check if an account with this email exists that is not otp verified.
    client = User.objects.filter(email=request.data.get('email', None), is_verified=False)
    if client:
        client.delete()

    referalId = request.data.get('referalId', None)
    if referalId:
        try:
            doctorDetails = DoctorDetails.objects.get(referalId=referalId)
            data['referalId'] = doctorDetails.id
        except DoctorDetails.DoesNotExist:
            # If the doctor with the provided referalId doesn't exist, set referalId to None
            data['referalId'] = None
    else:
        data['referalId'] = None

    userSerializer = RegistrationSerializers(data=data, context={'request': request})
    details = CustomerDetailsSerializer(data=data)

    # Validations
    userSerializerValidation = userSerializer.is_valid(raise_exception=True)
    detailSerializerValidation = details.is_valid(raise_exception=True)
    PasswordErrors = dict()
    try:
        password_validators.validate_password(password=userSerializer.initial_data['password'], user=User)
    except exceptions.ValidationError as e:
        PasswordErrors.update({'password': list(e.messages)})
    if password != password2:
        PasswordErrors.update({'password': 'Passwords do not match.'})

    if userSerializerValidation and detailSerializerValidation and not PasswordErrors:
        user = userSerializer.save()
        fcm_token = request.data.get('fcm_token', None)
        if fcm_token:
            user.fcm_token = fcm_token
            user.save()
        details.save(user=user)
        context['otpId'] = user.id
        context['success'] = "Successfully registered"
        return JsonResponse(context, status=status.HTTP_201_CREATED)
    else:
        context = userSerializer.errors
        context.update(details.errors)
        context.update(PasswordErrors)
        return JsonResponse(context, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((HasAPIKey,))
def doctor_registration(request):
    context = {}
    password = request.data.get('password', None)
    password2 = request.data.get('password2', None)
    data = request.data.copy()
    data['role'] = User.DOCTOR
    userSerializer = RegistrationSerializers(data=data, context={"request": request})
    details = DoctorRegSerializer(data=request.data)

    # validations
    userSerializerValidation = userSerializer.is_valid(raise_exception=True)
    detailSerializerValidation = details.is_valid(raise_exception=True)
    PasswordErrors = dict()
    try:
        password_validators.validate_password(password=userSerializer.initial_data['password'], user=User)
    except exceptions.ValidationError as e:
        PasswordErrors.update({'password': list(e.messages)})
    if password != password2:
        PasswordErrors.update({'password': 'Passwords does not match.'})

    # save
    if userSerializerValidation and detailSerializerValidation and not PasswordErrors:
        user = userSerializer.save()
        details.save(user=user)
        context['otpId'] = user.id
        context['success'] = "Successfuly registered"
        subject = 'Account confirmation'
        html_content = render_to_string('Emails/Doctor/AccountConfirmation.html', {
            'title': subject,
            "firstname": user.firstname.capitalize()
        })
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [user.email])
        email.attach_alternative(html_content, "text/html")
        # email.send()
        # whatsAppMessage = "Just reaching out to inform you that {drName} is waiting for his account verification to join shebirth family,kindly take appropriate actions.\nTo know more :{link}\nThis is a SYSTEM GENERATED MESSAGE".format(
        #     drName=user.firstname.capitalize() + " " + user.lastname,
        #     link="link"
        # )
        # admin_numbers = User.objects.filter(admin=True,mobile__isnull=False).values_list('mobile')
        # for number in admin_numbers:
        #     number = 'whatsapp:91{number}'.format(number=doctor.mobile)
        #     WhatsAppClient.messages.create(from_=from_number,body=whatsAppMessage,to=number)
        return JsonResponse(context, status=status.HTTP_201_CREATED)
    else:
        context = userSerializer.errors
        context.update(details.errors)
        context.update(PasswordErrors)
        return JsonResponse(context, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def sales_registration(request):
    context = {}
    password = request.data.get('password', None)
    password2 = request.data.get('password2', None)

    data = request.data.copy()
    data['role'] = User.SALES

    userSerializer = RegistrationSerializers(data=data, context={"request": request})
    details = SalesTeamSerializer(data=request.data)

    data['passwordString'] = request.data.get('password', None)
    details = SalesTeamSerializer(data=data)

    # validations
    userSerializerValidation = userSerializer.is_valid(raise_exception=True)
    detailSerializerValidation = details.is_valid(raise_exception=True)
    PasswordErrors = dict()
    try:
        password_validators.validate_password(password=userSerializer.initial_data['password'], user=User)
    except exceptions.ValidationError as e:
        PasswordErrors.update({'password': list(e.messages)})

    if userSerializerValidation and detailSerializerValidation and not PasswordErrors:
        user = userSerializer.save()
        detials = details.save(user=user)
        context['success'] = "successfuly registered"
        return JsonResponse(context, status=status.HTTP_201_CREATED)
    else:
        context = userSerializer.errors
        context.update(details.errors)
        context.update(PasswordErrors)
        return JsonResponse(context, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def consultant_registration(request):
    context = {}
    password = request.data.get('password', None)
    password2 = request.data.get('password2', None)

    data = request.data.copy()
    data['role'] = User.CONSULTANT

    userSerializer = RegistrationSerializers(data=data, context={"request": request})
    details = ConsultantInfoSerializer(data=request.data)

    data['passwordString'] = request.data.get('password', None)
    details = ConsultantInfoSerializer(data=data)

    # validations
    userSerializerValidation = userSerializer.is_valid(raise_exception=True)
    detailSerializerValidation = details.is_valid(raise_exception=True)
    PasswordErrors = dict()
    try:
        password_validators.validate_password(password=userSerializer.initial_data['password'], user=User)
    except exceptions.ValidationError as e:
        PasswordErrors.update({'password': list(e.messages)})

    if userSerializerValidation and detailSerializerValidation and not PasswordErrors:
        user = userSerializer.save()
        detials = details.save(user=user)
        context['success'] = "successfuly registered"
        return JsonResponse(context, status=status.HTTP_201_CREATED)
    else:
        context = userSerializer.errors
        context.update(details.errors)
        context.update(PasswordErrors)
        return JsonResponse(context, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def hostpital_registration(request):
    context = {}
    # password = request.data.get('password', None)
    # password2 = request.data.get('password2', None)

    data = request.data.copy()
    data['role'] = User.HOSPITAL_MANAGER
    data['passwordString'] = request.data.get('password', None)

    registration_serializer = RegistrationSerializers(data=data, context={"request": request})
    details = HospitalDetailSerializer(data=data)

    # validations
    userSerializerValidation = registration_serializer.is_valid(raise_exception=True)
    detailSerializerValidation = details.is_valid(raise_exception=True)

    PasswordErrors = dict()
    try:
        password_validators.validate_password(password=registration_serializer.initial_data['password'], user=User)
    except exceptions.ValidationError as e:
        PasswordErrors.update({'password': list(e.messages)})

    if userSerializerValidation and detailSerializerValidation and not PasswordErrors:
        user = registration_serializer.save()
        detials = details.save(user=user)
        context['success'] = "successfuly registered"
        return JsonResponse(context, status=status.HTTP_201_CREATED)
    else:
        context = registration_serializer.errors
        context.update(details.errors)
        context.update(PasswordErrors)
        return JsonResponse(context, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
# @permission_classes((HasAPIKey,))
@permission_classes((AllowAny,))
def login_view(request):
    serializer = LoginSerializer(data=request.data)

    fcm_token = None
    data = request.data
    print(data)
    if data.get('fcm_token'):
        fcm_token = fcm_token

    if serializer.is_valid(raise_exception=True):
        user = serializer.validated_data['user']
        print(user.id)
        print(serializer.validated_data['fcm_token'])
        user_obj = User.objects.get(pk=user.id)
        try:
            FirebaseFcm.objects.create(user=user_obj, fcm_token=serializer.validated_data['fcm_token'])
        except Exception as e:
            print(e)
        # user_obj.fcm_token = serializer.validated_data['fcm_token']
        # print(user_obj)
    else:
        return JsonResponse(serializer.errors)

    token, created = Token.objects.get_or_create(user=user)

    user_obj.save()

    # Different users
    if user.role == User.CLIENT:
        try:
            print(user.id)
            Subscription = PurchasedMembership.objects.filter(user__id=user.id, is_paid=True).order_by('-pk')
            # if Subscription:
            has_subscription = True
            subscription_package = Subscription[0].membership.membership_name
        except Exception as e:
            has_subscription = False
            subscription_package = ""
        context = {
            'token': token.key,
            'client': True,
            'id': user.id,
            'has_subscription': has_subscription,
            'subscription_package': subscription_package
        }

        return JsonResponse(context, status=status.HTTP_200_OK)
    elif user.role == User.DOCTOR:
        context = {
            'token': token.key,
            'doctor': True,
            'doctorId': user.id,
            'fcm_token': user_obj.fcm_token
        }
        return JsonResponse(context, status=status.HTTP_200_OK)
    elif user.role == User.SALES:
        return JsonResponse({
            "id": user.id,
            'token': token.key,
            'sales': True,
            'fcm_token': user_obj.fcm_token

        })
    elif user.role == User.ADMIN:
        return JsonResponse({
            "id": user.id,
            'token': token.key,
            'admin': True,
            'fcm_token': user_obj.fcm_token

        })
    elif user.role == User.CONSULTANT:
        return JsonResponse({
            "id": user.id,
            'token': token.key,
            "consltant": True,
            'fcm_token': user_obj.fcm_token

        })

    elif user.role == User.DAD:
        return JsonResponse({
            "id": user.id,
            'token': token.key,
            "dad": True,
            'fcm_token': user_obj.fcm_token

        })
    else:  # user.hospitalManager
        return JsonResponse({
            "id": user.id,
            'token': token.key,
            "hospitalManager": True,
            'fcm_token': user_obj.fcm_token

        })


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
# @authentication_classes([TokenAuthentication])
def logout_view(request):
    customer = request.user.id
    if customer is not None:
        try:
            token = Token.objects.get(user=customer)
            token.delete()
            return JsonResponse({'message': 'User logged out successfully'})
        except Token.DoesNotExist:
            return JsonResponse({'message': 'User already logged out'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({"Error": "User customer not provided"}, status=status.HTTP_400_BAD_REQUEST)


# Customer Update Functions
@api_view(['PATCH'])
@permission_classes((IsAuthenticated,))
def update_profile(request):
    # cid = request.data.get('customer', None)
    user = request.user
    user_id = user.id

    if user.role == User.ADMIN or user.role == User.SALES:
        data = request.data
        if data.get('customer_id') is None:
            return JsonResponse({"error": "customer_id is required."}, status=status.HTTP_404_NOT_FOUND)
        else:
            user_id = data.get('customer_id')
            try:
                details = CustomerDetails.objects.get(user__id=user_id)
                print(details)
            except CustomerDetails.DoesNotExist:
                return JsonResponse({"error": "Customer details not found."}, status=status.HTTP_404_NOT_FOUND)
            detailSerializer = CustomerDetailsSerializer(details, data=request.data, partial=True)
            if detailSerializer.is_valid():
                detailSerializer.save()
                return JsonResponse({
                    "success": "update successfull",
                    "details": detailSerializer.data,
                })
            else:
                return JsonResponse({
                    "details": detailSerializer.errors,
                })

    print(user.role)
    if True:
        # password = request.data.get('password', None)
        if user_id is not None:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            if user.role == User.CLIENT:
                try:
                    details = CustomerDetails.objects.get(user=user_id)
                except CustomerDetails.DoesNotExist:
                    return JsonResponse({"error": "Customer details not found."}, status=status.HTTP_404_NOT_FOUND)
                detailSerializer = CustomerDetailsSerializer(details, data=request.data, partial=True)

            elif user.role == User.DOCTOR:
                try:
                    details = DoctorDetails.objects.get(user=user_id)
                except DoctorDetails.DoesNotExist:
                    return JsonResponse({"error": "Doctor details not found."}, status=status.HTTP_404_NOT_FOUND)
                detailSerializer = DocDetailSerializer(details, data=request.data, partial=True,
                                                       context={'request': request})
            else:
                return JsonResponse({'error': 'only doctor and client have profile update feature'},
                                    status=status.HTTP_403_FORBIDDEN)
            customerSerializer = UpdateSerializer(user, data=request.data, partial=True)
        else:
            return JsonResponse({"Error": "Customer id or email empty"}, status=status.HTTP_400_BAD_REQUEST)
        user_validation = customerSerializer.is_valid(raise_exception=True)
        details_validation = detailSerializer.is_valid(raise_exception=True)

        if user_validation and details_validation:
            user = customerSerializer.save()
            detailSerializer.save(user=user)

            return JsonResponse({
                "success": "update successfull",
                "user": customerSerializer.data,
                "details": detailSerializer.data,
            })

        else:
            return JsonResponse({
                "customer": customerSerializer.errors,
                "details": detailSerializer.errors,
            })
    else:
        return JsonResponse({'error': 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def activate_or_deactivate(request):
    user = request.user
    if user.role == User.ADMIN or user.role == User.HOSPITAL_MANAGER:
        userID = request.data.get('id', None)
        if userID is not None:
            try:
                user = User.objects.get(id=userID)
            except User.DoesNotExist:
                return JsonResponse({"Error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            Token.objects.filter(user=user).delete()
            user.is_active = not user.is_active
            user.save()
            if user.is_active:
                state = "Activated"
            else:
                state = "Deactivated"
            return JsonResponse({"Success": "Account " + state})
        else:
            return JsonResponse({"Error": "id not provided"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error': 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def customer_profile(request):
    user = request.user
    if not user.role == User.HOSPITAL_MANAGER and not user.role == User.DOCTOR:
        if user.role == User.CLIENT:
            cid = user.id
        else:
            cid = request.query_params.get('customer', None)
        if cid is not None:
            try:
                customer = User.objects.get(id=cid)
            except User.DoesNotExist:
                return JsonResponse({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

            try:
                details = CustomerDetails.objects.get(user=cid)
            except CustomerDetails.DoesNotExist:
                return JsonResponse({"error": "Customer details not found."}, status=status.HTTP_404_NOT_FOUND)

            customer = RegistrationSerializers(customer, context={'request': request})
            details = CustomerDetailsSerializer(details)

            context = {
                "customer": customer.data,
                "details": details.data
            }

            return JsonResponse(context, status=status.HTTP_200_OK)
        else:
            return JsonResponse({"Error": "Customer is None"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error': 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes((AllowAny,))
def email_verification(request):
    email = request.data.get('email', None)
    client = User.objects.filter(email=email).first()
    send_email(client)
    return JsonResponse({'success': "verification email is send"})


@api_view(['POST'])
@permission_classes((AllowAny,))
def otp_verification(request):
    id = request.data.get('otp_id', None)
    entered_otp = request.data.get('otp', None)
    try:
        saved_otp = Otp.objects.get(client=id)
    except:
        return JsonResponse({'error': "Account not found"}, status=status.HTTP_404_NOT_FOUND)

    if saved_otp.otp == int(entered_otp):

        if saved_otp.validity > timezone.now():
            client = User.objects.get(id=id)
            client.is_verified = True
            client.save()
            # # send email on confirmation/creation of account
            subject = 'Account confirmation / start of trial subscription'
            html_content = render_to_string('Emails/Client/ClientAccountConfirmation.html', {
                'title': subject,
                "firstname": client.firstname.capitalize()
            })
            text_content = strip_tags(html_content)
            email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [client.email])
            email.attach_alternative(html_content, "text/html")
            email.send()

            # send whatsapp notification to client
            # whatsAppMessage = "Congrats,\nJust reaching out to inform you that {clientName} has been registered under you.".format(
            #     clientName=client.firstname.capitalize() + " " + client.lastname,
            # )
            # customerDetails = client.customer_details.first()
            # to_number = 'whatsapp:91{number}'.format(number=customerDetails.referalId.user.mobile)
            # WhatsAppClient.messages.create(from_=from_number,body=whatsAppMessage,to=to_number)

            # # whatsapp notification to admin
            # whatsAppMessage = "Just reaching out to inform you that {clientName} has been registered under shebirth.\nTo know more :{link}\nThis is a SYSTEM GENERATED MESSAGE".format(
            #     clientName=client.firstname.capitalize() + " " + client.lastname,
            #     link="link"
            # )
            # admin_numbers = User.objects.filter(admin=True,mobile__isnull=False).values_list('mobile')
            # for number in admin_numbers:
            #     to_number = 'whatsapp:91{number}'.format(number=number)
            #     WhatsAppClient.messages.create(from_=from_number,body=whatsAppMessage,to=to_number)
            return JsonResponse({'success': "Otp verified"})
        else:
            return JsonResponse({'error': 'otp expired'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return JsonResponse({'error': 'wrong otp'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def user_data(request):
    user = request.user
    # try:
    #     instance = User.objects.get(id=user.id)
    # except User.DoesNotExist:
    #     return JsonResponse({'error' : 'user not found'}, status=status.HTTP_404_NOT_FOUND)
    context = {
        'firstname': user.firstname,
        'lastname': user.lastname,
        'email': user.email
    }
    if user.role == User.DOCTOR:
        try:
            instance = user.docDetails.first()
        except DoctorDetails.DoesNotExist:
            return JsonResponse({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        doctor_gender = instance.gender
        gender = doctor_gender if doctor_gender is not None else ""
        # if gender is not None:
        #     context['gender'] = gender
        context['gender'] = gender
    return JsonResponse(context)


@api_view(['PATCH'])
@permission_classes((IsAuthenticated,))
def password_change(request):
    user = request.user
    if user.role == User.CLIENT or user.role == User.DOCTOR:
        password = request.data.get('password', None)
        PasswordErrors = dict()
        if password is not None:
            try:
                password_validators.validate_password(password=password, user=User)
            except exceptions.ValidationError as e:
                PasswordErrors['password'] = list(e.messages)
                return JsonResponse(PasswordErrors, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(password)
            user.save()
            return JsonResponse({'success': 'password changed successfully'})
    else:
        return JsonResponse({'error', 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


# forgot password section
def reset_password(request):
    token = request.GET.get('token', '')
    context = {
        'token': token,
        'passwordsMatch': True
    }
    return render(request, 'forgot_password/reset.html', context)


# from django.contrib import messages
def set_password(request):
    token = request.POST.get('token')
    password = request.POST.get('password')
    password2 = request.POST.get('password2')
    reset_endpoint = request.build_absolute_uri().replace('/password-reset/', '/api/password_reset/confirm/')
    data = {
        'password': password,
        'token': token
    }
    headers = {'content-type': 'application/json'}
    if password == password2:
        try:
            result = requests.post(reset_endpoint, headers=headers, data=json.dumps(data))
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)
        json_result = json.loads(result.text)
        context = {
            'token': token,
            'result': json_result,
            'passwordsMatch': True
        }
        return render(request, 'forgot_password/reset.html', context)
    else:
        context = {
            'token': token,
            'passwordsMatch': False
        }
        return render(request, 'forgot_password/reset.html', context)


@api_view(['PATCH'])
@permission_classes((AllowAny,))
def change_roles(request):
    # patient to client
    User.objects.filter(patient=True).update(role=User.CLIENT, patient=False)
    # sales
    User.objects.filter(sales=True).update(role=User.SALES, sales=False)
    # admin
    User.objects.filter(admin=True).update(role=User.ADMIN, admin=False)
    # consultant
    User.objects.filter(consultant=True).update(role=User.CONSULTANT, consultant=False)
    # doctor
    User.objects.filter(doctor=True).update(role=User.DOCTOR, doctor=False)

    # hospital_manager
    User.objects.filter(hospitalManager=True).update(role=User.HOSPITAL_MANAGER, hospitalManager=False)


@api_view(['POST'])
@permission_classes((AllowAny,))
def dad_registration(request):
    try:
        data = request.data
        serializer = DadRegisterSerializer(data=data)

        if serializer.is_valid():
            validated_data = (serializer.validated_data)
            user = User.objects.filter(email=validated_data['email'])

            if user.exists():
                return JsonResponse({'status': False, 'message': 'Account with this email already exists'})
            wife_email = User.objects.filter(email=validated_data['wife_email'])

            if not wife_email.exists():
                return JsonResponse({'status': False, 'message': 'Invalid Wife Email'})
            serializer.save()
            return JsonResponse({'status': True, 'message': 'Dad registration successfull'})
        return JsonResponse({'status': False, 'message': serializer.errors})
    except Exception as e:
        print(e)
        import sys, os
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return JsonResponse({'status': False, 'message': 'Something went wrong'})


from Customer.models import *
from Customer.serializer import *


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def dad_dashboard(request):
    try:

        from datetime import date, timedelta, datetime

        if request.user.role != 7:
            return JsonResponse({'status': False, 'messagge': 'only dad can access'})

        user = request.user
        details = User.objects.get(email=user.dad_details.first().wife_email)

        serializer = DadSerializer(user.dad_details.first())
        context = {}
        context['data'] = serializer.data

        print(details)
        periods_date = details.customer_details.first().Menstruation_date
        today = date.today()

        daysPregnant = today - periods_date
        week = int(daysPregnant.days / 7)
        # daysCompleted = (daysPregnant.days % 365) % 7
        daysCompleted = daysPregnant.days % 7

        week = 0 if week < 0 else week
        daysLeft = 280 - daysPregnant.days

        daysLeft = 0 if daysLeft < 0 else daysLeft

        symptoms_data = PositiveSymptoms.objects.filter(customer=details, positive=True).prefetch_related(
            'symptom').order_by('-date')
        symptoms_serializer = PositiveSymptomsSerializer(symptoms_data, many=True)

        data_with_input = SymptomsInput.objects.filter(customer=details).order_by('-date')
        data_with_input_serializer = SymptomsInputDisplaySerializer(data_with_input, many=True)

        custom_symptoms_data = PositiveCustomSymptoms.objects.filter(symptom__customer=details,
                                                                     positive=True).prefetch_related(
            'symptom').order_by('-date')
        custom_symptoms_serializer = PositiveSymptomDisplaySerializer(custom_symptoms_data, many=True)

        context['symptom_input'] = data_with_input_serializer.data
        context['postive_symptoms'] = symptoms_serializer.data
        context['postive_custom_symptoms'] = custom_symptoms_serializer.data

        print(week)
        context['babyDetails'] = {}
        video = VideoLink.objects.all()
        video_serializer = VideoLinkSerializer(video, many=True)
        context['video'] = video_serializer.data
        try:
            babyDetail = BabyPics.objects.get(week=week)
            babydetails = BabyDetailSerializer(babyDetail, context={"request": request})
            context['babyDetails'] = babydetails.data

        except Exception as e:
            print(e)

        banners = Banner.objects.all()
        banner_serializer = BannerSerializer(banners, many=True)
        context['banners'] = banner_serializer.data

        return JsonResponse({'status': True, 'details': context})

    except Exception as e:
        print(e)

        return JsonResponse({'status': False, 'details': {}})


from rest_framework.views import APIView
from rest_framework.response import Response


class BannerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            banners = Banner.objects.all()
            serializer = BannerSerializer(banners, many=True)
            return Response({
                'status': True,
                'data': serializer.data
            })
        except Exception as e:
            return JsonResponse({'status': False, 'details': {}})

    def post(self, request):
        try:
            data = request.data
            serializer = BannerSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': True,
                    'data': serializer.data
                })
            return JsonResponse({'status': False, 'details': serializer.errors})

        except Exception as e:
            print(e)
            return JsonResponse({'status': False, 'details': {}})

    def delete(self, request):
        try:
            data = request.data
            if not data.get('id'):
                return JsonResponse({'status': False, 'message': 'id is required', 'details': {}})

            try:
                banner = Banner.objects.get(id=data.get('id')).delete()
                return Response({
                    'status': True,
                    'data': ""
                })
            except Exception as e:
                return JsonResponse({'status': False, 'message': 'invalid id ', 'details': {}})


        except Exception as e:
            return JsonResponse({'status': False, 'details': {}})


class VideoLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            video = VideoLink.objects.all()
            serializer = VideoLinkSerializer(video, many=True)
            return Response({
                'status': True,
                'data': serializer.data
            })
        except Exception as e:
            return JsonResponse({'status': False, 'details': {}})

    def post(self, request):
        try:
            data = request.data
            serializer = VideoLinkSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': True,
                    'data': serializer.data
                })
            return JsonResponse({'status': False, 'details': serializer.errors})

        except Exception as e:
            print(e)
            return JsonResponse({'status': False, 'details': {}})

    def patch(self, request):
        try:
            data = request.data

            id = data.get('id')
            if id is None:
                return JsonResponse({'status': False, 'details': 'id is required'})

            print('####')
            print(id)
            print('####')

            for v in VideoLink.objects.all():
                print(v.id)

            print(VideoLink.objects.all())
            print('@@@@@')
            obj = VideoLink.objects.get(id=id)
            serializer = VideoLinkSerializer(obj, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': True,
                    'data': serializer.data
                })
            return JsonResponse({'status': False, 'details': serializer.errors})

        except Exception as e:
            print(e)
            return JsonResponse({'status': False, 'details': {}})

    def delete(self, request):
        try:
            data = request.data
            if not data.get('id'):
                return JsonResponse({'status': False, 'message': 'id is required', 'details': {}})

            try:
                video = VideoLink.objects.get(id=data.get('id')).delete()
                return Response({
                    'status': True,
                    'data': ""
                })
            except Exception as e:
                return JsonResponse({'status': False, 'message': 'invalid id ', 'details': {}})


        except Exception as e:
            return JsonResponse({'status': False, 'details': {}})


class SymptomRemedyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        objs = SymptomsRemedy.objects.all()

        if request.GET.get('search'):
            search = request.GET.get('search')
            search = search.split(',')
            objs = objs.filter(id__in=search)
            # print(type(search))

        serializer = SymptomsRemedySerializer(objs, many=True)
        return JsonResponse({'status': True, 'data': serializer.data})


class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        if data.get('fcm_token') is None:
            return Response({
                "status": False,
                "message": "key fcm_token missing",
                "data": {}
            })

        FirebaseFcm.objects.filter(fcm_token=data.get('fcm_token')).delete()

        return JsonResponse({'status': True, 'data': {}, "message": "Fcm token removed"})
