
from os import stat
from .serializers import *
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
# from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework_api_key.permissions import HasAPIKey
from Accounts.models import CustomerDetails
from django.contrib.auth import get_user_model

User = get_user_model()
from datetime import date

def calculate_stage(periods_date):
    today = date.today()
    daysPregnant = today - periods_date
    # week = daysPregnant.days/7
    # if isinstance(week, float):
    #         week = int(week)
    week = int((daysPregnant.days % 365) / 7)

    if week > 0 and week <= 4: #28
        stage = Stage.objects.get(name='stage1')
    elif week >= 5 and week <= 8:
        stage = Stage.objects.get(name='stage2')
    elif week >= 9 and week <= 12:
        stage = Stage.objects.filter(name='stage3').first()
    elif week >= 13 and week <= 16:
        stage = Stage.objects.get(name='stage4')
    elif week >= 17 and week <= 20:
        stage = Stage.objects.get(name='stage5')
    elif week >= 21 and week <= 24:
        stage = Stage.objects.get(name='stage6')
    elif week >= 25 and week <= 28:
        stage = Stage.objects.get(name='stage7')
    elif week >= 29 and week <= 32:
        stage = Stage.objects.get(name='stage8')
    elif week >= 33 and week <= 36:
        stage = Stage.objects.get(name='stage9')
    # elif week > 37:
    #     stage = Stage.objects.filter(name='stage10').first()
    else:
        stage = Stage.objects.filter(name='stage10').first()
    return stage.id

# Admin and sales adding videos
@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def add_videos(request):
    user = request.user
    if user.role == User.ADMIN or user.role == User.SALES:
        is_update = False
        data = request.data.copy()
        moduleName = data.get('module', None)
        stageName = data.get('stage', None)

        if moduleName and stageName is not None:
            try:
                module = Modules.objects.get(name__iexact=moduleName)
            except Modules.DoesNotExist:
                return JsonResponse({"error" : "Module not found"}, status=status.HTTP_404_NOT_FOUND)
            try:
                stage = Stage.objects.get(name__iexact=stageName)
            except Stage.DoesNotExist:
                return JsonResponse({"error" : "Stage not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return JsonResponse({"error" : "module and stage fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        data['module'] = module.id
        data['stage'] = stage.id

        # check if video update
        try:
            vdo = Videos.objects.get(stage=stage.id, module=module.id)
            is_update = True
        except Videos.DoesNotExist:
            is_update = False

        if is_update == True:
            serializer = AddVideoSerializers(vdo, data=data)
        else:
            serializer = AddVideoSerializers(data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return JsonResponse({"success" : "Successfull", "Data" : serializer.data})
        else:
            raise serializers.ValidationError({"error" : serializer.errors})
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_module_data(request):
    customer = request.user
    if customer.role == User.CLIENT:
        module = request.query_params.get('module', None)
        # get selected module
        try:
            module = Modules.objects.get(name__iexact=module)
        except Modules.DoesNotExist:
            return JsonResponse({"error" : "selected module not found !"}, status=status.HTTP_404_NOT_FOUND)

        # calculate stage of customer (0-4,5-12 weeks, .... )
        try:
            details = customer.customer_details.first()
        except CustomerDetails.DoesNotExist:
            return JsonResponse({"error" : "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # calc week and days left from Menstruation_date
        periods_date =  details.Menstruation_date

        
        stage = calculate_stage(periods_date)
        notes = Notes.objects.filter(customer=customer, stage=stage, module=module.id).first()
        video = Videos.objects.filter(module=module.id, stage=stage).first()

        videoserializer = AddVideoSerializers(video)
        noteserializer = NoteSerializer(notes)

        return JsonResponse({
            "video" : videoserializer.data,
            "note" : noteserializer.data,
            # "module" : module.name,
            # "stage" : "stage" + str(stage),
            # "week" : week,
        })
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)



# Add Notes
@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def add_notes(request):
    user = request.user
    if user.role == User.CLIENT:
    # is_update = False
        data = request.data.copy()
        module = request.data.get('module', None)
        customer = user.id
        if module and customer is not None:
            try:
                customerDetails = user.customer_details.first()
            except :
                return JsonResponse({"Error" : "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

            try:
                module = Modules.objects.get(name__iexact=module)
            except Modules.DoesNotExist:
                return JsonResponse({"error" : "Specified module not found"}, status=status.HTTP_404_NOT_FOUND)

            stage_id = calculate_stage(customerDetails.Menstruation_date)
            data['module'] = module.id
            data['stage'] = stage_id
            data['customer'] = customer
            # check if notes update
            try:
                note = Notes.objects.get(customer=customer, stage=stage_id, module=module.id)
                serializer = NoteSerializer(note, data=data)
            except Notes.DoesNotExist:
                serializer = NoteSerializer(data=data)

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return JsonResponse({"success" : "notes added", "data" : serializer.data})
            else:
                raise serializers.ValidationError({"error" : serializer.errors})
        else:
            return JsonResponse({"error" : "module field cannot be empty"})
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)