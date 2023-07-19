# from http.client import responses
from Customer.models import LastUpdateDate
from Sales.models import PatientDetailsApporval
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import *
from rest_framework.decorators import api_view, permission_classes
from .models import InvestigationCriticallity, CustomerCallReposnses ,CallResponses, CriticalityChange
import datetime
from datetime import timedelta, timezone
# from Accounts.serializers import CustomerSerializer
from Accounts.models import CustomerDetails
from django.contrib.auth import get_user_model
from Admin.serializers import totalClientSerializer
from django.db.models import Q
# from Appointments.views import WhatsAppClient, from_number
from django.conf import settings
# for email
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models.query import Prefetch
User = get_user_model() 

# criticality change message
def CriticalityChangeMessage(prev,current):
    base_message = "Hi\nReaching out to inform that the criticality status of {clientName} has been changed from {prev} to {current}."
    if prev=='medium' and current=='severe':
        whatsAppMessage = base_message + "Immediately take necessary steps to make her health stable.\n\nTo know more :[client profile link]"
    elif prev=='medium' and current=='stable':
        whatsAppMessage = base_message + "Please have a look on her profile.\n\nTo know more :[client profile link]"
    elif prev=='stable' and current=='medium' or current=='severe':
        whatsAppMessage = base_message + "Please take necessary steps to avoid further complication.\n\nTo know more :[client profile link]"
    # else its severe to medium or stable
    else:
        whatsAppMessage = base_message + "Please have a look on her profile.\n\nTo know more :[client profile link]".format(
            prevCriticality=prev,
            currentCriticality=current,
        )
    return whatsAppMessage


@api_view(['POST',])
@permission_classes((AllowAny,))
def request_response(request):
    user = request.user
    if user.role==User.SALES or user.role==User.ADMIN:
        is_approved = request.data.get('is_approved', None)
        id = request.data.get('id', None)
        if is_approved and id is not None:

            # get the request
            try:
                detailsRequest = PatientDetailsApporval.objects.get(id=id)
            except PatientDetailsApporval.DoesNotExist:
                return JsonResponse({"Error" : "Client details request not found."}, status=status.HTTP_404_NOT_FOUND)

            # if the request is approved
            if is_approved == 'True':
                detailsRequest.is_approved = True
                detailsRequest.save()
                return JsonResponse({"Success" : "Request approved"}, status=status.HTTP_202_ACCEPTED)

            # else the request is rejected
            else:
                detailsRequest.delete()
                return JsonResponse({"Success" : "Request Rejected"}, status=status.HTTP_202_ACCEPTED)  
        else:
            return JsonResponse({"Error" : "is_approved/id attribute is not provided."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def view_all_requests(request):
    user = request.user
    if user.role==User.SALES or user.role==User.ADMIN:
        data = PatientDetailsApporval.objects.filter(is_approved=False)
        serializer = RequestApprovalSerializer(data, many=True)
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST','PATCH'])
@permission_classes((IsAuthenticated,))
def investigation_submit(request):
    user = request.user
    if user.role == User.SALES:
        cid =request.data.get('customer', None)
        criticallity_value = request.data.get('criticallity', None)
        custom_report = request.data.get('custom', None)
        existing_custom = request.data.get('existing_custom', None)
        date = request.data.get('date', None)
        data = request.data.copy()
        # context = {}

        if cid and date is not None: 
            
            try:
                customer = User.objects.prefetch_related('customer_details','customer_details__referalId','customer_details__referalId__user').get(id=cid)
            except User.DoesNotExist:
                return JsonResponse({"Error" : "Customer not found."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # sales = SalesTeamDetails.objects.get(user=request.user.id)
                sales = request.user.salesDetails.first()
            except SalesTeamDetails.DoesNotExist:
                return JsonResponse({"Error" : "Sales Team not found"}, status=status.HTTP_404_NOT_FOUND)

            if request.method == "PATCH":
                try:
                    investigation_update = Investigation.objects.get(customer=customer.id, date=date)
                    update=True
                    investigation = InvestigationSerializer(investigation_update, data=data, partial=True)
                except Investigation.DoesNotExist:
                    update=False
                    return JsonResponse({'error':'No investigation found for update, do post request'}, status=status.HTTP_404_NOT_FOUND)
            else:
                investigation = InvestigationSerializer(data=data)

            if criticallity_value is not None:
                try:
                    criticallity = InvestigationCriticallity.objects.get(name=criticallity_value)
                    data['criticallity'] = criticallity.id
                except InvestigationCriticallity.DoesNotExist:
                    return JsonResponse({"Error" : "Criticallity not found."}, status=status.HTTP_400_BAD_REQUEST)
        
            data['customer'] = customer.id
            data['sales'] = sales.id

            if custom_report is not None and len(custom_report) != 0:
                if request.method == 'POST':
                    if custom_report is not None:
                        for dict in custom_report:
                            dict.update({'sales' : sales.id, 'customer' : customer.id, "date" : date})
                        customSerializer = CustomInvestigationSerializer(data=custom_report, many=True)
                # patch
                else:
                    if custom_report is not None and len(custom_report) != 0:
                        for dict in custom_report: #"custom" json key
                            dict.update({'sales' : sales.id, 'customer' : customer.id, "date" : date})
                            customSerializer = CustomInvestigationSerializer(data=custom_report, many=True)
                    if existing_custom is not None and len(existing_custom) != 0:
                        for dict in existing_custom: #custom key
                            # dict.update({'sales' : sales.id, 'customer' : customer.id, "date" : date})
                            try:
                                # print(dict)
                                instance = CustomInvestigation.objects.get(id=dict.get('id','0'))
                                existing_customSerializer = CustomInvestigationSerializer(instance,data=dict, partial=True)
                                if existing_customSerializer.is_valid():
                                    existing_customSerializer.save()
                            except CustomInvestigation.DoesNotExist:
                                return JsonResponse({'error' : 'custom investigation with the id not found'}, status=status.HTTP_404_NOT_FOUND)

                    # CustomInvestigation.objects.filter(customer=customer.id, date=date).delete()
                    # customSerializer = CustomInvestigationSerializer(data=custom_report, many=True)
                if custom_report is not None and len(custom_report) != 0:
                    if customSerializer.is_valid():
                        customSerializer.save() #investigation=investigation_instance
                    else:
                        return JsonResponse(customSerializer.errors, safe=False)
            validation = investigation.is_valid(raise_exception=True)
            if validation:
                if len(investigation.validated_data) > 3: # check if data is present other than foriegn key relations
                    new_instance = investigation.save()
                # check for criticaly change
                investigations = Investigation.objects.filter(customer=cid,criticallity__isnull=False,date__lte=date).prefetch_related('criticallity').order_by('-date', '-id')
                if investigations and investigations.count() >= 2:
                    previous_criticality = investigations[1].criticallity.name
                    current_criticality = investigations[0].criticallity  
    
                    if previous_criticality != current_criticality.name:
                        instance, created = CriticalityChange.objects.get_or_create(customer=customer,date=date,defaults={'criticallity':current_criticality, 'consent' : False})
                        if not created:
                            instance.criticallity = current_criticality
                            instance.consent = False
                            instance.save()
                        # a=CriticalityChange.objects.filter(customer=customer,date=date)
                        # if true


                        # ? whatsapp notification to doctor
                        whatsAppMessage = CriticalityChangeMessage(previous_criticality, current_criticality.name)
                        whatsAppMessage = whatsAppMessage.format(
                            prev=previous_criticality,
                            current=current_criticality.name,
                            clientName=customer.firstname.capitalize()
                        )
                        doctor_number = customer.customer_details.first().referalId.user.mobile
                        to_number = 'whatsapp:91{}'.format(doctor_number)
                        # ? WhatsAppClient.messages.create(from_=from_number,body=whatsAppMessage,to=to_number)
                        # email to the sales team
                        reciever_email = request.user.email
                        subject = 'Criticality Changed'
                        html_content = render_to_string('Emails/Sales/CriticalityChange.html', {
                            'title' : subject,
                            "clientName" : customer.firstname.capitalize(),
                        })# + customer.lastname
                        text_content = strip_tags(html_content)
                        email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [reciever_email])
                        email.attach_alternative(html_content, "text/html")
                        # ?email.send()
                else:
                    instance, created = CriticalityChange.objects.get_or_create(customer=customer,date=date,criticallity=new_instance.criticallity)
                return JsonResponse({"Success" : "Investigation report added successfully."}, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse(investigation.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({"Error" : "Customer/date not provided."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

 
@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def delete_custom_investigation(request):
    user = request.user
    if user.role == User.SALES:
        id = request.data.get('id', None)
        if id is not None:
            try:
                CustomInvestigation.objects.get(id=id).delete()
                return JsonResponse({"success": "Custom investigation deleted"})
            except CustomInvestigation.DoesNotExist:
                return JsonResponse({"error": "Custom investigation with the id not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return JsonResponse({"error" : 'id not provided in data'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def submit_custom_investigation(request):  
    user = request.user
    if user.role==User.SALES:  
        try:
            sales = request.user.salesDetails.all()
            if sales:
                sales = sales.first()
            else:
                return JsonResponse({"Error" : "Sales team not found"}, status=status.HTTP_404_NOT_FOUND)
        except SalesTeamDetails.DoesNotExist:
            return JsonResponse({"Error" : "Sales team not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        for dict in data:
            dict.update({'sales' : sales.id})
        customSerializer = CustomInvestigationSerializer(data=data, many=True)
        if customSerializer.is_valid():
            customSerializer.save() #investigation=investigation_instance
            return JsonResponse({"Success" : "Investigation report added successfully."}, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(customSerializer.errors)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def sales_dashboard_details(request):
    user = request.user
    if user.role==User.SALES:
        # allPatients = User.objects.filter(patient=True).prefetch_related('customer_details', 'customer_details__referalId','customer_details__referalId__user')
        allPatients = CustomerDetails.objects.filter(user__is_active=True).prefetch_related('user', 'referalId__user',Prefetch('user__criticality_change',queryset=CriticalityChange.objects.order_by('-date','-criticallity__criticality')))
        # allPatients = CustomerDetails.objects.filter(user__is_active=True).prefetch_related('referalId', 'referalId__user',)
        # total clients count
        total_patients_count = allPatients.count()
        # detials
        totalPatients = ClientDetialSerializer(allPatients, many=True)
        # time_threshold = datetime.datetime.now() - datetime.timedelta(days=1,hours=24)
        time_threshold = datetime.datetime.now(timezone.utc) - timedelta(hours=24)

        lastUpdatedPatients = LastUpdateDate.objects.filter(Q(diet__lt = time_threshold) | Q(activity__lt = time_threshold) | Q(symptom__lt = time_threshold) | Q(medicine__lt = time_threshold)).filter(customer__is_active = True)

        lastUpdatedPatients_count = lastUpdatedPatients.count()

        # lastUpdatedPatientSerializer = CustomerLastUpdated24hoursSerilializer(lastUpdatedPatients, many=True)
    
        # total clients this month
        month = datetime.datetime.today().month
        this_month_patients = allPatients.filter(user__dateJoined__month=month)

        # details
        # this_month_patient_details = CustomerSerializer(this_month_patients, many=True)

        # this month count
        this_month_patients_count = this_month_patients.count()

    
        return JsonResponse({
            'firstname' : user.firstname,
            'lastname' : user.lastname,
            # 'lastUpdated_in_24Hours' : lastUpdatedPatientSerializer.data,   

            'total_patients_count' : total_patients_count,
            'noUpdateFromClientsCount' : lastUpdatedPatients_count,

            'this_month_patients_count' : this_month_patients_count,

            # details
            'totalPatients_details' : totalPatients.data
            # 'this_month_patient_details' : this_month_patient_details.data,
            # 'diet' : dietSerializer.data,
        })
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def clients_this_month(request):
    user = request.user
    if user.role==User.SALES or user.role==User.ADMIN or user.role==User.CONSULTANT:
        threshold_date = datetime.datetime.now().date() - timedelta(days=294) #42 weeks
        # total clients this month
        month = datetime.datetime.today().month
        this_month_patients = CustomerDetails.objects.filter(user__dateJoined__month=month,Menstruation_date__gte=threshold_date).prefetch_related('referalId', 'referalId__user')
        # details
        this_month_patient_details = ClientDetialSerializer(this_month_patients, many=True)
        return JsonResponse(this_month_patient_details.data, safe=False)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def all_clients(request):
    user = request.user
    if user.role==User.SALES or user.role==User.DOCTOR or user.role==User.CONSULTANT:
        threshold_date = datetime.datetime.now().date() - timedelta(days=294) #42 weeks
        allClients = CustomerDetails.objects.filter(Menstruation_date__gte=threshold_date).prefetch_related('referalId', 'referalId__user')
        serializer = ClientDetialSerializer(allClients, many=True)
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def no_update_clients(request):
    user = request.user
    time_threshold = datetime.datetime.now(timezone.utc) - timedelta(hours=24)

    # lastUpdatedPatients = LastUpdateDate.objects.filter(Q(diet__lt = time_threshold) | Q(activity__lt = time_threshold) | Q(symptom__lt = time_threshold) | Q(medicine__lt = time_threshold)).prefetch_related('customer', 'customer__customer_details')
    if user.role==User.SALES:
        lastUpdatedPatients = CustomerDetails.objects.filter(
            Q(user__is_active__in=[True])
            & Q(user__last_update__diet__lt=time_threshold)
            & Q(user__last_update__activity__lt=time_threshold)
            & Q(user__last_update__symptom__lt=time_threshold)
            & Q(user__last_update__medicine__lt=time_threshold)).prefetch_related('user','referalId', 'referalId__user')

        # lastUpdatedPatientSerializer = CustomerLastUpdated24hoursSerilializer(lastUpdatedPatients, many=True)
        lastUpdatedPatientSerializer = ClientDetialSerializer(lastUpdatedPatients, many=True)
    
        return JsonResponse({
            'clients' : lastUpdatedPatientSerializer.data,
            'sales_firstname' : user.firstname,
            'sales_lastname' : user.lastname
        })
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((AllowAny,))
def last_updated_before_one_day(request):
    user = request.user
    time_threshold = datetime.datetime.now(timezone.utc) - timedelta(hours=24)
    today = datetime.datetime.today().date()
    # print(today)
    # to get patients that are in antinatal, that is LMP is greater than (todays date - 280 days)
    date = today - timedelta(days=280)
    # print(date)
    if user.role==User.SALES:
        customers_with_LMP_gt_date = CustomerDetails.objects.filter(Menstruation_date__lt=date).values_list('user_id')
        # print(customers_with_LMP_gt_date)

        lastUpdatedPatients = LastUpdateDate.objects.filter(Q(diet__lt = time_threshold) | Q(activity__lt = time_threshold) | Q(symptom__lt = time_threshold) | Q(medicine__lt = time_threshold)).exclude(customer__id__in=customers_with_LMP_gt_date)

        # lastUpdatedPatients_count = lastUpdatedPatients.count()

        lastUpdatedPatientSerializer = CustomerLastUpdated24hoursSerilializer(lastUpdatedPatients, many=True, context={
            'date' : date
        })
    
        return JsonResponse(lastUpdatedPatientSerializer.data, safe=False)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST','PATCH'])
@permission_classes((IsAuthenticated,))
def add_call_response(request):
    user = request.user
    response = request.data.get('response', 'None')
    customer = request.data.get('customer', None)
    date = request.data.get('date', None)
    data = request.data.copy()
    if user.role==User.SALES:
        if response is not None:
            try:
                response = CallResponses.objects.get(response__iexact=response)
                data['response'] = response.id
            except CallResponses.DoesNotExist:
                response = ""
                # return JsonResponse({"Error" : "Call Response not found"}, status=status.HTTP_404_NOT_FOUND)
            try:
                sales = SalesTeamDetails.objects.get(user=request.user.id)
            except SalesTeamDetails.DoesNotExist:
                return JsonResponse({"Error" : "Sales Team not found"}, status=status.HTTP_404_NOT_FOUND)

            data['sales'] = sales.id
            data['date'] = date if date is not None else  datetime.datetime.now().date()

            if request.method == 'PATCH':
                try:
                    instance = CustomerCallReposnses.objects.get(customer=customer, date=datetime.datetime.today())
                except CustomerCallReposnses.DoesNotExist:
                    return JsonResponse({"error" : "call response not found"}, status=status.HTTP_404_NOT_FOUND)
                serializer = CustomerCallReposnseSerializer(instance, data=data, partial=True)
            else:
                serializer = CustomerCallReposnseSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return JsonResponse(serializer.data,  safe=False)
        else:
            return JsonResponse({"Error" : "response cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_call_response(request):
    user = request.user
    customer = request.query_params.get('customer', None)
    param_date = request.query_params.get('date', None)
    date = param_date if param_date is not None else datetime.datetime.today()
    if user.role==User.SALES:
        if customer is not None:
            try:
                instance = CustomerCallReposnses.objects.get(customer=customer, date=date)
            except CustomerCallReposnses.DoesNotExist:
                return JsonResponse({'error' : 'no call repsonse'})
                # instance = ""
            serializer = CustomerCallReposnseSerializer(instance)
            return JsonResponse(serializer.data, safe=False)

        else:
            return JsonResponse({'error' : 'provide customer id in params'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_all_call_responses(request):
    user = request.user
    customer = request.query_params.get('customer', None)
    if user.role==User.SALES or user.role==User.DOCTOR:
        if customer is not None:
            responses = CustomerCallReposnses.objects.filter(customer=customer)
            serializer = CustomerCallReposnseSerializer(responses, many=True)
            return JsonResponse(serializer.data, safe=False)

        else:
            return JsonResponse({'error' : 'provide customer id in params'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def clients_under_sales(request):
    user = request.user
    sales = request.query_params.get('sales', None)
    try:
        # sales = SalesTeamDetails.objects.get(user=sales)
        sales = User.objects.get(id=sales)
        sales = sales.salesDetails.first()
    except User.DoesNotExist:
        return JsonResponse({"Error" : "sales team not found"}, status=status.HTTP_404_NOT_FOUND)
    if user.role==User.ADMIN:
        investigation = Investigation.objects.filter(sales=sales.id).distinct().values_list('customer')
        # custom investigation
        custom = CustomInvestigation.objects.filter(sales=sales.id).distinct().values_list('customer')
        # customer call response
        CallResponse = CustomerCallReposnses.objects.filter(sales=user.id).distinct().values_list('customer')
        total_ids = list(investigation) + list(custom) + list(CallResponse)

        clients = CustomerDetails.objects.filter(user__in=total_ids)
        serializer = totalClientSerializer(clients, many=True)

        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse({"Error" : "You dont have permission for that"}, status=status.HTTP_401_UNAUTHORIZED)


# def DeleteResponse():
#     CallResponses.objects.all().delete()

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def sales_team_called_list(request):
    customer_id = request.query_params.get('customer_id', None)

    if customer_id is not None:
        try:
            customer_id = int(customer_id)
            calls = CustomerCallReposnses.objects.filter(customer__id=customer_id)
            serializer = CustomerCallReposnsesSerializer(calls, many=True)
            return JsonResponse(serializer.data, safe=False)  # Set safe parameter to False
        except CustomerCallReposnses.DoesNotExist:
            return JsonResponse({'error': 'No calls found for the given customer_id.'},
                                status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return JsonResponse({'error': 'Invalid customer_id. Must be an integer.'},
                                status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({'error': 'No customer_id provided in the query parameters.'},
                        status=status.HTTP_400_BAD_REQUEST)