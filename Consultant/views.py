import datetime
from Sales.models import CriticalityChange
from django.core.checks import messages
from .serializers import *
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from Accounts.models import CustomerDetails
from django.contrib.auth import get_user_model
from Sales.serializers import ClientDetialSerializer
from django.db.models.query import Prefetch

User = get_user_model()


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def consultant_dashboard_details(request):

    # customelr = request.data.get('customer', None)
    # consultant = request.data.get('consultant', None) #106
    user = request.user
    print(user)
    if user.role == User.CONSULTANT:
        print('@@@@@@')
        totalCustomers = CustomerDetails.objects.filter(user__is_active = True)
        print('#########')

            
        # total patient count
        print(totalCustomers)
        totalCount = totalCustomers.count()

        # patients in the current month
        currentDate =  datetime.datetime.today()
        currentMonth = currentDate.month
        customers_thisMonth = totalCustomers.filter(user__dateJoined__month=currentMonth).count()

        # consultantDEtials = User.objects.get(id=consultant)
        allClient = CustomerDetails.objects.filter(user__is_active=True).prefetch_related('user', 'referalId__user',
        Prefetch('user__criticality_change',queryset=CriticalityChange.objects.order_by('-date','-criticallity__criticality')))
        # allClient = CustomerDetails.objects.filter(
        #     user__is_active=True
        # ).prefetch_related(
        #     "referalId",
        #     "referalId__user",
        # )
        serializer = ClientDetialSerializer(allClient, many=True)
        # client.consultant.add(consultantDEtials)

        return Response({
            "firstname" : user.firstname,
            "lastname" : "" if user.lastname is None else user.lastname,
            "total_clients" : totalCount,
            "clients_this_month" : customers_thisMonth,
            "all_clients" : serializer.data
        })
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def add_customized_plan(request):
    user = request.user
    if user.role == User.DOCTOR:
        tracker_name = request.data.get('module', None)
        customer = request.data.get('customer', None)
        if tracker_name and customer is not None:
            data = request.data.copy()
            if tracker_name.lower() == "diet":
                data['tracker'] = CustomizedPlan.DIET
            elif tracker_name.lower() == 'exercise':
                data['tracker'] = CustomizedPlan.EXERCISE
            
            else:
                return JsonResponse({'error' : 'module not found, choose either diet or activity'}, status=status.HTTP_404_NOT_FOUND)

            try:
                module = CustomizedPlan.objects.get(tracker=data['tracker'], customer=customer)
                serializer = CustomizedPlanSerializer(module,data=data)
            except CustomizedPlan.DoesNotExist:
                serializer = CustomizedPlanSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'success': "url added successfully"})
            else:
                return JsonResponse(serializer.errors)
        else:
            return JsonResponse({"error" : "daily tracker module/customer missing"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)



    



