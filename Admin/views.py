# from django.db.models.query import Prefetch
# from multiprocessing import context
from LearnIt.models import Stage
from Sales.models import CustomerCallReposnses, InvestigationCriticallity
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Count
from Payments.serializers import Membership2Serializer
from Accounts.models import CustomerDetails, ConsultantInfo, hospitalManagerDetails
from Accounts.serializers import ConsultantInfoSerializer, HospitalDetailSerializer
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes , authentication_classes
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.db.models import Q
from Customer.models import Exercises
from .serializers import *
from .serializers import CriticalSymptomSerializer

from Payments.serializers import MembershipPlanSerializer
from django.utils.timezone import make_aware
from Sales.serializers import DisplayCallReposnseSerializer, SalesSerializer
from Consultant.serializers import ConsultantSerializer
from rest_framework.authentication import TokenAuthentication
User = get_user_model() 


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def admin_dashboard(request):
    # totalDoctors = User.objects.filter(doctor=True)
    # totalClients = User.objects.filter(patient=True)
    # single query
    # totalConsultant = User.objects.filter(consultant=True).count()
    # totalSalesTeam = User.objects.filter(sales=True).count()
    # activeClients = totalClients.filter(is_active=True).count()
    # disabledDoctors = totalDoctors.filter(is_active=False).count()
    # totalHospitals = User.objects.filter(hospitalManager=True).count()
    # 
    user = request.user
    if user.role == User.ADMIN:
        counts = User.objects.aggregate(
            totalConsultant=Count('id', filter=Q(role=User.CONSULTANT,is_active=True, consultantDetails__isnull = False)),
            totalSalesTeam=Count('id', filter=Q(role=User.SALES,is_active=True)),
            activeClients=Count('id', filter=Q(role=User.CLIENT,is_active=True)),
            disabledDoctors=Count('id', filter=Q(role=User.DOCTOR,is_active=False)),
            totalHospitals=Count('id', filter=Q(role=User.HOSPITAL_MANAGER,is_active=True)),
            totalDoctors=Count('id', filter=Q(role=User.DOCTOR,is_active=True)),
            totalClients=Count('id', filter=Q(role=User.CLIENT,is_active=True)))

        print(counts)

        CountSerializer = adminDashboardCountsSerializer(counts)
    
        clientDetails = CustomerDetails.objects.all()
        clientDetails = totalClientSerializer.pre_loader(clientDetails)
        serializer = totalClientSerializer(clientDetails, many=True, context={'request' : request})

        memberships = MemberShip.objects.all()
        membershipSerialized = Membership2Serializer(memberships, many=True)   

        context = {
            "MemberShipPlans" : membershipSerialized.data,
            "counts" : CountSerializer.data,
            # "totalDoctors" : totalDoctors.count(),
            # "totalClients" : totalClients.count(),
            # "totalHospitals" : totalHospitals,
            # "totalConsultant" : totalConsultant,
            # "totalSalesTeam" : totalSalesTeam,
            # "activeClients" : activeClients,
            # "disabledDoctors" : disabledDoctors,
            "clientDetails" : serializer.data
        }
        return JsonResponse(context)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def all_doctors(request):
    user = request.user
    if user.role == User.ADMIN or user.role == User.CLIENT:
        doctors = DoctorDetails.objects.filter(Q(user__is_active__in=[True])).prefetch_related('user', 'hospitalManager')
        serializer = DoctorDetailSerializer(doctors, many=True,context={'request' : request})
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)




@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def all_sales_team(request):
    try:

        user = request.user
        sales = SalesTeamDetails.objects.filter(user__isnull = False, user__role = 4).prefetch_related('user')
        if user.role == User.ADMIN:
            serializer = SalesTeamSerializer(sales, many=True)
        elif user.role == User.CLIENT:
            serializer = SalesSerializer(sales,many=True, context={'request':request})
        else:
            return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
        context = {
            'count' : len(serializer.data),
                'details' : serializer.data
            }
        return JsonResponse(context)
    except Exception as e:
        print(e)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_membership_plans(request):
    user = request.user
    if user.role != User.ADMIN:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
    memberships = MembershipPlans.objects.all()
    serializer = MembershipPlanSerializer(memberships, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def change_client_membership(request):
    user = request.user
    if user.role != User.ADMIN:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
    customer =  request.data.get('customer', None)
    membership = request.data.get('membershipId', None)
    currentDate = datetime.now()
    membershipPlan = None
    try:
        membershipPlan = MemberShip.objects.get(id=membership)
    except MemberShip.DoesNotExist:
        return JsonResponse({"Error" : "Selected Membership Doesnot exists"}, status=status.HTTP_404_NOT_FOUND)
    try:
        customer = User.objects.get(id=customer)
    except User.DoesNotExist:
        return JsonResponse({"Error" : "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        # ? make current plan inactive
    purchased_membership = PurchasedMembership.objects.filter(
        user = customer
    )

    if purchased_membership.exists():
        purchased_membership.update(membership =membershipPlan , is_paid = True)
        purchased_membership.update(membership =membershipPlan , is_paid = True)
        print(purchased_membership[0].membership)

    else:
        PurchasedMembership.objects.create(
            user = customer,
            membership =membershipPlan,
            is_paid = True
        )






    # for pm in purchased_membership:
    #     pm.membership = membershipPlan
    #     pm.save()



    return JsonResponse({"success" : "Successfully changed membership"})


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def subscriptions_data(request):
    user = request.user
    if user.role == User.ADMIN:
        # allSubscriptions = Subscriptions.objects.all()
        # activeSubscriptions = allSubscriptions.filter(is_active=True)
        # basic = activeSubscriptions.filter(membership__name='basic')
        # standard = activeSubscriptions.filter(membership__name='standard')

        # customers_ids_with_subscriptions = allSubscriptions.values_list('customer')

        # # exclude the above to get the customers that are in the free trail
        # thresholdDate = datetime.now(timezone.utc) - timedelta(days=30)
        # trail = CustomerDetails.objects.exclude(user__in=customers_ids_with_subscriptions).filter(user__dateJoined__gte=thresholdDate)
        # TrailSerializer = totalClientSerializer(trail, many=True)
        # return JsonResponse({
        #     'basic' : basic.count(),
        #     'standard' : standard.count(),
        #     'trail' : trail.count(),
        #     'clientsWithTrailPlan' : TrailSerializer.data
        # })

        #  sub counts
        oneMonthPlan = Subscriptions.objects.filter(membership__name="1 month package")
        threeMonthPlan = Subscriptions.objects.filter(membership__name="3 month package")
        pregnancyClass = Subscriptions.objects.filter(membership__name="pregnancy class")
        fullPregnancyPackage = Subscriptions.objects.filter(membership__name="full pregnancy package")

        # active clients
        activeClients = User.objects.filter(role=User.CLIENT, is_active=True)
        disabledClients = User.objects.filter(role=User.CLIENT, is_active=False)

        return JsonResponse({
            "oneMonthPlan" : oneMonthPlan.count(),
            "threeMonthPlan" : threeMonthPlan.count(),
            "pregnancyClass" : pregnancyClass.count(),
            "fullPregnancyPackage" : fullPregnancyPackage.count(),
            "activeClients" : activeClients.count(),
            "disabledClients" : disabledClients.count()
        })
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def clients_with_basic_plan(request):
    user = request.user
    if user.role == User.ADMIN:
        basic = Subscriptions.objects.filter(membership__name='basic', is_active=True).values_list('customer')
        customers = CustomerDetails.objects.filter(user__in=basic)
        customers = totalClientSerializer.pre_loader(customers)
        serializer = totalClientSerializer(customers, many=True, context={'request':request})    
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def clients_with_standard_plan(request):
    user = request.user
    if user.role == User.ADMIN:
        standard = Subscriptions.objects.filter(membership__name='standard', is_active=True).values_list('customer')
        customers = CustomerDetails.objects.filter(user__in=standard)
        customers = totalClientSerializer.pre_loader(customers)
        serializer = totalClientSerializer(customers, many=True, context={'request' : request})
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def all_clients_list(request):
    user = request.user
    print(user.role)
    if user.role == User.ADMIN:
        date = datetime.now().date()
        threshold_date = date - timedelta(days=294) #42 weeks
        # get all users with subscription
        users_with_subs = Subscriptions.objects.filter(is_active=True).values_list('customer')
        # clientDetails = CustomerDetails.objects.filter(user__is_verified=True, user__sub_client__is_active=True)
        clientDetails = CustomerDetails.objects.filter(user__is_verified=True,user__id__in=users_with_subs,Menstruation_date__gte=threshold_date)
        clientDetails = totalClientSerializer.pre_loader(clientDetails)
        serializer = totalClientSerializer(clientDetails, many=True, context={'request' : request})
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def all_hospitals(request):
    user = request.user
    if user.role == User.ADMIN:
        hospitals = hospitalManagerDetails.objects.all().prefetch_related('user')
        serializer = HospitalDetailSerializer(hospitals, many=True)
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def doctor_approval_requests(request):
    user = request.user
    if user.role == User.ADMIN:
        doctors = DoctorDetails.objects.filter(user__is_active=False).prefetch_related('user', 'hospitalManager')
        serializer = DoctorDetailSerializer(doctors, many=True, context={'request' : request})
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def approve_doctor(request):
    user = request.user
    if user.role == User.ADMIN:
        id = request.data.get('doctor', None)
        if id is not None:
            try:
                doctor = User.objects.get(id=id)
                doctor.is_verified = True
                doctor.save()
                return JsonResponse({'success' : 'doctor approved successfully'})
            except User.DoesNotExist:
                return JsonResponse({'error' : 'doctor with the given id not found'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'error' : 'pass doctor:id as data'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def all_consultants_list(request):
    user = request.user
    consultants = ConsultantInfo.objects.filter(user__role = 5).prefetch_related('user')
    if user.role == User.ADMIN:
        serializer = ConsultantInfoSerializer(consultants, many=True, context={'request' : request})
    elif user.role == User.CLIENT:
        serializer = ConsultantSerializer(consultants, many=True, context={'request':request})
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
    return JsonResponse({'data' : serializer.data, 'count' :consultants.count() }, safe=False)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_call_response(request):
    user = request.user
    if user.role == User.ADMIN:
        salesTeam = request.query_params.get('salesTeam', None)
        date_param = request.query_params.get('date', None)
        # if date is None:
        #     date = datetime.today().date()    
        date =  date_param if date_param is not None else datetime.today().date()
        try:
            Salesdetails = SalesTeamDetails.objects.get(user=salesTeam)
        except SalesTeamDetails.DoesNotExist:
            return JsonResponse({"Error" : "Sales team not found"}, status=status.HTTP_400_BAD_REQUEST)
        if salesTeam is not None:
            responses = CustomerCallReposnses.objects.filter(sales=Salesdetails.id, date=date).prefetch_related('response')
            serializer = DisplayCallReposnseSerializer(responses, many=True)
            return JsonResponse(serializer.data, safe=False)
        else:
            return JsonResponse({
                'Error' : "salesTeam id not provided"
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def all_exercises(request):
    user = request.user
    if user.role == User.ADMIN:
        stage = request.query_params.get('stage', None)
        if stage is not None:
            try:
                stage_id = Stage.objects.get(name=stage)
            except Stage.DoesNotExist:
                return Response({"error" : "selected period does not exists"}, status=status.HTTP_404_NOT_FOUND)
            exercises = Exercises.objects.filter(stage=stage_id.id)
            serializer = AllExerciseSerializer(exercises, many=True)
            return Response(serializer.data)
        else:
            return Response({"error" : "pass stage as params"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error" : "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['PATCH'])
@permission_classes((IsAuthenticated,))
def edit_exercise(request):
    try:
        user = request.user
        if user.role == User.ADMIN:
            print('THUIS')
            exercise_id = request.data.get('id', None)
            exercise_name = request.data.get('exercise', None)
        

            if exercise_id is not None and exercise_name:
                try:
                    exercise = Exercises.objects.get(id=exercise_id)
                except Exercises.DoesNotExist:
                    return Response({"error" : "selected exercises does not exists"}, status=status.HTTP_404_NOT_FOUND)
                print('#####')
                print(exercise_id)
                print(exercise_name)
                print('#####')    
                exercise.name = exercise_name
                exercise.save()
                

                return Response({"success" : "successfuly updated", "data" : {'id' : exercise.id , 'name' : exercise.name}})
            else:
                return Response({"error" : "pass exercise_id as params"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error" : "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        print(e)

@api_view(['PATCH'])
@permission_classes((IsAuthenticated,))
def toggle_exercise(request):
    user = request.user
    if user.role == User.ADMIN:
        exercise_id = request.data.get('id', None)
        if exercise_id is not None:
            try:
                exercise = Exercises.objects.get(id=exercise_id)
            except Exercises.DoesNotExist:
                return Response({"error" : "selected exercises does not exists"}, status=status.HTTP_404_NOT_FOUND)
                
            exercise.disabled = not exercise.disabled
            exercise.save()
            return Response({"success" : "successfuly updated"})
        else:
            return Response({"error" : "pass exercise_id as params"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error" : "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def all_activity_main_modules(request):
    user = request.user
    if user.role == User.ADMIN:
        stage = request.query_params.get('stage', None)
        if stage is not None:
            try:
                stage_id = Stage.objects.get(name=stage)
            except Stage.DoesNotExist:
                return Response({"error" : "selected period does not exists"}, status=status.HTTP_404_NOT_FOUND)
            activity = ActivityMainModule.objects.filter(stage=stage_id.id)
            serializer = ActivityMainModuleSerializer(activity, many=True)
            return Response(serializer.data)
        else:
            return Response({"error" : "pass stage as params"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error" : "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def all_activity_sub_modules(request):
    user = request.user
    if user.role == User.ADMIN:
        id = request.query_params.get('id', None)
        if id is not None:
            sub_modules = ActivitySubModules.objects.filter(ActivityMainModule=id)
            serializer = SubModuleSerializer(sub_modules, many=True)
            return Response(serializer.data)
        else:
            return Response({"error" : "pass stage as params"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error" : "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['PATCH'])
@permission_classes((IsAuthenticated,))
def edit_activity_main_module(request):
    user = request.user
    if user.role == User.ADMIN:
        main_module_id = request.data.get('id', None)
        main_module = request.data.get('name', None)
        if main_module_id and main_module is not None:
            try:
                module = ActivityMainModule.objects.get(id=main_module_id)
            except ActivityMainModule.DoesNotExist:
                return Response({"error" : "selected main module does not exists"}, status=status.HTTP_404_NOT_FOUND)
                
            module.name = main_module
            module.save()
            return Response({"success" : "successfuly updated"})
        else:
            return Response({"error" : "pass id as params"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error" : "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['PATCH'])
@permission_classes((IsAuthenticated,))
def edit_activity_sub_module(request):
    user = request.user
    if user.role == User.ADMIN:
        sub_module_id = request.data.get('id', None)
        sub_module = request.data.get('name', None)
        if sub_module_id and sub_module is not None:
            try:
                module = ActivitySubModules.objects.get(id=sub_module_id)
            except ActivitySubModules.DoesNotExist:
                return Response({"error" : "selected sub module does not exists"}, status=status.HTTP_404_NOT_FOUND)
                
            module.subModuleName = sub_module
            module.save()
            return Response({"success" : "successfuly updated"})
        else:
            return Response({"error" : "pass id as params"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error" : "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['PATCH'])
@permission_classes((IsAuthenticated,))
def toggle_main_module(request):
    user = request.user
    if user.role == User.ADMIN:
        main_module_id = request.data.get('id', None)
        if main_module_id is not None:
            try:
                main_module = ActivityMainModule.objects.get(id=main_module_id)
            except ActivityMainModule.DoesNotExist:
                return Response({"error" : "selected main module does not exists"}, status=status.HTTP_404_NOT_FOUND)
                
            main_module.disabled = not main_module.disabled
            main_module.save()
            return Response({"success" : "successfuly updated"})
        else:
            return Response({"error" : "pass id as params"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error" : "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['PATCH'])
@permission_classes((IsAuthenticated,))
def toggle_sub_module(request):
    user = request.user
    if user.role == User.ADMIN:
        sub_module_id = request.data.get('id', None)
        if sub_module_id is not None:
            try:
                sub_module = ActivitySubModules.objects.get(id=sub_module_id)
            except ActivitySubModules.DoesNotExist:
                return Response({"error" : "selected sub module does not exists"}, status=status.HTTP_404_NOT_FOUND)
                
            sub_module.disabled = not sub_module.disabled
            sub_module.save()
            return Response({"success" : "successfuly updated"})
        else:
            return Response({"error" : "pass id as params"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error" : "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def all_dates_critical_symptoms(request):
    user = request.user
    if user.role == User.ADMIN or user.role == User.DOCTOR or user.role == User.SALES:
        cid = user.id if user.role == User.CLIENT else request.query_params.get('customer', None)
        if cid is not None:
            symptoms_data = PositiveCriticalSymptoms.objects.filter(customer=cid, positive=True).prefetch_related('symptom').order_by('-date')
            symptoms_serializer = PositiveCriticalSymptomsSerializer(symptoms_data, many=True)
            return Response(symptoms_serializer.data)
        else:
            return Response({"Error" : "customer not provided"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_critical_symptoms(request):
    user = request.user
    if user.role == User.ADMIN or user.role == User.SALES or user.role == User.DOCTOR:
        date = request.query_params.get('date', None)
        cid = request.query_params.get('customer', None)
        if cid is None:
            return Response({"Error" : "Specify 'customer':id in params"}, status=status.HTTP_400_BAD_REQUEST)
        if date == None:
            date = datetime.now().date()
        else:
            date = datetime.fromisoformat(date)

        symptoms = CriticalSymptoms.objects.all().prefetch_related(
            Prefetch('positive_symptom', queryset=PositiveCriticalSymptoms.objects.filter(date=date,positive=True,customer=cid))
        )
        serializer = CriticalSymptomSerializer(symptoms ,many=True)
        return Response( serializer.data)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST','PATCH'])
@permission_classes((IsAuthenticated,))
def submit_critical_symptom(request):
    user = request.user
    try:
        if user.role == User.ADMIN or user.role == User.SALES:

            data = request.data 

            date = data.get('date', None)
            symptom_id = data.get('symptom', None)
            positive = data.get('positive', None)
            customer = data.get('customer', None)

            if date is None or symptom_id is None or positive is None or customer is None:
                return Response({'error' : 'date ,  symptom , positive, customer are fields are reuqired'}, status=status.HTTP_404_NOT_FOUND)

                 


            try:
                customer = User.objects.get(id=customer)
            except User.DoesNotExist:
                return Response({"error" : "customer not fount"}, status=status.HTTP_404_NOT_FOUND)
            try:
                symptom = CriticalSymptoms.objects.get(id=symptom_id)
            except CriticalSymptoms.DoesNotExist:
                return Response({"error" : "symptom not found"}, status=status.HTTP_404_NOT_FOUND)

            if date and symptom_id is not None:
                instance, created = PositiveCriticalSymptoms.objects.get_or_create(
                    symptom=symptom,customer=customer,
                    date=date)
                if not created:
                    instance.positive = positive
                    instance.save()

                # criticality change
                try:
                    criticality = InvestigationCriticallity.objects.get(name="high risk")
                except InvestigationCriticallity.DoesNotExist:
                    return Response({'error' : 'criticality not found'}, status=status.HTTP_404_NOT_FOUND)

                if positive and symptom: #True/checked
                    instance, created = CriticalityChange.objects.get_or_create(customer=customer,criticallity=criticality,date=date)
                else: #False/unchecked
                    # check if there is other symptoms with same criticality,
                    # if yes dont delete the criticality change
                    # else delelete it.
                    criticality_change = PositiveCriticalSymptoms.objects.filter(customer=customer,date=date,positive=True)
                    if not criticality_change:
                        CriticalityChange.objects.filter(customer=customer,criticallity=criticality,date=date).delete()
                return Response({"success" : "successfuly updated"})
            else:
                return Response({'error' : "date or symptom field empty"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        import sys, os
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)



from rest_framework.views import APIView

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
            print(e)
            return JsonResponse({'status' : False ,'details' : {}})

    def post(self , request):
        try:
            data = request.data
            serializer = FreeContentSerializer(data = data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                'status' : True,
                'data' : serializer.data
            })
            return JsonResponse({'status' : False ,'details' : serializer.errors})
        
        except Exception as e:
            print(e)
            return JsonResponse({'status' : False ,'details' : {}})

    
    def delete(self , request):
        try:
            data = request.data
            if not data.get('id'):
                return JsonResponse({'status' : False, 'message' : 'id is required' ,'details' : {}})

            try:
                freeContent = FreeContent.objects.get(id = data.get('id')).delete()
                return Response({
                    'message' : 'content deleted',
                    'status' : True,
                    'data' : {}
                })
            except Exception as e:
                return JsonResponse({'status' : False, 'message' : 'invalid id ' ,'details' : {}})


        except Exception as e:
            return JsonResponse({'status' : False ,'details' : {}})




