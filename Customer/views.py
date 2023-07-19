
from multiprocessing import context
from os import stat
from django.db.models.query import Prefetch
# from django.http.response import JsonResponse
# from rest_framework.serializers import Serializer
from Accounts.models import Banner, DoctorDetails
from Accounts.serializers import BannerSerializer

from .serializer import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.timezone import make_aware
from LearnIt.views import calculate_stage
from datetime  import date, timedelta, datetime
import datetime
from .models import LastUpdateDate
from Sales.models import CustomInvestigation, Investigation, CriticalityChange
from Sales.serializers import InvestigationSerializer, CustomInvestigationSerializer
from LearnIt.models import Stage
from Consultant.serializers import CustomizedPlanSerializer
from Consultant.models import CustomizedPlan
from django.db.models import Q
from django.db.models import Count
# medical
from rest_framework.decorators import parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from Doctor.serializers import DoctorProfileSerialzer


# ? normal functions
def foetal_age(menstruation_date, lastDate):
    days_pregnant = lastDate - menstruation_date
    week = days_pregnant.days/7
    if isinstance(week, float):
        week = int(week)
        days_completed = days_pregnant.days % 7
    week = 0 if week < 0 else week
    days_left = 280 - days_pregnant.days
    days_left = 0 if days_left < 0 or days_left > 280 else days_left

    return week, days_completed, days_left

def scan_date_to_string(startDate, endDate):
    stringFormat = "From {fromWeekDay}, {fromMonth} {fromDay}, {fromYear} to {toWeekDay}, {toMonth} {toDay}, {toYear}".format(
            fromWeekDay = startDate.strftime('%A'),
            fromMonth = startDate.strftime('%B'),
            fromDay = str(startDate.day),
            fromYear = str(startDate.year),
            toWeekDay = endDate.strftime('%A'),
            toMonth = endDate.strftime('%B'),
            toDay = str(endDate.day),
            toYear = str(endDate.year)
        )
    return stringFormat

def update_date(instance, module):
    current_date = datetime.datetime.now()
    timezone_aware_date = make_aware(current_date)
    customer = User.objects.filter(id=instance.customer.id).first()
    LastUpdate, created = LastUpdateDate.objects.get_or_create(customer=customer)

    instanceDate = instance.date
    if isinstance(instanceDate, str):
        instanceDate = instanceDate.replace('-','')
        instanceDate = datetime.datetime.strptime(instanceDate, '%Y%m%d').date()

    if module == 'diet' and instanceDate >= LastUpdate.diet.date():
        LastUpdate.diet = timezone_aware_date
    elif module == 'activity' and instanceDate >= LastUpdate.activity.date():
        LastUpdate.activity = timezone_aware_date
    elif module == 'medicine' and instanceDate >= LastUpdate.medicine.date():
        LastUpdate.medicine = timezone_aware_date
    elif module == 'symptom' and instanceDate >= LastUpdate.symptom.date():
        LastUpdate.symptom = timezone_aware_date
    elif module == 'exercise' and instanceDate >= LastUpdate.exercise.date():
        LastUpdate.exercise = timezone_aware_date
    else:
        # LastUpdate.contraction = timezone_aware_date
        pass
    LastUpdate.save()

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def my_doctor_profile(request):
    user = request.user
    if user.role == User.CLIENT:
        try:
            client_detail = CustomerDetails.objects.prefetch_related('referalId', 'referalId__user').get(user=user.id)
        except CustomerDetails.DoesNotExist:
            return Response({'error' : 'client not found'}, status=status.HTTP_404_NOT_FOUND)

        doctor = client_detail.referalId
        serializer = DoctorProfileSerialzer(doctor,context={'request':request})
        return Response(serializer.data)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

from Accounts.models import VideoLink
from Accounts.serializers import VideoLinkSerializer
from Payments.models import PurchasedMembership
@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def customer_dashboard_details(request):

    try:
        user = request.user
        if user.role == User.CLIENT:
            daysCompleted = 0
            cid = user.id
            if cid is not None:
                try:
                    details = user.customer_details.first()
                except User.DoesNotExist:
                    return Response({"Error" : "Customer with the given id not found"},status=status.HTTP_404_NOT_FOUND )

                # calc week and days left from Menstruation_date
                periods_date =  details.Menstruation_date
                today = date.today()

                daysPregnant = today - periods_date
                week = int(daysPregnant.days/ 7)
                # daysCompleted = (daysPregnant.days % 365) % 7
                daysCompleted = daysPregnant.days % 7

                week = 0 if week < 0 else week
                daysLeft = 280 - daysPregnant.days

                daysLeft = 0 if daysLeft < 0 else daysLeft

                purchased_membership_context = {}
                
                
                purchased_membership = PurchasedMembership.objects.filter(
                                    user = user,
                                    is_paid = True
                                )
                if purchased_membership.exists():
                    purchased_membership = purchased_membership[0]
                    purchased_membership_context = {
                            "membership" : purchased_membership.membership.membership_name,
                            "is_paid" : purchased_membership.is_paid,
                            "created_at" : purchased_membership.created_at
                    }
                
                


                context = {
                    'id' : user.id,
                    'firstname' : user.firstname,
                    'lastname' : user.lastname,
                    'week' : week,
                    'daysCompleted' : daysCompleted,
                    'daysLeft' : daysLeft,
                    'dateJoined' : user.dateJoined,
                   
                    'subscription_package' : purchased_membership_context
                }

                print("GOOOODD")
                print(context)


                video = VideoLink.objects.all()
                video_serializer = VideoLinkSerializer(video, many = True)
                context['video'] = video_serializer.data
                # get the detials of the baby (wiegth, length and the image)
                # print(week)
                try:
                    babyDetail = BabyPics.objects.get(week=week)
                except BabyPics.DoesNotExist:
                    babyDetail = None

                if babyDetail is not None:
                    babydetails = BabyDetailSerializer(babyDetail, context={"request": request})
                    context['babyDetails'] = babydetails.data

                banners = Banner.objects.all()
                banner_serializer = BannerSerializer(banners, many = True)
                context['banners'] = banner_serializer.data
                
                return Response(context,status=status.HTTP_200_OK)
        else:
            return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(e)

        
        return Response({'error' : 'something went wrong'}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def all_dates_diet(request):
    user = request.user
    if not user.role == User.HOSPITAL_MANAGER:
        if user.role == User.CLIENT:
            customer = user.id
        else:
            customer = request.query_params.get('id', None)
        if customer is not None:
            diet = DietTracker.objects.filter(customer=customer).prefetch_related('meal').order_by('-date')
            serializer = DietTrackerDisplaySerializer(diet ,many=True)
            return Response(serializer.data)
        else:
            return Response({"Error" : "customer not provided"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


# diet tracker GET method
@api_view(['GET',])
@permission_classes((AllowAny,))
def diet_tracker_get(request):
    user = request.user
    if not user.role == User.HOSPITAL_MANAGER:
        if user.role == User.CLIENT:
            cid = user.id
        else:
            cid = request.query_params.get('customer', None)

        if cid is None:
            return Response({"Error" : "Provide 'customer': id in the params"}, status=status.HTTP_400_BAD_REQUEST)

        date = request.query_params.get('date', None)
        if date == None:
                date = datetime.datetime.now()
        if cid is not None:
            try:
                customer = User.objects.get(id=cid)
            except User.DoesNotExist:
                return Response({'user':'Customer does not exists'}, status=status.HTTP_404_NOT_FOUND)

            # get customized diet uploaded by doctor
            # try:
            #     mod = DailyTrackerModule.objects.get(name__iexact='diet')
            # except DailyTrackerModule.DoesNotExist:
            #     return Response({"Error" : "Selected module not found"})

            customized = CustomizedPlan.objects.filter(tracker=CustomizedPlan.DIET,customer=cid)
            # check if empty, if not get the latest from the queryset to serialize
            if not customized:
                customizedSerializer = CustomizedPlanSerializer()
            else:
                customizedSerializer = CustomizedPlanSerializer(customized.latest('time', 'date'))

            diet = DietTracker.objects.filter(customer=customer, date=date) #2011-02-10 = 2 meals
            serializer = DietTrackerSerializer(diet ,many=True)
            return Response({"Diet" : serializer.data, "CustomizedDiet" : customizedSerializer.data})
        else:
            return Response({"Error" : "Customer not provided"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

# submit diet taken
@api_view(['POST','PATCH'])
@permission_classes((IsAuthenticated,))
def diet_tracker_post(request):
    user = request.user
    if user.role == User.CLIENT or user.role == User.SALES:
        meal_type = request.data.get('mealType', None)
        if user.role == User.CLIENT:
            customer = user
        else:
            cid = request.data.get('customer', None)
            if cid is not None:
                try:
                    customer = User.objects.get(id=cid,role=User.CLIENT)
                except User.DoesNotExist:
                    return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
            # return Response({'error' : "provided customer:id in params"}, status=status.HTTP_401_UNAUTHORIZED)

        if meal_type is not None:
            try:
                meal = Meal.objects.get(name=meal_type)
            except Meal.DoesNotExist:
                return Response({"error" : "Meal Type not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error" : "meal type cannot be empty"})

        data = request.data.copy()
        data['meal'] = meal.id
        data['customer'] = customer.id
        if request.data.get('date', None) is None:
            data['date'] = datetime.datetime.today().strftime('%Y-%m-%d')
        # if request.method == 'POST':
        #     serializer = DietTrackerSerializer(data=data)
        # else:
        instance, created = DietTracker.objects.get_or_create(customer=customer,meal=meal,date=data['date'])
        serializer = DietTrackerSerializer(instance, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
            update_date(instance,'diet')
            return Response({'success': 'Successfull', 'data' : serializer.data})
        else:
            return Response({'error' : serializer.errors})
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

# current day's medicine
@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def medicine_get(request):
    user = request.user
    if not user.role == User.HOSPITAL_MANAGER:
        # from calender
        date = request.query_params.get('date', None)
        cid = user.id if user.role == User.CLIENT else request.query_params.get('customer', None)
        
        if cid is None:
            return Response({"Error" : "Provide id in params as customer:id"}, status=status.HTTP_400_BAD_REQUEST)
        # if date == None:
        #     date = datetime.datetime.now()
        # else:
        #     date = datetime.datetime.strptime(date, '%Y-%m-%d')
        date = date if date is not None else datetime.datetime.now().date()
        data = MedicineTime.objects.all().prefetch_related(
            Prefetch('Medicines',queryset=Medicines.objects.filter(customer=cid, date__lte=date)),
            Prefetch('Medicines__MedicineDetail',queryset=TakenMedicine.objects.filter(date=date))
        )
        serializer = MedicineTimeSerializer(data, many=True)
        return Response(serializer.data)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


# customers full medicine detail
@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def all_medicines(request):
    user = request.user
    if not user.role == User.HOSPITAL_MANAGER:
        cid = user.id if user.role == User.CLIENT else request.query_params.get('customer', None)
        # cid = 5
        if cid is not None:
            # ? new response
            data = TakenMedicine.objects.filter(customer=cid, taken=True).prefetch_related('medicine', 'medicine__time').order_by('-date')
            serializer = TakenMedicineSerializer(data, many=True)
            #  ? old response
            # data = MedicineTime.objects.all().prefetch_related(
            #     Prefetch('Medicines',queryset=Medicines.objects.filter(customer=cid, MedicineDetail__taken=True)),
            #     Prefetch('Medicines__MedicineDetail',queryset=TakenMedicine.objects.filter(taken=True,customer=cid))
            # )
            # serializer = MedicineTimeDisplaySerializer(data, many=True, context={'customer':cid})
            return Response(serializer.data)
        else:
            return Response({"Error" : "Customer is not provided"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


# add new medicine
@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def medicine_post(request):
    user = request.user
    if user.role == User.CLIENT or user.role == User.SALES:
        data = request.data.copy()
        if user.role == User.CLIENT:
            data['customer'] = user.id
        else:
            cid = request.data.get('customer', None)
            if cid is not None:
                try:
                    customer = User.objects.get(id=cid)
                    data['customer'] = customer.id
                except User.DoesNotExist:
                    return Response({'error' : 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'error' : 'provide customer in data'}, status=status.HTTP_400_BAD_REQUEST)

        medTime = request.data.get('medicationTime', None)
        if medTime is not None:
            try:
                med_time = MedicineTime.objects.get(name=medTime)
            except MedicineTime.DoesNotExist:
                return Response({"error" : "Medicine Time not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error" : "Medicine Time cannot be empty"})

        data['time'] = med_time.id
        serializer = AddMedicineSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
            update_date(instance,"medicine")
            return Response({'Success': 'Successfull', 'data': serializer.data})
        else:
            return Response({'Error': serializer.errors})
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


# Update taken medicines
@api_view(['POST','PATCH'])
@permission_classes((IsAuthenticated,))
def medicine_update(request):
    user = request.user
    if user.role == User.SALES or user.role == User.CLIENT:
        date = request.data.get('date', None)
        medicine = request.data.get('medicine', None)
        taken = request.data.get('taken', None)
        if user.role == User.CLIENT:
            customer = request.user
        else:
            customer = request.data.get('customer', None)
            if customer is None:
                return Response({"Error" : "Provide 'customer':id in data"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                customer = User.objects.get(id=customer)
            except User.DoesNotExist:
                return Response({"Error" : "customer not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            med = Medicines.objects.get(id=medicine)
        except Medicines.DoesNotExist:
            return Response({"Error" : "Medicine not found"}, status=status.HTTP_404_NOT_FOUND)

        if date and taken is not None:
            instance, created = TakenMedicine.objects.get_or_create(medicine=med, date=date, customer=customer,
            defaults={'taken': taken})
            if not created: #then its False, so delete the entry
                instance.taken = taken
                instance.save()
            update_date(instance, "medicine")
            return Response({'succes':'Medicine Updated successfuly'}, status=status.HTTP_202_ACCEPTED)

        else:
            return Response({"Error" : "Date/taken data not provided"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST','PATCH'])
@permission_classes((IsAuthenticated,))
def medicine_multiple_update(request):
    user = request.user
    if user.role == User.SALES or user.role == User.CLIENT:
        if user.role == User.CLIENT:
            customer = request.user
        else:
            customer = request.data.get('customer', None)
            if customer is None:
                return Response({"Error" : "Provide 'customer':id in data"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                customer = User.objects.get(id=customer)
            except User.DoesNotExist:
                return Response({"Error" : "customer not found"}, status=status.HTTP_404_NOT_FOUND)

        for obj in request.data:
            date = obj.get('date', None)
            medicine = obj.get('medicine', None)
            taken = obj.get('taken', None)
            
            try:
                med = Medicines.objects.get(id=medicine)
            except Medicines.DoesNotExist:
                return Response({"error" : "medicine not found"}, status=status.HTTP_404_NOT_FOUND)

            if date and taken is not None:
                instance, created = TakenMedicine.objects.get_or_create(medicine=med, date=date, customer=customer,
                defaults={'taken': taken})
                if not created: #then its False, so delete the entry
                    instance.taken = taken
                    instance.save()
        return Response({'succes':'Medicine Updated successfuly'}, status=status.HTTP_202_ACCEPTED)
        update_date(instance, "medicine")
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_symptoms(request):
    user = request.user
    if not user.role == User.HOSPITAL_MANAGER:
        date = request.query_params.get('date', None)
        cid = user.id if user.role == User.CLIENT else request.query_params.get('customer', None)
        if cid is None:
            return Response({"Error" : "Specify 'customer':id in params"}, status=status.HTTP_400_BAD_REQUEST)
        if date == None:
            date = datetime.datetime.now().date()
        else:
            date = datetime.date.fromisoformat(date)
        try:
            customer = User.objects.get(id=cid)
        except User.DoesNotExist:
            return Response({'user':'Customer does not exists'}, status=status.HTTP_404_NOT_FOUND)

        symptoms = Symptoms.objects.all().prefetch_related(
            Prefetch('positive_symptom', queryset=PositiveSymptoms.objects.filter(date=date,positive=True,customer=cid))
        )
        # queryset=PositiveSymptoms.objects.filter(positive=True,date=date,customer=cid).prefetch_related('symptom')

        custom = CustomSymptoms.objects.filter(customer=customer).prefetch_related(
            Prefetch('positive_custom_symptom', queryset=PositiveCustomSymptoms.objects.filter(date=date,positive=True,symptom__customer=cid))
        )
        queryset2 = PositiveCustomSymptoms.objects.filter(positive=True,date=date,symptom__customer=cid).prefetch_related('symptom')

        inputs = SymptomsInput.objects.filter(customer=customer,date=date)
        serializer = SymptomSerializer(symptoms ,many=True) #, context={'queryset' : queryset}
        
        CustomSerializer = CustomSymptomSerializer(custom, many=True, context={'queryset' : queryset2}) #, context={'queryset' : queryset2}
        inputSerializer = SymptomsInputSerializer(inputs, many=True)
        # report
        from_last_week = date - timedelta(days=7)
        last_week_positive_symptoms = PositiveSymptoms.objects.filter(date__range=[from_last_week,date],customer=cid,positive=True).prefetch_related('symptom').values('symptom__name').annotate(count=Count('symptom'))
        last_week_symptom_serializer = LastWeekReport(last_week_positive_symptoms,many=True)

        # custom symptoms report
        last_week_positive_custom_symptoms = PositiveCustomSymptoms.objects.filter(date__range=[from_last_week,date],symptom__customer=cid,positive=True).prefetch_related('symptom').values('symptom__name').annotate(count=Count('symptom'))
        last_week_custom_symptom_serializer = LastWeekReport(last_week_positive_custom_symptoms,many=True)
        # report end
        return Response({
            "Symptoms" : serializer.data,
            'customSymptom' : CustomSerializer.data,
            "symptomsWithIputs" : inputSerializer.data,
            "last_week_symptom_report" : last_week_symptom_serializer.data,
            "last_week_custom_symptom_report" : last_week_custom_symptom_serializer.data
        })
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

# add new symptoms
@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def add_symptoms(request):
    user = request.user
    if user.role == User.CLIENT or user.role == User.SALES:
        if user.role == User.CLIENT:
            customer = user
        else:
            customer = request.data.get('customer', None)
            try:
                customer = User.objects.get(id=customer)
            except User.DoesNotExist:
                return Response({"error" : "customer not fount"}, status=status.HTTP_404_NOT_FOUND)
        # data['customer'] = user.id
        data = request.data.copy()
        data['customer'] = customer.id
        serializer = CustomSymptomSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
            return Response({'Success': 'Symptom added successfuly'})
        else:
            return Response({'Error': serializer.errors})
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST','PATCH'])
@permission_classes((IsAuthenticated,))
def symptom_submit(request):
    user = request.user
    if user.role == User.CLIENT or user.role == User.SALES:
        positive = request.data.get('positive', None)
        date = request.data.get('date', None)
        symptom_id = request.data.get('symptom', None)
        if user.role == User.CLIENT:
            customer = user
        else:
            customer = request.data.get('customer', None)
            try:
                customer = User.objects.get(id=customer)
            except User.DoesNotExist:
                return Response({"error" : "customer not fount"}, status=status.HTTP_404_NOT_FOUND)
        try:
            symptom = Symptoms.objects.prefetch_related('criticality').get(id=symptom_id)
        except Symptoms.DoesNotExist:
            return Response({"error" : "symptom not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            symptom = Symptoms.objects.prefetch_related('criticality').get(id=symptom_id)
        except Symptoms.DoesNotExist:
            return Response({"error" : "symptom not found"}, status=status.HTTP_404_NOT_FOUND)
        if date and symptom_id is not None:
            instance, created = PositiveSymptoms.objects.get_or_create(symptom=symptom,customer=customer, date=date,defaults={'positive' : positive})
            if not created:
                instance.positive = positive
                instance.save()
            # update_date(instance, 'symptom')
            # criticality change
            if positive and symptom.criticality: #True/checked
                instance, created = CriticalityChange.objects.get_or_create(customer=customer,criticallity=symptom.criticality,date=date)
            else: #False/unchecked
                # check if there is other symptoms with same criticality,
                # if yes dont delete the criticality change
                # else delelete it.
                criticality_change = PositiveSymptoms.objects.filter(customer=customer,symptom__criticality=symptom.criticality,date=date,positive=True)
                if not criticality_change:
                    CriticalityChange.objects.filter(customer=customer,criticallity=symptom.criticality,date=date).delete()
        update_date(instance, 'symptom')
        return Response({"success" : "successfuly updated"})
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST','PATCH'])
@permission_classes((IsAuthenticated,))
def symptom_submit_array(request):
    user = request.user
    if user.role == User.CLIENT or user.role == User.SALES:
        if user.role == User.CLIENT:
            customer = user
        else:
            customer = request.data.get('customer', None)
            try:
                customer = User.objects.get(id=customer)
            except User.DoesNotExist:
                return Response({"error" : "customer not fount"}, status=status.HTTP_404_NOT_FOUND)
        # try:
        #     symptom = Symptoms.objects.prefetch_related('criticality').get(id=symptom_id)
        # except Symptoms.DoesNotExist:
        #     return Response({"error" : "symptom not found"}, status=status.HTTP_404_NOT_FOUND)
        
        for object in request.data:
            date = object.get('date', None)
            symptom_id = object.get('symptom', None)
            positive = object.get('positive', None)
            try:
                symptom = Symptoms.objects.prefetch_related('criticality').get(id=symptom_id)
            except Symptoms.DoesNotExist:
                return Response({"error" : "symptom not found"}, status=status.HTTP_404_NOT_FOUND)

            if date and symptom_id is not None:
                instance, created = PositiveSymptoms.objects.get_or_create(symptom=symptom,customer=customer, date=date,defaults={'positive' : positive})
                if not created:
                    instance.positive = positive
                    instance.save()
                # update_date(instance, 'symptom')
                # criticality change
                if positive and symptom.criticality: #True/checked
                    instance, created = CriticalityChange.objects.get_or_create(customer=customer,date=date, defaults={'criticallity' : symptom.criticality})
                else: #False/unchecked
                    # check if there is other symptoms with same criticality,
                    # if true dont delete the criticality change
                    # else delelete it.
                    criticality_change = PositiveSymptoms.objects.filter(customer=customer,symptom__criticality=symptom.criticality,date=date,positive=True)
                    if not criticality_change:
                        CriticalityChange.objects.filter(customer=customer,criticallity=symptom.criticality,date=date).delete()
        update_date(instance, 'symptom')
        return Response({"success" : "successfuly updated"})
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['PATCH','POST'])
@permission_classes((IsAuthenticated,))
def submit_custom_symptoms(request):
    user = request.user
    if user.role == User.CLIENT or user.role == User.SALES:
        if user.role == User.CLIENT:
            customer = user.id
        else:
            customer = request.data.get('customer', None)
            try:
                customer = User.objects.get(id=customer)
            except User.DoesNotExist:
                return Response({"error" : "customer not fount"}, status=status.HTTP_404_NOT_FOUND)
        symptom_id = request.data.get('symptom', None)
        date = request.data.get('date', None)
        positive = request.data.get('positive', None)

        if symptom_id and date and positive is not None:
            try:
                custom_symptom = CustomSymptoms.objects.get(id=symptom_id,customer=customer)
            except CustomSymptoms.DoesNotExist:
                return Response({"error" : "custom symptom not found"}, status=status.HTTP_404_NOT_FOUND)
            instance, created = PositiveCustomSymptoms.objects.get_or_create(symptom=custom_symptom,date=date,defaults={'positive':positive})
            if not created:
                instance.positive = positive
                instance.save()
        return Response({"success" : "symptom updated"})
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['PATCH','POST'])
@permission_classes((IsAuthenticated,))
def submit_custom_symptoms_array(request):
    user = request.user
    if user.role == User.CLIENT or user.role == User.SALES:
        if user.role == User.CLIENT:
            customer = user.id
        else:
            customer = request.data.get('customer', None)
            try:
                customer = User.objects.get(id=customer)
            except User.DoesNotExist:
                return Response({"error" : "customer not fount"}, status=status.HTTP_404_NOT_FOUND)
        # symptom_id = request.data.get('symptom', None)
        # date = request.data.get('date', None)
        # positive = request.data.get('positive', None)
        for object in request.data:
            symptom_id = object.get('symptom', None)
            date = object.get('date', None)
            positive = object.get('positive', None)
            if symptom_id and date and positive is not None:
                try:
                    custom_symptom = CustomSymptoms.objects.get(id=symptom_id,customer=customer)
                except CustomSymptoms.DoesNotExist:
                    return Response({"error" : "custom symptom not found"}, status=status.HTTP_404_NOT_FOUND)
                instance, created = PositiveCustomSymptoms.objects.get_or_create(symptom=custom_symptom,date=date,defaults={'positive':positive})
                if not created:
                    instance.positive = positive
                    instance.save()
        return Response({"success" : "symptom updated"})
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST', 'PATCH'])
@permission_classes((IsAuthenticated,))
def submit_symptoms_with_input(request):
    date = request.data.get('date', None)
    if date is not None:
        user = request.user
        if user.role == User.CLIENT or user.role == User.SALES:
            if user.role == User.CLIENT:
                customer = user
            else:
                cid = request.data.get('customer', None)
                try:
                    customer = User.objects.get(id=cid)
                except User.DoesNotExist:
                    return Response({"error":"Customer not found"}, status=status.HTTP_404_NOT_FOUND)

            data = request.data.copy()
            data['customer'] = customer.id
            if request.method == 'PATCH':
                instance, created = SymptomsInput.objects.get_or_create(customer=customer,date=date)
                serializer = SymptomsInputSerializer(instance, data=data, partial=True)
            else:
                serializer = SymptomsInputSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error' : 'date is not provided'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def all_dates_symptoms(request):
    user = request.user
    if user.role:
        cid = user.id if user.role == User.CLIENT else request.query_params.get('customer', None)

        date = request.query_params.get('date', None)

        print(date)

        if date == None:
            date = datetime.datetime.now().date()
        else:
            date = datetime.date.fromisoformat(date)


        if cid is not None:

            # ? new response
            symptoms_data = PositiveSymptoms.objects.filter(customer=cid, positive=True).prefetch_related('symptom').order_by('-date')
            symptoms_serializer = PositiveSymptomsSerializer(symptoms_data, many=True)

            data_with_input = SymptomsInput.objects.filter(customer=cid).order_by('-date')
            data_with_input_serializer = SymptomsInputDisplaySerializer(data_with_input, many=True)

            custom_symptoms_data = PositiveCustomSymptoms.objects.filter(symptom__customer=cid, positive=True).prefetch_related('symptom').order_by('-date')
            custom_symptoms_serializer = PositiveSymptomDisplaySerializer(custom_symptoms_data, many=True)
            
            
            from_last_week = date - timedelta(days=7)



            last_week_positive_symptoms = PositiveSymptoms.objects.filter(date__range=[from_last_week,date],customer=cid,positive=True).prefetch_related('symptom').values('symptom__name').annotate(count=Count('symptom'))
            last_week_symptom_serializer = LastWeekReport(last_week_positive_symptoms,many=True)
           

            # ? old response
            # symptoms_data = Symptoms.objects.all().prefetch_related(
            #     Prefetch('positive_symptom', queryset=PositiveSymptoms.objects.filter(customer=cid,positive=True))
            # )
            # symptoms_serializer = SymptomsDisplaySerializer(symptoms_data, many=True)

            # custom_symptoms_data = CustomSymptoms.objects.filter(customer=cid)
            # custom_symptoms_serializer = CustomSymptomDisplaySerializer(custom_symptoms_data, many=True)

            return Response({
                "symptoms" : symptoms_serializer.data,
                "symptoms_with_text" : data_with_input_serializer.data,
                'custom_symptoms' : custom_symptoms_serializer.data,
                'last_week_symptom' : last_week_symptom_serializer.data
            })
        else:
            return Response({"Error" : "customer not provided"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
@parser_classes([FormParser,MultiPartParser])
def add_medical(request):
    user = request.user
    if user.role == User.CLIENT or user.role == User.SALES:
        # data = request.data.copy()
        if user.role == User.CLIENT:
            customer = user
        else:
            customer_id = request.data.get('customer', None)
            try:
                customer = User.objects.get(id=customer_id, role=User.CLIENT)
            except:
                return Response({'error' : 'client not found'}, status=status.HTTP_404_NOT_FOUND)

        if customer is None:
            return Response({"Error" : "Specify 'customer':id in params"}, status=status.HTTP_400_BAD_REQUEST)

        date_from_body = request.data.get('date', None)
        #     data['date'] = datetime.datetime.today().strftime('%Y-%m-%d')
        
        date = date_from_body if date_from_body is not None and date_from_body != "" else datetime.datetime.today().strftime('%Y-%m-%d')
        try:
            medical_data = Medical.objects.get(customer=customer, date=date)
            serializer = MedicalSerializer(medical_data, data=request.data, context={'request' : request})
        except Medical.DoesNotExist:
            serializer = MedicalSerializer(data=request.data, context={'request' : request})
        if serializer.is_valid(raise_exception=True):
            serializer.save(date=date, customer=customer)
            return Response(serializer.data)
        else:
            return Response({'error' : serializer.error})
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_all_medical_details(request):
    user = request.user
    if not user.role == User.HOSPITAL_MANAGER:
        cid = user.id if user.role == User.CLIENT else request.query_params.get('customer', None)
        if cid is not None:
            investigation_data = Investigation.objects.filter(customer=cid).order_by('-date')
            serializer = InvestigationSerializer(investigation_data, many=True)

            custom_data = CustomInvestigation.objects.filter(customer=cid).order_by('-date')
            custom_serializer = CustomInvestigationSerializer(custom_data, many=True)
            return Response({
                'investigation_data' : serializer.data,
                'custom_investigation' : custom_serializer.data
            })
        else:
            return Response({'error' : "customer : id not provided in params"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_medical_details(request):
    user = request.user
    if not user.role == User.HOSPITAL_MANAGER:
        params_date = request.query_params.get('date', None)
        cid = user.id if user.role == User.CLIENT else request.query_params.get('customer', None)
        date = params_date if params_date is not None else datetime.datetime.now().date()
        if cid is not None and cid != '':
            investigation_data = Investigation.objects.filter(customer=cid,date=date).prefetch_related('criticallity')
            if investigation_data:
                serializer = InvestigationSerializer(investigation_data.first())
                data = serializer.data
            else:
                data = {}
            custom_data = CustomInvestigation.objects.filter(customer=cid, date=date)
            custom_serializer = CustomInvestigationSerializer(custom_data, many=True)
            return Response({
                'investigation_data' : data,
                'custom_investigation' : custom_serializer.data
            })
        else:
            return Response({'error' : "customer : id not provided in params"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_medical_form_data(request):
    user = request.user
    param_date = request.query_params.get('date', None)
    date = param_date if param_date is not None else datetime.datetime.now().date()
    if user.role == User.CLIENT:
        client_id = user
    elif user.role == User.SALES:
        id = request.query_params.get('customer', None)
        try:
            client_id = User.objects.get(id=id, role=User.CLIENT)
        except User.DoesNotExist:
            return Response({'error' : 'client not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)    
    try:
        medical = Medical.objects.filter(customer=client_id.id, date=date).latest('id')
    except Medical.DoesNotExist:
        return Response({'error' : 'no data found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = MedicalSerializer(medical, context={'request' : request})
    return Response(serializer.data)


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def add_contraction(request):
    user = request.user
    if user.role == User.CLIENT:
        pain = request.data.get('painScale', None)
        time = request.data.get('time', None)
        data = request.data.copy()
        data['customer'] = request.user.id
        contraction = request.data.get('contraction', None)
        if contraction is not None:
            contraction_list = contraction.split(":")
            contraction_inSeconds = int(contraction_list[0]) * 60 + int(contraction_list[1])
            data['contraction'] = contraction_inSeconds

        # to assign the pain scale value
        # try:
        #     pain_scale = PainScale.objects.get(name__iexact=pain)
        # except PainScale.DoesNotExist:
        #     return Response({"error" : "pain scale not found"}, status=status.HTTP_404_NOT_FOUND)
        # data['painScale'] = pain_scale.id

        # to set the interval
        previous_data = Contraction.objects.filter(customer=user.id ,date=make_aware(datetime.datetime.now()))
        if previous_data:
            latest_contraction = previous_data.latest('time_stamp')
            date = datetime.datetime.now().date()
            datetime1 = datetime.datetime.combine(date, datetime.datetime.strptime(time, "%H:%M:%S").time())
            datetime2 = datetime.datetime.combine(date, latest_contraction.time)
            interval = datetime1 - datetime2
            data['interval'] = interval
            # print(interval)
            # print(latest_contraction.time)
        else:
            data['interval'] = 0

        serializer = ContractionSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
            update_date(instance, "contraction")
            return Response(serializer.data)
        else:
            return Response({"error" : serializer.errors})
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_contraction(request):
    user = request.user
    if not user.role == User.HOSPITAL_MANAGER:
        date = request.query_params.get('date', None)
        if date is None:
            date = datetime.datetime.now().date()
        user = request.user
        cid = user.id if user.role == User.CLIENT else request.query_params.get('customer', None)
        if cid is not None:
            contraction_data = Contraction.objects.filter(customer=cid,date=date)
            serializer = ContractionSerializer(contraction_data, many=True)
            return Response(serializer.data)
        else:
            return Response({"error" : "customer : id not provided in params"})
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

# all dates contraction
@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def all_dates_contractions(request):
    # customer = request.query_params.get('customer', None)
    user = request.user
    if not user.role == User.HOSPITAL_MANAGER:
        customer = user.id if user.role == User.CLIENT else request.query_params.get('customer', None)
        if customer is not None:
            data = Contraction.objects.filter(customer=customer).order_by('-date', '-time')
            serializer = ContractionDisplaySerializer(data, many=True)
            return Response(serializer.data)
        else:
            return Response({"Error" : "customer not provided"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def scan_dates(request):
    # id = request.query_params.get('customer', None)
    user = request.user
    if user.role == User.CLIENT:
        id = user.id
        if id is not None:
            try:
                customer = User.objects.get(id=id)
            except User.DoesNotExist:
                return Response({"Error" : "Customer not found.!"}, status=status.HTTP_404_NOT_FOUND)

            details = customer.customer_details.first()

            # consulting doctor
            try:
                # DocDetails = DoctorDetails.objects.get(id=details.referalId.id)
                DocDetails = details.referalId
                consultingDoctor = DocDetails.user.firstname + " " + DocDetails.user.lastname
            except DoctorDetails.DoesNotExist:
                consultingDoctor = ""

            # customer's last menstruation date
            menstruation_date = details.Menstruation_date

            # Due date (40 weeks)
            dueDate = menstruation_date + timedelta(days=280) #40*7 = 280 days

            # probable date of conception (2 weeks after mensutral date)
            probableDate = menstruation_date + timedelta(days=14)

            # foetal age
            # today = date.today()
            week, daysCompleted, daysLeft = foetal_age(menstruation_date, date.today())

            # Dating scan
            # from 7th to 8th week
            dating_scan_from = menstruation_date + timedelta(days=49)
            dating_scan_to = menstruation_date + timedelta(days=56)

            dating_scan = scan_date_to_string(dating_scan_from, dating_scan_to)

            # Nt scan
            # from 12 week 3 days to 13 week 3 days
            nt_scan_from = menstruation_date + timedelta(days=87)
            nt_scan_to = menstruation_date + timedelta(days=94)

            nt_scan = scan_date_to_string(nt_scan_from, nt_scan_to)

            # morphology scan
            # 19th week ( 18th to 19th week)
            morphology_scan_from = menstruation_date + timedelta(days=126)
            morphology_scan_to = menstruation_date + timedelta(days=133)

            morphology_scan = scan_date_to_string(morphology_scan_from, morphology_scan_to)

            # Anomaly scan
            # 20-22th week
            anomaly_scan_from = menstruation_date + timedelta(days=140)
            anomaly_scan_to = menstruation_date + timedelta(days=154)

            anomaly_scan = scan_date_to_string(anomaly_scan_from, anomaly_scan_to)

            # growth scan
            # 32 to 34th week
            growth_scan_from = menstruation_date + timedelta(days=224)
            growth_scan_to = menstruation_date + timedelta(days=238)

            growth_scan = scan_date_to_string(growth_scan_from, growth_scan_to)




            context = {
                "doctor" : consultingDoctor,
                'dueDate' : dueDate.strftime("%d-%m-%Y"),
                "lastMenstrualDate" : menstruation_date.strftime("%d-%m-%Y"),
                "probableDate" : probableDate.strftime("%d-%m-%Y"),
                "foetal_week" : week,
                "foetal_days" : daysCompleted,
                "datingScan" : dating_scan,
                "ntScan"  : nt_scan,
                "morphologyScan" : morphology_scan,
                "anomalyScan" : anomaly_scan,
                "growthScan" : growth_scan,
                # "lastScan" : scanName,
                # "lastScanDetails" :   lastScanDate.strftime('%d/%B/%Y') + " - {Scan_Week} Weeks and {Scan_DaysCompleted} days old. " .format(Scan_Week=Scan_Week, Scan_DaysCompleted=Scan_DaysCompleted)
            }
            # if no investigation
            try:
                lastScan = Investigation.objects.filter(scan__isnull=False, customer=id).latest('date')
                lastScanDate = lastScan.date
                scanName = lastScan.scan
                Scan_Week, Scan_DaysCompleted, Scan_DaysLeft = foetal_age(menstruation_date, lastScanDate)
                lastScan = scanName
                lastScanDetails = lastScanDate.strftime('%d/%B/%Y') + " - {Scan_Week} Weeks and {Scan_DaysCompleted} days old. " .format(Scan_Week=Scan_Week, Scan_DaysCompleted=Scan_DaysCompleted)
                context.update({'ultraSound' : lastScan, 'lastScanDetails' : lastScanDetails})
            except:
                pass
            return Response(context)
        else:
            return Response({"Error" : "Id not provided"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


# Excersice or Activity adding function
@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def add_modules(request):
    user = request.user
    if user.role == User.ADMIN:
        context = {}
        module = request.data.get('tracker', None)
        stageName = request.data.get('stage', None)
        update = request.data.get('update', None)
        subModule = request.data.get('subModuleName', None)
        admin_added_main_module = request.data.get('mainModule', None)

        try:
            stage = Stage.objects.get(name=stageName)
        except Stage.DoesNotExist:
            return Response({"Erro" : "selected stage not found"}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['stage'] = stage.id

        if module is not None:
            if module.lower() == 'activity':
                data['name'] = admin_added_main_module
                if update == 'True': #if update, then get the main modules and set id in data
                    try:
                        mainModule = ActivityMainModule.objects.get(name=admin_added_main_module,stage=stage.id)
                    except ActivityMainModule.DoesNotExist:
                        return Response({"Error" : "mainModule not found"}, status=status.HTTP_404_NOT_FOUND)
                else: #add the main module as new entry
                    mainModuleSerializer = AddActivityMainModuleSerializer(data=data)
                    if mainModuleSerializer.is_valid():
                        mainModule = mainModuleSerializer.save()
                        context['mainModule'] =  "Main Module added successfully"
                    else:
                        return Response(mainModuleSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

                if subModule is not None:
                    data['ActivityMainModule'] = mainModule.id
                    subModuleSerializer = DailyTrackerSubModulesSerializer(data=data)
                    if subModuleSerializer.is_valid():
                        subModuleSerializer.save()
                        context['subModule'] = "Sub Module added successfully"
                    else:
                        return Response(subModuleSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

            else: #its exercise
                context = {}
                url = request.data.get('url', None)
                exercise = request.data.get('exercise', None)
                if exercise is not None and len(exercise.replace(" ", "")) != 0:
                    try:
                        instance = Exercises.objects.create(stage=stage,name=exercise)
                        context['exercise'] = "exercise added successfully"
                    except:
                        return Response({'error' : 'exercise already exists, so not added'}, status=status.HTTP_400_BAD_REQUEST)

                if url is not None:
                    instance, created = ExerciseVideos.objects.get_or_create(stage=stage, defaults={'url':url})
                    if not created:
                        instance.url = url
                        instance.save()
                    context['url'] = "url added successfully"
                return Response(context)
        else:
            return Response({'error' : "Tracker field is empty"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)






    return Response(context, status=status.HTTP_201_CREATED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_activity_main_modules(request):
    user = request.user
    if user.role == User.ADMIN:
        stageName = request.query_params.get('stage', None)
        if stageName is not None:
            try:
                stage = Stage.objects.get(name=stageName)
            except Stage.DoesNotExist:
                return Response({'error' : "stage not found"}, status=status.HTTP_404_NOT_FOUND)

            mainModules = ActivityMainModule.objects.filter(stage=stage.id)
            serializer = GetActivityMainModuleSerializer(mainModules, many=True)

            return Response(serializer.data)
        else:
            return Response({
                "error" : "stage field empty"
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


# single days data
@api_view(['GET',])
@permission_classes([IsAuthenticated])
def get_activity(request): #Excercise
    user = request.user
    if not user.role == User.HOSPITAL_MANAGER:
        if user.role == User.CLIENT:
            customer = request.user.id
        else:
            customer = request.query_params.get('customer', None)
        # change date if its provided in params
        date2 = request.query_params.get('date', None)
        today = datetime.datetime.today()
        if date2 is not None:
            today = date2

        if customer is None:
            return Response({"Error" : "Specify 'customer':id in params"}, status=status.HTTP_400_BAD_REQUEST)
        # if module is not None:
        try:
            details = CustomerDetails.objects.get(user=customer)
        except CustomerDetails.DoesNotExist:
            return Response({"Error" : "Customer not found.Invliad id."}, status=status.HTTP_404_NOT_FOUND)
        periods_date =  details.Menstruation_date
        stage_id = calculate_stage(periods_date) #returns stage id

        if user.role == User.CLIENT:
            main_module_data = ActivityMainModule.objects.filter(stage=stage_id,disabled=False).prefetch_related(
                Prefetch('sub_module', queryset=ActivitySubModules.objects.filter(disabled=False)),
                Prefetch('sub_module__Completed_activity', queryset=CompletedActivity.objects.filter(date=today,completed=True)),
            ) 
        else:
            main_module_data = ActivityMainModule.objects.filter(stage=stage_id).prefetch_related(
                Prefetch('sub_module', queryset=ActivitySubModules.objects.all()),
                Prefetch('sub_module__Completed_activity', queryset=CompletedActivity.objects.filter(date=today,completed=True)),
            )

        custom = CustomActivity.objects.filter(customer=customer).prefetch_related(
            Prefetch('completedCustom', queryset=CompletedCustomActivity.objects.filter(date=today,completed=True))
        )

        serializer = ActivityMainModuleSerializer(main_module_data, many=True)
        customSerializer = CustomActivitySerilializer(custom, many=True)

        return Response({
                "predefined" : serializer.data,
                "custom" : customSerializer.data,
                # "customized" : customizedSerializer.data # + Mod.name.capitalize()
            })
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST','PATCH'])
@permission_classes([IsAuthenticated,])
def submit_activity(request):
    user = request.user
    if user.role == User.CLIENT or user.role == User.SALES:
        date = request.data.get('date', None)
        id = request.data.get('id', None) #sub module id
        completed = request.data.get('completed', False)
        # is_custom = request.data.get('is_custom', False)
        if request.user.role == User.CLIENT:
            customer = request.user.id
        else:
            customer = request.data.get('customer', None)
        if customer is None:
            return Response({"Error" : "Specify 'customer':id in data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                user = User.objects.get(id=customer)
            except User.DoesNotExist:
                return Response({"Error" : "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        if date is not None:
            try:
                submodule = ActivitySubModules.objects.get(id=id) #todo add prefetch related and uncomment "UpdateDate()"
            except ActivitySubModules.DoesNotExist:
                return Response({"Error" : "Sub module not found"}, status=status.HTTP_404_NOT_FOUND)
            instance, created = CompletedActivity.objects.get_or_create(
                customer=user,daily_tracker_submodules=submodule, date=date,
                defaults=({'completed' : completed})
            )
            # UpdateDate(instance, submodule.DailyTrackerMainModule.dailyTrackerModule.name)
            if not created:
                instance.completed = completed
                instance.save()
        else:
            return Response({"Error" : "Date not provided"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"success" : "Successfully Updated."})
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST','PATCH'])
@permission_classes([IsAuthenticated,])
def submit_activity_array(request):
    user = request.user
    if user.role == User.CLIENT or user.role == User.SALES:
        if request.user.role == User.CLIENT:
            customer = request.user.id
        else:
            customer = request.data.get('customer', None)
        if customer is None:
            return Response({"Error" : "Specify 'customer':id in data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                user = User.objects.get(id=customer)
            except User.DoesNotExist:
                return Response({"Error" : "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        for object in request.data:
            date = object.get('date', None)
            id = object.get('id', None) #sub module id
            completed = object.get('completed', False)
            if date and id is not None:
                try:
                    submodule = ActivitySubModules.objects.get(id=id) #todo add prefetch related and uncomment "UpdateDate()"
                except ActivitySubModules.DoesNotExist:
                    return Response({"Error" : "Sub module not found"}, status=status.HTTP_404_NOT_FOUND)
                instance, created = CompletedActivity.objects.get_or_create(
                    customer=user,daily_tracker_submodules=submodule, date=date,
                    defaults=({'completed' : completed})
                )
                # UpdateDate(instance, submodule.DailyTrackerMainModule.dailyTrackerModule.name)
                if not created:
                    instance.completed = completed
                    instance.save()
        return Response({"success" : "Successfully Updated."})
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

# display all activity data
@api_view(['GET',])
@permission_classes([IsAuthenticated,])
def display_all_activity(request):
    # module = request.query_params.get('module', None)
    user = request.user
    # print(not user.HOSPITAL_MANAGER)
    if not user.role == User.HOSPITAL_MANAGER:
        customer = user.id if user.role == User.CLIENT else request.query_params.get('customer', None)
        if customer is not None:
            # ? new reponse
            activities = CompletedActivity.objects.filter(customer=customer, completed=True).prefetch_related(
                'daily_tracker_submodules', 'daily_tracker_submodules__ActivityMainModule'
            ).order_by('-date')

            serializer =  ActivityDisplaySerializer(activities, many=True)

            customActivities = CompletedCustomActivity.objects.filter(activity__customer=customer, completed=True).order_by('-date')
            customerSerializer = CompletedCustomActivitySerializer(customActivities, many=True)
            return Response({
                "Predefined" : serializer.data,
                "Custom" : customerSerializer.data
                })
        else:
            return Response({"Error" : "Specify 'customer':id in params"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST',])
@permission_classes([IsAuthenticated,])
def add_custom_activity(request):
    # cid = request.data.get('customer', None)
    user = request.user
    if user.role == User.CLIENT or user.role == User.SALES:
        data = request.data.copy()
        date = request.data.get('date', None)
        if user.role == User.CLIENT:
            customer = user
        else:
            customer = request.data.get('customer', None)
            try:
                customer = User.objects.get(id=customer)
            except User.DoesNotExist:
                return Response({"error" : "customer not fount"}, status=status.HTTP_404_NOT_FOUND)
        # if request.data.get('date', None) is None:
        #     data['date'] = datetime.datetime.today().strftime('%Y-%m-%d')
        data['customer'] = customer.id

        if date is None:
            date = datetime.datetime.today().date()
        # try:
        #     customer = User.objects.get(id=cid)
        # except User.DoesNotExist:
        #     return Response({"Error" : "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        # try:
        #     module = DailyTrackerModule.objects.get(name=mod)
        # except:
        #     return Response({"Error" : "Module not found"}, status=status.HTTP_400_BAD_REQUEST)

        data["date"] = date
        # data['DailyTrackerModule'] = module.id # exercise/activity
        data['customer'] = customer.id
        # print(data)
        serializer = CustomActivitySerilializer(data=data)
        if serializer.is_valid():

            instance = serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST',])
@permission_classes([IsAuthenticated,])
def submit_custom_activity(request):
    user = request.user
    if user.role == User.SALES or user.role == User.CLIENT:
        date = request.data.get('date', None)
        activity_id = request.data.get('activity', None)
        completed = request.data.get('completed', None)
        if user.role == User.CLIENT:
            customer = user
        else:
            customer = request.data.get('customer', None)
            try:
                customer = User.objects.get(id=customer)
            except User.DoesNotExist:
                return Response({"error" : "customer not fount"}, status=status.HTTP_404_NOT_FOUND)
        try:
            activity = CustomActivity.objects.get(id=activity_id,customer=customer)
        except CustomActivity.DoesNotExist:
            return Response({"error" : "custom activity not found"})

        if date and activity is not None:
            instance, created = CompletedCustomActivity.objects.get_or_create(activity=activity, date=date,defaults={'completed' : completed})
            if not created:
                instance.completed = completed
                instance.save()
            return Response({"success" : "successfuly updated"})
        else:
            return Response({'error' : "date or exercise field empty"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST','PATCH'])
@permission_classes([IsAuthenticated,])
def submit_custom_activity_array(request):
    user = request.user
    if user.role == User.SALES or user.role == User.CLIENT:
        if user.role == User.CLIENT:
            customer = user
        else:
            customer = request.data.get('customer', None)
            try:
                customer = User.objects.get(id=customer)
            except User.DoesNotExist:
                return Response({"error" : "customer not fount"}, status=status.HTTP_404_NOT_FOUND)
        for object in request.data:
            date = object.get('date', None)
            activity_id = object.get('activity', None)
            completed = object.get('completed', None)
            try:
                activity = CustomActivity.objects.get(id=activity_id,customer=customer)
            except CustomActivity.DoesNotExist:
                return Response({"error" : "custom activity not found"})

            if date and activity is not None:
                instance, created = CompletedCustomActivity.objects.get_or_create(activity=activity, date=date,defaults={'completed' : completed})
                if not created:
                    instance.completed = completed
                    instance.save()
        return Response({"success" : "successfuly updated"})
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET',])
@permission_classes([IsAuthenticated,])
def exercise_get(request):
    user = request.user
    if not user.role == User.HOSPITAL_MANAGER:
        context = {}
        date = request.query_params.get('date', None)
        if not date:
            date = datetime.datetime.now().date()
        if user.role == User.CLIENT:
            cid = user.id
        else:
            id = request.query_params.get('customer', None)
            try:
                user = User.objects.get(id=id)
                cid = user.id
            except User.DoesNotExist:
                return Response({"error" : "client not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            client_details = user.customer_details.first()
        except:
            return Response({"error" : "client not found"}, status=status.HTTP_404_NOT_FOUND)   

        stage_id = calculate_stage(client_details.Menstruation_date)
        
        
        if user.role == User.CLIENT:
            # for client dont show the disables exercises
            exercises = Exercises.objects.filter(stage=stage_id,disabled=False).prefetch_related(
                Prefetch('completed_exercise', queryset=CompletedExercises.objects.filter(customer=cid,date=date,completed=True))
            )
        else:
            exercises = Exercises.objects.filter(stage=stage_id).prefetch_related(
                Prefetch('completed_exercise', queryset=CompletedExercises.objects.filter(customer=cid,date=date,completed=True))
            )
        
        custom_exercises = CustomExercises.objects.filter(customer=cid).prefetch_related(
            Prefetch('completed_custom_exercise', queryset=CompletedCustomeExercises.objects.filter(date=date,completed=True))
        )
        serializer = ExerciseSerializer(exercises, many=True)
        custom_serializer = CustomExerciseSerializer(custom_exercises, many=True)
        context['exercises'] = serializer.data
        context['custom'] = custom_serializer.data
        video = ExerciseVideos.objects.filter(stage=stage_id)
        if video:
            video = video.first()
            context['url'] = video.url
        # get calorie
        calorie = CaloriesBurnt.objects.filter(date=date,customer=cid)
        context['calorieBurnt'] = f'{calorie.first().value:.2f}' if calorie else 0
        customized = CustomizedPlan.objects.filter(tracker=CustomizedPlan.EXERCISE,customer=cid)

        # check if empty, if not get the latest from the queryset to serialize
        if not customized:
            customizedSerializer = CustomizedPlanSerializer()
        else:
            customizedSerializer = CustomizedPlanSerializer(customized.latest('time','date'))

        context['customizedExercise'] = customizedSerializer.data

        return Response(context)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST','PATCH'])
@permission_classes([IsAuthenticated,])
def submit_exercise_consent(request):
    user = request.user
    if user.role == User.CLIENT:
        date = request.data.get('date', None)
        changedCriticality = CriticalityChange.objects.filter(customer=user, date__lte=date)
        if changedCriticality and date is not None:
            instance = changedCriticality.latest('date')
            if user.role == User.CLIENT:
                instance = changedCriticality.first()
                instance.consent = True
                instance.save()
                return Response({'success' : 'consent recorded successfuly'})
            else:
                return Response({'error' : "permission denied"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error' : "no criticality change/date not provided"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST','PATCH',])
@permission_classes([IsAuthenticated,])
def submit_exercise(request):
    user = request.user
    if user.role == User.CLIENT or user.role == User.SALES:
        exercise_id = request.data.get('exercise', None)
        completed = request.data.get('completed', None)
        date = request.data.get('date', None)

        if user.role == User.CLIENT:
            customer = request.user
        else:
            cid = request.data.get('customer', None)
            try:
                customer = User.objects.get(id=cid)
            except User.DoesNotExist:
                return Response({"error" : "client not found"}, status=status.HTTP_404_NOT_FOUND)

        # check for consent from client before proceeding
        # criticalityChange = CriticalityChange.objects.filter(customer=customer.id,date__lte=date).prefetch_related('criticallity')
        # if criticalityChange:
        #     latest = criticalityChange.latest('date')
        #     if not latest.consent and latest.criticallity.name.lower() != 'stable':
        #         return Response({'error' : 'accept the consent to proceed'}, status=status.HTTP_403_FORBIDDEN)

        if exercise_id and completed and date is not None:
            try:
                exercise = Exercises.objects.get(id=exercise_id)
            except Exercises.DoesNotExist:
                return Response({"error":"Exercise not found"}, status=status.HTTP_404_NOT_FOUND)

            instance, created = CompletedExercises.objects.get_or_create(customer=customer,exercise=exercise,date=date,defaults={'completed': completed})
            if not created:
                instance.completed = completed
                instance.save()
            return Response({"success" : "Exercise updated successfuly"})
        else:
            return Response({"error" : "completed or exercise or date empty"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST','PATCH',])
@permission_classes([IsAuthenticated,])
def submit_exercise_array(request):
    user = request.user
    if user.role == User.CLIENT or user.role == User.SALES:
        if user.role == User.CLIENT:
            customer = request.user
        else:
            cid = request.data.get('customer', None)
            try:
                customer = User.objects.get(id=cid)
            except User.DoesNotExist:
                return Response({"error" : "client not found"}, status=status.HTTP_404_NOT_FOUND)

        for object in request.data:
            exercise_id = object.get('exercise', None)
            completed = object.get('completed', None)
            date = object.get('date', None)

            if exercise_id and completed and date is not None:
                try:
                    exercise = Exercises.objects.get(id=exercise_id)
                except Exercises.DoesNotExist:
                    return Response({"error":"Exercise not found"}, status=status.HTTP_404_NOT_FOUND)

                instance, created = CompletedExercises.objects.get_or_create(customer=customer,exercise=exercise,date=date,defaults={'completed': completed})
                if not created:
                    instance.completed = completed
                    instance.save()
        return Response({"success" : "Exercise updated successfuly"})
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST','PATCH',])
@permission_classes([IsAuthenticated,])
def add_calories_burnt(request):
    user = request.user
    if user.role == User.CLIENT or user.role == User.SALES:
        date = request.data.get('date', None)
        value = request.data.get('value', None)

        if user.role == User.CLIENT:
            customer = request.user
        else:
            cid = request.data.get('customer', None)
            try:
                customer = User.objects.get(id=cid)
            except User.DoesNotExist:
                return Response({"error" : "client not found"}, status=status.HTTP_404_NOT_FOUND)
        # check for consent from client before proceeding
        # criticalityChange = CriticalityChange.objects.filter(customer=customer.id,date__lte=date).prefetch_related('criticallity')
        # if criticalityChange:
        #     latest = criticalityChange.latest('date')
        #     if not latest.consent and latest.criticallity.name.lower() != 'stable':
        #         return Response({'error' : 'accept the consent to proceed'}, status=status.HTTP_403_FORBIDDEN)

        if date and value is not None:
            instance, created = CaloriesBurnt.objects.get_or_create(customer=customer, date=date, defaults={'value' : value})
            if not created:
                instance.value = value
                instance.save()
            return Response({'success' : "calorie added"})
        else:
            return Response({"error" : "date/value not provided"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST',])
@permission_classes([IsAuthenticated,])
def add_custom_exercise(request):
    user = request.user
    if user.role == User.CLIENT or user.role == User.SALES:
        data = request.data.copy()
        # name = request.data.get('name', None)
        if user.role == User.CLIENT:
            user = request.user
        else:
            cid = request.data.get('customer', None)
            try:
                user = User.objects.get(id=cid)
            except User.DoesNotExist:
                return Response({"error" : "client not found"}, status=status.HTTP_404_NOT_FOUND)
        data['customer'] = user.id
        serializer = CustomExerciseSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST','PATCH'])
@permission_classes((IsAuthenticated,))
def submit_custom_exercise(request):
    user = request.user
    if user.role == User.CLIENT or user.role == User.SALES:
        date = request.data.get('date', None)
        exercise_id = request.data.get('exercise', None)
        completed = request.data.get('completed', None)
        if user.role == User.CLIENT:
            customer = user
        else:
            customer = request.data.get('customer', None)
            try:
                customer = User.objects.get(id=customer)
            except User.DoesNotExist:
                return Response({"error" : "customer not fount"}, status=status.HTTP_404_NOT_FOUND)
        try:
            exercise = CustomExercises.objects.get(id=exercise_id,customer=customer)
        except CustomExercises.DoesNotExist:
            return Response({"error" : "custom exercise not found"})

        # check for consent from client before proceeding
        # criticalityChange = CriticalityChange.objects.filter(customer=customer.id,date__lte=date).prefetch_related('criticallity')
        # if criticalityChange:
        #     latestChange = criticalityChange.latest('date')
        #     if not latestChange.consent and latestChange.criticallity is not None and latestChange.criticallity.name.lower() != 'stable':
        #         return Response({'error' : 'Accept the consent to proceed'}, status=status.HTTP_403_FORBIDDEN)

        if date and exercise is not None:
            instance, created = CompletedCustomeExercises.objects.get_or_create(exercise=exercise, date=date,defaults={'completed' : completed})
            if not created:
                instance.completed = completed
                instance.save()
            return Response({"success" : "successfuly updated"})
        else:
            return Response({'error' : "date or exercise field empty"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST','PATCH'])
@permission_classes((IsAuthenticated,))
def submit_custom_exercise_array(request):
    user = request.user
    if user.role == User.CLIENT or user.role == User.SALES:
        if user.role == User.CLIENT:
            customer = user
        else:
            customer = request.data.get('customer', None)
            try:
                customer = User.objects.get(id=customer)
            except User.DoesNotExist:
                return Response({"error" : "customer not fount"}, status=status.HTTP_404_NOT_FOUND)

        for object in request.data:
            date = object.get('date', None)
            exercise_id = object.get('exercise', None)
            completed = object.get('completed', None)
            try:
                exercise = CustomExercises.objects.get(id=exercise_id,customer=customer)
            except CustomExercises.DoesNotExist:
                return Response({"error" : "custom exercise not found"})

            if date and exercise is not None:
                instance, created = CompletedCustomeExercises.objects.get_or_create(exercise=exercise, date=date,defaults={'completed' : completed})
                if not created:
                    instance.completed = completed
                    instance.save()
        return Response({"success" : "successfuly updated"})
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def all_days_exercises(request):
    user = request.user
    if not user.role == User.HOSPITAL_MANAGER:
        cid = user.id if user.role == User.CLIENT else request.query_params.get('customer', None)
        if cid is not None:
            exercise_data = CompletedExercises.objects.filter(customer=cid, completed=True).prefetch_related('exercise').order_by('-date')
            exercise_serializer = CompletedExercisesDisplaySerializer(exercise_data, many=True)

            custom_exercise_data = CompletedCustomeExercises.objects.filter(exercise__customer=cid).prefetch_related('exercise').order_by('-date')
            custom_exercise_serializer = CompletedCustomExercises(custom_exercise_data, many=True)

            calorie_data = CaloriesBurnt.objects.filter(customer=cid).order_by('-date')
            calorie_serializer = CaloriesBurntSerializer(calorie_data, many=True)

            return Response({
                "exercises" : exercise_serializer.data,
                "customExericises" : custom_exercise_serializer.data,
                "calories" : calorie_serializer.data
            })
        else:
            return Response({"error" : "customer : id in params not found"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

from rest_framework.views import APIView
from Admin.models import FreeContent
from Admin.serializers import FreeContentSerializer

class FreeContentAPI(APIView):

    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            freecontent = FreeContent.objects.all()
            serializer = FreeContentSerializer(freecontent, many = True)
            return Response({
                'status' : True,
                'data' : serializer.data
            })
        except Exception as e:
            return Response({'status' : False ,'details' : {}})