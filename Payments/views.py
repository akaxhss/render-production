from os import stat
from django.shortcuts import render
from rest_framework import status
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
# from django.http import HttpResponseNotFound
from Accounts.models import DoctorDetails
from rest_framework.permissions import IsAuthenticated, AllowAny
import razorpay
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.response import Response
# from django.views.decorators.csrf import  csrf_exempt
from .models import *
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from Accounts.models import CustomerDetails
from Appointments.serializers import BookingSerializer
from django.conf import settings
from requests.auth import HTTPBasicAuth
import requests
import json
# for email
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags
User = get_user_model()
import hmac
import hashlib
from rest_framework.views import APIView


client = razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_API_ID))


# @csrf_exempt
@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def checkout(request):
    user = request.user
    if user.role == User.CLIENT or user.role == User.HOSPITAL_MANAGER:
        # if user.role == User.HOSPITAL_MANAGER:
        #     try:
        #         user = User.objects.get(id=)
        razorpay_payment_id = request.data.get('razorpay_payment_id', None)
        razorpay_subscription_id = request.data.get('razorpay_subscription_id', None) #razorpay_subscription_id
        razorpay_signature = request.data.get('razorpay_signature', None)
    
        if razorpay_payment_id and razorpay_subscription_id and razorpay_signature is not None:
            try:
                payment = Payments.objects.select_related('customer').get(sub_Id=razorpay_subscription_id)
                payment.paymentId = razorpay_payment_id
                payment.signature = razorpay_signature
                payment.save()
            except Payments.DoesNotExist:
                return JsonResponse({"error" : "Payment not found."}, status=status.HTTP_404_NOT_FOUND)

            generated_signature =  hmac.new(bytes(settings.RAZOR_API_ID, encoding='utf-8') , (razorpay_payment_id + "|" + payment.sub_Id).encode('utf-8'), hashlib.sha256).hexdigest()

            if generated_signature == razorpay_signature:
                payment.captured = True
                payment.save()
                # create a new subscription in api db
                try:
                    membership = MembershipPlans.objects.filter(amount=payment.amount).first()
                except:
                    return JsonResponse({"error" : "selected plan not found"}, status=status.HTTP_404_NOT_FOUND)
            
                # ! make the current active plan to inactive
                Subscriptions.objects.filter(customer=payment.customer,is_active=True).update(is_active=False)

                # ? new subscription
                validity = datetime.now() + timedelta(days=membership.validity) #days=payment.membership.validity
                Subscriptions.objects.create(customer=payment.customer, valid_till=make_aware(validity), membership=membership,is_active=True) 

                # ? send email for successfull purachase
                # reciever_email = payment.email
                # if payment.membership.membership.name.lower() == 'basic':
                #     subject = 'Thank you for starting your Basic Subscription'
                #     html_content = render_to_string('Emails/Client/BasicSubscription.html', {
                #         'title' : subject,
                #         "firstname" :payment.firstname.capitalize()
                #     })
                # else: #payment.membership.membership.name.lower() == 'standard'
                #     subject = 'Thank you for starting your Premium Subscription'
                #     html_content = render_to_string('Emails/Client/StandardSubscription.html', {
                #         'title' : subject,
                #         "firstname" : payment.firstname.capitalize()
                #     })
                # text_content = strip_tags(html_content)
                # email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [reciever_email])
                # email.attach_alternative(html_content, "text/html")
                # email.send()

                # make is_active false after successfull payment
                payment.customer.is_active=False
                payment.customer.save()
                # render success page on successful caputre of payment
                return JsonResponse({"success" : "Payment captured successfully.!"}, status=status.HTTP_200_OK)
            else:
                # if signature verification fails.
                payment.delete()
                return JsonResponse({"Error" : "Payment signature verification failed."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({"error" : "razorpay_payment_id/razorpay_subscription_id/razorpay_signature is none"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def payment(request):
    plan_id = request.data.get('plan_id', None)
    amount = request.data.get('amount', None)
    user = request.user
    if user.role==User.CLIENT or user.role == User.HOSPITAL_MANAGER:
        if user.role == User.HOSPITAL_MANAGER:
            customer = request.data.get('customer', None)
            try:
                user = User.objects.get(id=customer, role=User.CLIENT)
            except User.DoesNotExist:
                return Response({'error' : 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        if plan_id and amount is not None:
            try:
                membership = MembershipPlans.objects.get(amount=amount)
            except:
                return Response({"error" : "Selected plan not found"}, status=status.HTTP_404_NOT_FOUND)

            callback_url = "https://" + str(get_current_site(request)) + "/payments/checkout/" 
            url = "https://api.razorpay.com/v1/subscriptions"
            result = requests.post(url, data={
                "plan_id":  plan_id, #"plan_Hj5rCoyu7jFO3m"
                "total_count":  membership.recurrence_count, #1
                "quantity":1
            }, auth=HTTPBasicAuth(settings.RAZOR_KEY_ID,settings.RAZOR_API_ID))
            subscription = json.loads(result.text)
            Payments.objects.create(sub_Id=subscription["id"],customer=user, amount=amount)
            context = {
                'callback_url' : callback_url,
                'sub_id' : subscription['id']
            }
            return JsonResponse(context, safe=False)
        else:
            return JsonResponse({"error" : "amount/plan_id not provided"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({"error" : "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)
    

@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def get_free_subscription(request):
    user = request.user
    if not user.role == User.CLIENT:
        customer_id = request.data.get('customer', None)
        try:
            user = User.objects.get(id=customer_id, role=User.CLIENT)
        except User.DoesNotExist:
            return Response({'error' : 'client not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        membership = MembershipPlans.objects.get(name="free version")
    except MembershipPlans.DoesNotExist:
        return Response({'error' : 'membership not found'}, status=status.HTTP_404_NOT_FOUND)
    # ! make the current active plan to inactive
    Subscriptions.objects.filter(customer=user,is_active=True).update(is_active=False)

    # ? new subscription
    validity = datetime.now() + timedelta(days=membership.validity)
    Subscriptions.objects.create(customer=user, valid_till=make_aware(validity), membership=membership,is_active=True)
    # make account inactive.
    user.is_active = False
    user.save()
    return Response({'success' : 'subscribed to free version'}) 


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_all_plans(request):
    context = {'plans' : []}
    response = requests.get('https://api.razorpay.com/v1/plans', auth=HTTPBasicAuth(settings.RAZOR_KEY_ID,settings.RAZOR_API_ID))
    result = json.loads(response.text)
    if response.status_code == 200:
        for plan in result['items']:
            dict = {
                "id" : plan['id'],
                "name" : plan['item']['name'],
                "amount" : plan['item']['amount']
            }
            context['plans'].append(dict)
        return JsonResponse(context, safe=False)
    else:
        # print(result['error']['description'])
        return JsonResponse({'message' : result['error']['description']}, status=status.HTTP_504_GATEWAY_TIMEOUT)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_client_subscription(request):
    user = request.user
    if user.role == User.CLIENT:
        try:
            Subscription = Subscriptions.objects.prefetch_related('membership').get(customer=user.id,is_active=True)
            # if Subscription:
            has_subscription = True
            subscription_package = Subscription.membership.name
        except Subscriptions.DoesNotExist:
            has_subscription = False
            subscription_package = ""
        # 401 if no active subscription
        if not has_subscription:
            return Response({'error' : 'has no active subscription'}, status=status.HTTP_401_UNAUTHORIZED)
        # else return package name
        return Response({
            "subscription_package" : subscription_package
        })
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST',])
@permission_classes((AllowAny,))
def halted(request):
    try:
        sub_id = request.data['payload']['subscription']['entity']['id']
        instance = Subscriptions.objects.get(sub_id=sub_id)
        instance.is_active=False
        instance.save()
    except:
        pass
    return JsonResponse({'success' : 'success'}, status=status.HTTP_200_OK)



@api_view(['POST',])
@permission_classes((AllowAny,))
def success(request):
    razorpay_signature = request.data.get('razorpay_signature', "failed")
    id = request.data['payload']['subscription']['entity']['id']
    # print(id)
    # for key, value in request.data.items():   
    #     print(f'key : {key} and value : {value}')
    return JsonResponse({'success' : 'success'}, status=status.HTTP_200_OK)

# ./ngrok http 8000

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def appointment_payment(request):
    currency = 'INR'
    params_amount = request.query_params.get('amount', None)
    amount = int(params_amount)

    if amount is None or amount == 0:
        return Response({'error' : 'No amount'}, status=status.HTTP_400_BAD_REQUEST)
    # doctor_id = request.query_params.get('doctor_id', 0)
    # try:
    #     doctor = User.objects.get(id=doctor_id, doctor=True)
    #     doc_details = doctor.docDetails.first()
    #     amount = doc_details.price
    #     if amount == 0 or amount == None:
    #         return JsonResponse({'error' : 'Doctor has not mentioned his fee'}, status=status.HTTP_404_NOT_FOUND)

    # except DoctorDetails.DoesNotExist:
    #     return JsonResponse({'error' : 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)
     
    # Create a Razorpay Order
    razorpay_order = client.order.create(dict(amount=amount * 100,currency=currency))
 
    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = "https://" + str(get_current_site(request)) + "/payments/appointment-payment-handler/" 
 
    # pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount * 100
    context['currency'] = currency
    context['callback_url'] = callback_url
    AppointmentPayments.objects.create(order_id=razorpay_order_id,amount=amount)
    return Response(context)
    # return render(request, 'index.html', context=context)



# @csrf_exempt
@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def appointment_payment_handler(request):
    # doctor = request.data.get('doctor', None)
    # date = request.data.get('date', None)
    # time = request.data.get('time', None)
    # customer = request.user.id 
    user = request.user
    # only accept POST request.
    if request.method == "POST" and user.role==User.CLIENT:
        try:
            # get the required parameters from post request.
            payment_id = request.data.get('razorpay_payment_id', None)
            razorpay_order_id = request.data.get('razorpay_order_id', None)
            signature = request.data.get('razorpay_signature', None)
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            # verify the payment signature.
            result = client.utility.verify_payment_signature(params_dict)
            if result is None:
                # amount = 20000  # Rs. 200
                try:
                    appointment_payment = AppointmentPayments.objects.get(order_id=razorpay_order_id)
                except:
                    return JsonResponse({'error' : 'aapointment payment not found'}, status=status.HTTP_404_NOT_FOUND)
                # if doctor is not None:
                #     try:
                #         doctor = DoctorDetails.objects.select_related('user').get(user=doctor)
                #     except DoctorDetails.DoesNotExist:
                #         return JsonResponse({"Error" : "doctor does not exists"}, status=status.HTTP_404_NOT_FOUND)
                #     try:
                #         customer = CustomerDetails.objects.get(user=request.user.id)
                #     except User.DoesNotExist:
                #         return JsonResponse({"Error" : "Customer does not exists"}, status=status.HTTP_404_NOT_FOUND)
                # else:
                #     return JsonResponse({"Error" : "Customer and doctor is required to make an appointment."})
                try:
                    # capture the payemt
                    # data = request.data
                    # data['customer'] = customer.id
                    # data['doctor'] = doctor.id
                    # try:
                    #     schedule = datetime.combine(datetime.fromisoformat(date),datetime.strptime(time.replace(" ", ""), '%H:%M').time()) #without pm
                    # except:
                    #     schedule = datetime.combine(datetime.fromisoformat(date),datetime.strptime(time.replace(" ", ""), '%H:%M%p').time()) #with am and pm
                    # data['schedule'] = schedule

                    # serializer = BookingSerializer(data=data, context={'request': request})
                    
                    # if serializer.is_valid(raise_exception=True):
                    client.payment.capture(payment_id, appointment_payment.amount*100)
                    # appointment = serializer.save()
                    # appointment_payment.appointment = appointment
                    appointment_payment.captured = True
                    appointment_payment.save()
                    return JsonResponse({'success' : 'payment successfull'})
                    # else:
                    #     return JsonResponse(serializer.errors)                   
                except:
                    # if there is an error while capturing payment.
                    return JsonResponse({'error' : 'error capturing payment'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # if signature verification fails.
                return JsonResponse({'error' : 'signature verification failed'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse({'error' : 'errors 1'})
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


def test(request):
    currency = 'INR'
    amount = 20000  # Rs. 200
 
    # Create a Razorpay Order
    razorpay_order = client.order.create(dict(amount=amount,currency=currency,payment_capture='0'))
 
    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = 'paymenthandler/'
 
    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url
 
    return render(request, 'index.html', context=context)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_user_data(request):
    user = request.user
    cid = request.query_params.get('customer', None)
    try:
        customer = User.objects.get(id=cid, role=User.CLIENT)
    except User.DoesNotExist:
        return Response({'error' : 'client not found'}, status=status.HTTP_404_NOT_FOUND)

    name = customer.firstname + " " + customer.lastname if customer.lastname else ""
    email = customer.email
    phone = customer.mobile if customer.mobile else ""

    return Response({
        "name" : name,
        "email" : email,
       "phone" : phone
    })


from .serializers import Membership2Serializer ,PurchasedMembershipSerializer

@api_view(['GET',])
@permission_classes((AllowAny,))
def get_memberships(request):
    queryset = MemberShip.objects.all()
    serializer = Membership2Serializer(queryset , many = True)

    return Response({
        "status" : True,
        "data" : serializer.data,
        "message" : "membership fetched"
    })

@api_view(['GET',])
@permission_classes((AllowAny,))
def get_purchased_memberships(request):
    user_id = request.GET.get('user_id')
    if user_id is None:
        return Response({
            "status" : False,
            "data" : {},
            "message" : "user_id is required"
        })
    
    queryset = PurchasedMembership.objects.filter(user__id = request.GET.get('user_id'))
    
    serializer = PurchasedMembershipSerializer(queryset , many = True)

    return Response({
        "status" : True,
        "data" : serializer.data,
        "message" : "purchased membership fetched"
    })


@api_view(['POST',])
@permission_classes((AllowAny,))
def purchase_memberships(request):
    try:
        keys = ['membership_id', 'user_id' ,'uid']

        data = request.data

        for key in keys:
            if data.get(key) is None:
                return Response({
                    "status" : False,
                    "message" : f"{key} is required"
                })
        queryset1 = None 
        try:
            queryset1 = MemberShip.objects.get(pk = data.get('membership_id') )
        except Exception as e:
            print(e)
            return Response({
                    "status" : False,
                    "message" : f"invalid membership id"
                })
        
        

        PurchasedMembership.objects.create(
            user = User.objects.get(pk = data.get('user_id')),
            membership = queryset1,
            uid = data.get('uid')
        )


        # serializer = Membership2Serializer(queryset , many = True)
        
        return Response({
            "status" : True,
            "data" : {},
            "message" : "payment done"
        })

    except Exception as e :
        print(e)
        return Response({
            "status" : False,
            "data" : {},
            "message" : "something went wrong"
        })


class WebHook(APIView):
    def post(self , request):
        try:
            data = request.data
            payload = data.get('payload').get('payment').get('entity').get('description')
            
            print(payload)
            if payload:
                obj = PurchasedMembership.objects.get(uid = payload)
                obj.is_paid = True
                
                user_obj = User.objects.get(id = obj.user.id)
                user_obj.is_active = False
                user_obj.save()
                obj.save()

                return Response({
                    'status' : True
                })
            
            return Response({
                    'status' : False,
                    'message' : 'not done'
                })

        except Exception as e:
            print(e)

        return Response({
                'status' : False
            })


       


class AppointmentWebHook(APIView):
    def post(self , request):
        try:
            data = request.data
            payload = data.get('payload').get('payment').get('entity').get('description')

            if payload:
                obj = Appointments.objects.get(uid = payload)
                obj.is_paid = True
                obj.save()
                return Response({
                    'status' : True
                })
            
            return Response({
                    'status' : False,
                    'message' : 'not done'
                })
        
        except Exception as e:
            print(e)
        
        return Response({
                'status' : False
            })