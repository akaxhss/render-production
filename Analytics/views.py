from django.db.models.query import Prefetch
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .serializers import *
from Admin.models import PositiveCriticalSymptoms
from .models import *
from Sales.models import CriticalityChange
from Sales.serializers import CriticalityChangeSerializer
from Customer.models import PositiveSymptoms
from rest_framework.response import Response
# from django.db import connection
from datetime import datetime
from itertools import chain
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your views here.


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_medical_analysis(request):
    user = request.user
    try:
        user = User.objects.get(id=request.query_params.get('customer', None), role=User.CLIENT)
    except User.DoesNotExist:
        return render({"error" : "customer not found"}, status=status.HTTP_404_NOT_FOUND)
        
    total_count = {}
    current_count = {}
    complication_percentage = {}

    age_both =  [ 'early abortion', 'IUGR' ] #age less than 18 and 35+
    age_thirty_five_plus = ['uti', 'placenta preveria', 'placenta abruption', 'preterm', 'oligohydramnios', '	polyhydramnios', 'diabetes', 'HELLP', 'PIH'] #only 35+

    bmi_both = ['early abortion', 'placenta preveria', 'placenta abruption', 'preterm', 'oligohydramnios', 'IUGR'] #overweight and underweight
    bmi_overweight = [ 'hyperemesis gravidarum', 'uti', 'polyhydramnios', 'diabetes', 'HELLP', 'PIH' ] #only overweight

    # get personal details
    try:
        personal_details = PersonalDetails.objects.get(customer=user.id)
    except PersonalDetails.DoesNotExist:
        personal_details = None
    # get all customer medical history
    customer_medical_history = CustomerMedicalHistory.objects.filter(customer=user.id,flag=True).prefetch_related('medical_history','medical_history__complication')
    for medical in customer_medical_history:
        for complication in medical.medical_history.complication.all():
            complication_name = complication.name
            # check if its in current_count
            c = current_count.get(complication_name, None)
            if c is None:
                current_count[complication_name] = 1
            else:    
                current_count[complication_name] += 1

            # add total count
            t = total_count.get(complication_name, None)
            if t is None:
                total_count[complication_name] = complication.medicalhistory_set.count()
                # ? print(total_count)
                if personal_details is not None:
                    # Age based complications
                    age = personal_details.age
                    if age is not None:
                        if age < 18 or age > 35:
                            if complication_name in age_both:
                                total_count[complication_name] += 1
                            if age > 35:
                                if complication_name in age_thirty_five_plus:
                                    total_count[complication_name] += 1
                    
                    #BMI based complications
                    bmi = personal_details.bmi
                    if age is not None:
                        if bmi == PersonalDetails.UNDERWEIGHT or bmi == PersonalDetails.OVERWEIGHT:
                            if complication_name in bmi_both:
                                total_count[complication_name] += 1

                        if bmi == PersonalDetails.OVERWEIGHT:
                            if complication_name in bmi_overweight:
                                total_count[complication_name] += 1

            percentage_value = complication_percentage.get(complication_name, None)
            if percentage_value is None:
                complication_percentage[complication_name.replace(" ", "_")] = round((current_count[complication_name]/total_count[complication_name]) * 100,2 )

    return Response(complication_percentage)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_symptom_analysis(request):
    user = request.user
    client_id = request.query_params.get('customer', None)
    # if user.role == User.DOCTOR and user.role == User.CONSULTANT and user.role == User.CLIENT:
    try:
        client = User.objects.get(id=client_id, role=User.CLIENT)
    except User.DoesNotExist:
        return Response({'error' : 'client error'}, status=status.HTTP_404_NOT_FOUND)
    # else:
        # return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
    total_count = {}
    current_count = {}
    complication_percentage = {
        'still_birth' : 0,
        'covid' : 0,
        'Yeast_Infections' : 0,
        'Anemia' : 0,
        'Fluid_Leak' : 0,
        'cholestatsis' : 0,
        'RH_Incampatability' : 0,
        'IUGR' : 0,
        'PIH' : 0,
        'HELLP' : 0,
        'diabetes' : 0,
        'polyhydramnios' : 0,
        'oligohydramnios' : 0,
        'preterm' : 0,
        'placenta_abruption' : 0,
        'placenta_preveria' : 0,
        'uti' : 0,
        'hyperemesis_gravidarum' : 0,
        'early_abortion' : 0
    }
    query_date = request.query_params.get('date', None) 
    date = query_date if query_date is not None else datetime.now().date()
    # get all customer medical history
    symptoms = PositiveSymptoms.objects.filter(customer=client,positive=True,date=date).prefetch_related(
        'symptom',
        'symptom__complication'
    ).distinct('symptom') #date=date
    critical_symptoms = PositiveCriticalSymptoms.objects.filter(customer=client, date=date, positive=True).prefetch_related(
        'symptom',
        'symptom__complication',
    )
    chained_querset = chain(symptoms,critical_symptoms)
    # print(symptoms)
    for symptom in chained_querset:
        for complication in symptom.symptom.complication.all():
            complication_name = complication.name
            # check if its in current_count
            c = current_count.get(complication_name, None)
            if c is None:
                current_count[complication_name] = 1
            else:    
                current_count[complication_name] += 1

            # add total count
            t = total_count.get(complication_name, None)
            if t is None:
                # print(f'complication Name {complication_name} : and total Count {complication.symptoms_set.count()} ')
                total_count[complication_name] = complication.symptoms_set.count()

    for complication_name, count in total_count.items():
        percentage_value = complication_percentage.get(complication_name, None)
        if percentage_value in [None, 0]:
            # complication_percentage[complication_name] = str(round((current_count[complication_name]/total_count[complication_name]) * 100,2 )) + " %"
            complication_percentage[complication_name.replace(" ", "_")] = int((current_count[complication_name]/total_count[complication_name]) * 100)

    return Response(complication_percentage)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_personal_details(request):
    user = request.user
    cid = request.query_params.get('customer', None)

    try:
        customer = User.objects.get(id=cid, role=User.CLIENT)
    except User.DoesNotExist:
        return Response({'error' : 'customer not found'}, status=status.HTTP_404_NOT_FOUND)

    personal_details = PersonalDetails.objects.filter(customer=cid)

    serializer = PersonalDetailsSerializer(personal_details,many=True)

    return Response(serializer.data)

@api_view(['POST','PATCH'])
@permission_classes([IsAuthenticated])
def submit_personal_details(request):
    user = request.user
    cid = request.data.get('customer', None)
    try:
        customer = User.objects.get(id=cid, role=User.CLIENT)
    except User.DoesNotExist:
        return Response({'error' : 'customer not found'}, status=status.HTTP_404_NOT_FOUND)
    try:
        personal_data = PersonalDetails.objects.get(customer=customer.id)
        serializer = PersonalDetailsSerializer(personal_data, request.data)
    except PersonalDetails.DoesNotExist:
        serializer = PersonalDetailsSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response({'success' : 'successfully saved'})
    else:
        return Response({'error' : serializer.errors})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_medical_data(request):
    user = request.user
    cid = request.query_params.get('customer', None)

    try:
        customer = User.objects.get(id=cid, role=User.CLIENT)
    except User.DoesNotExist:
        return Response({'error' : 'client not found'}, status=status.HTTP_404_NOT_FOUND)

    medical_history = MedicalHistory.objects.all().prefetch_related(
        Prefetch('medical', queryset=CustomerMedicalHistory.objects.filter(customer=cid))
    )
    serializer = MedicalHistorySerializer(medical_history, many=True)
    return Response(serializer.data)


@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
def post_medical_data(request):
    med_id = request.data.get('id', None)
    cid = request.data.get('customer', None)
    flag = request.data.get('flag', False)

    bool_check = isinstance(flag, (bool))

    if bool_check:
        try:
            customer = User.objects.get(id=cid, role=User.CLIENT)
        except User.DoesNotExist:
            return Response({"error" : "client not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            medical_history = MedicalHistory.objects.get(id=med_id)
        except MedicalHistory.DoesNotExist:
            return Response({'error' : 'medical history not found'}, status=status.HTTP_404_NOT_FOUND)

        instance, created = CustomerMedicalHistory.objects.get_or_create(customer=customer, medical_history=medical_history,defaults={'flag' : flag})
        if not created:
            instance.flag = flag
            instance.save()
        return Response({'success' : 'successfully updated'})
    else:
        return Response({'error' : 'Boolean value is required for flag'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def client_criticalities(request):
    customer_id = request.query_params.get('customer', None)
    try:
        customer = User.objects.get(id=customer_id, role=User.CLIENT)
    except User.DoesNotExist:
        return Response({'error' : 'client not found'}, status=status.HTTP_404_NOT_FOUND)
    criticalities = CriticalityChange.objects.filter(customer=customer).prefetch_related('criticallity').order_by('-date')
    serializer = CriticalityChangeSerializer(criticalities, many=True)
    return Response(serializer.data)
