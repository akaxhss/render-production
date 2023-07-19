
from Accounts.models import  CustomerDetails
from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
from Customer.models import BabyPics
from django.db import connection
from django.contrib.sites.shortcuts import get_current_site

# from django.conf import settings
User = get_user_model()


# for 1 days activity/exercise
class SubModuleSerializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()
    class Meta:
        model = ActivitySubModules
        fields = ['id', 'subModuleName','disabled', 'completed'] #, 'date'

    def get_completed(self,obj):
        # print(len(connection.queries))
        # response = obj.Completed_activity.first()
        # try:
        #     return response.completed
        # except:ls -la
        #     return False
        instances = obj.Completed_activity.all()
        for instance in instances:
            return instance.completed
        return False


class ActivityMainModuleSerializer(serializers.ModelSerializer):
    sub_module = SubModuleSerializer(many=True)
    mainModule = serializers.CharField(source="name")
    
    class Meta:
        model = ActivityMainModule
        fields = ['id','mainModule', 'description', 'url', 'disabled', 'sub_module']
    

# end

# to add custom activity/exercise
class AddCustomActivityExercise(serializers.ModelSerializer):
    class Meta:
        model = CustomActivity
        fields = '__all__'

# 1 days data
class CustomActivitySerilializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()
    class Meta:
        model = CustomActivity
        fields = '__all__'
        extra_kwargs = {
            'DailyTrackerModule' : {'write_only' : True},
            'customer' : {'write_only' : True}
        }

    def get_completed(self,obj):
        # print(len(connection.queries))
        response = obj.completedCustom.first()
        try:
            return response.completed
        except:
            return False



# class FilteredCustomActivityExerciseSerializer(serializers.ListSerializer):
#     def to_representation(self, data):
#         data = data.filter(customer=self.context['customer'], completed=True)
#         return super(FilteredCustomActivityExerciseSerializer, self).to_representation(data)


class CompletedCustomActivitySerializer(serializers.ModelSerializer):
    activity = serializers.CharField(source="activity.name")
    class Meta:
        model = CompletedCustomActivity
        exclude = ['id']
    def to_representation(self, instance):
        representation = super(CompletedCustomActivitySerializer, self).to_representation(instance)
        representation['date'] = instance.date.strftime("%d-%m-%Y")
        return representation
        
# class DsiplayAllCustomExerciseActivitySerilializer(serializers.ModelSerializer):
#     completedCustom = CompletedExerciseActivity(many=True)
#     # name = serializers.CharField(source="name")
#     class Meta:
#         model = CustomActivity
#         fields = ['name' ,'completedCustom']



# serializer to filter for customer in nested ActivityExerciseDisplaySerializer 
# class FilteredListSerializer(serializers.ListSerializer):
#     def to_representation(self, data):
#         # data = data.filter(customer=self.context['customer'], completed=True)#daily_tracker_submodules
#         data = data.filter(customer=self.context['customer'], completed=True)
#         return super(FilteredListSerializer, self).to_representation(data)

# to display all days activity
class ActivityDisplaySerializer(serializers.ModelSerializer):
    submodule = serializers.CharField(source='daily_tracker_submodules.subModuleName')
    mainModule = serializers.CharField(source="daily_tracker_submodules.ActivityMainModule")

    class Meta:
        model = CompletedActivity
        exclude = ['daily_tracker_submodules', 'id', 'customer']
    def to_representation(self, instance):
        representation = super(ActivityDisplaySerializer, self).to_representation(instance)
        representation['date'] = instance.date.strftime("%d-%m-%Y")
        return representation

class SubModuleDisplaySerializer(serializers.ModelSerializer):
    Completed_activity = ActivityDisplaySerializer(many=True)
    class Meta:
        model = ActivitySubModules
        fields = ['id', 'subModuleName', 'Completed_activity']
        
class ActivityMainModuleDisplaySerializer(serializers.ModelSerializer):
    sub_module = SubModuleDisplaySerializer(many=True)
    mainModule = serializers.CharField(source="name")

    class Meta:
        model = ActivityMainModule
        fields = ['mainModule', 'sub_module']

    @staticmethod
    def setup_eager_loader(queryset):
        queryset = queryset.prefetch_related('sub_module', 'sub_module__Completed_activity')
        return queryset


# to display all exercise detials
class CompletedExercisesDisplaySerializer(serializers.ModelSerializer):
    exercise = serializers.CharField(source="exercise.name")
    date = serializers.DateField(format="%d-%m-%Y")
    class Meta:
        exclude = ['id', 'customer']
        model = CompletedExercises

       
class ExerciseDisplaySerializer(serializers.ModelSerializer):
    completed_exercise = CompletedExercisesDisplaySerializer(many=True)
    class Meta:
        fields = ['name', 'completed_exercise']
        model = Exercises


class CompletedCustomExercises(serializers.ModelSerializer):
    exercise = serializers.CharField(source="exercise.name")
    class Meta:
        exclude = ['id']
        model = CompletedCustomeExercises
    def to_representation(self, instance):
        representation = super(CompletedCustomExercises, self).to_representation(instance)
        representation['date'] = instance.date.strftime("%d-%m-%Y")
        return representation
        
# class CustomExercisesSerializer(serializers.ModelSerializer):
#     completed_custom_exercise = CompletedCustomExercises(many=True)
#     class Meta:
#         fields = ['name', 'completed_custom_exercise']
#         model = CustomExercises


# babys pic
class BabyDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = BabyPics
        fields = '__all__'

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image is not None:
            return "https://" + str(get_current_site(request)) + "/media/" + str(obj.image)
        
        # return request.build_absolute_uri(obj.image)

# diet serializer
class DietTrackerSerializer(serializers.ModelSerializer):
    mealType = serializers.CharField(read_only=True)
    mealName = serializers.CharField(source='meal.name', required=False)
    # customerName = serializers.CharField(source='customer.firstname', required=False)
    class Meta:
        model = DietTracker
        fields = '__all__'
        extra_kwargs = {
            'meal' : {'write_only' : True},
            'customer' : {'write_only' : True},
        }

class DietTrackerDisplaySerializer(serializers.ModelSerializer):
    mealType = serializers.CharField(read_only=True)
    mealName = serializers.CharField(source='meal.name', required=False)
    class Meta:
        model = DietTracker
        fields = '__all__'
        extra_kwargs = {
            'meal' : {'write_only' : True},
            'customer' : {'write_only' : True},
        }
    def to_representation(self, instance):
        representation = super(DietTrackerDisplaySerializer, self).to_representation(instance)
        representation['date'] = instance.date.strftime("%d-%m-%Y")
        return representation

class AddMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicines
        fields = '__all__'



class TakenMedicineSerializer(serializers.ModelSerializer):
    medicine = serializers.CharField(source='medicine.name') 
    medicationTime = serializers.CharField(source='medicine.time.name') 
    class Meta:
        # list_serializer_class = MedicineFilter
        model = TakenMedicine
        fields = '__all__'
        extra_kwargs = {
            'customer' : {'write_only' : True},
        }
    def to_representation(self, instance):
        representation = super(TakenMedicineSerializer, self).to_representation(instance)
        representation['date'] = instance.date.strftime("%d-%m-%Y")
        return representation


    




# new set medicine serializer (single days data)
class MedicineSerializer(serializers.ModelSerializer):
    taken = serializers.SerializerMethodField()
    MedicationTime = serializers.CharField(source="time.name")
    class Meta:
        model = Medicines
        fields = ['id', 'name', 'taken', 'MedicationTime']
        extra_kwargs = {
            'customer' : {'write_only' : True},
            'time' : {'write_only' : True},
            'taken' : {'read_only' : True},
            'MedicationTime' : {'read_only' : True}
        }
        
    def get_taken(self,obj):
        response = obj.MedicineDetail.first()
        # print(len(connection.queries))
        try:
            return response.taken 
        except:
            return False



class MedicineTimeSerializer(serializers.ModelSerializer):
    Medicines = MedicineSerializer(many=True)
    MedicationTime = serializers.CharField(source="name")
    class Meta:
        # print(len(connection.queries))
        model = MedicineTime
        fields = ['MedicationTime', 'Medicines']
    
# end


# symptoms



class SymptomSerializer(serializers.ModelSerializer):
    positive = serializers.SerializerMethodField()
    class Meta:
        model = Symptoms
        fields = ['id', 'name', 'positive','category']
        extra_kwargs = {
            'customer' : {'write_only' : True},
        }
    def get_positive(self,obj):
        for instance in obj.positive_symptom.all():
            try:
                return instance.positive
            except:
                return False
        return False
        # qs = self.context.get("queryset")
        # if qs:
        #     for instance in qs:
        #         if instance.symptom.id == obj.id:
        #             return instance.positive 
        # return False



class SymptomsInputSerializer(serializers.ModelSerializer):
    bloodSugar_with_unit = serializers.SerializerMethodField(read_only=True)
    bloodPressure_with_unit = serializers.SerializerMethodField(read_only=True)
    weight_with_unit = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SymptomsInput
        fields = '__all__'
        extra_kwargs = {
            'customer' : {'write_only' : True},
        }

    def get_bloodSugar_with_unit(self,obj):
        if obj.bloodSugar is not None:
            return str(obj.bloodSugar) + " " + "(mg/dL)"
    def get_bloodPressure_with_unit(self,obj):
        if obj.bloodPressure is not None:
            return str(obj.bloodPressure) + " " + "(mmHg)"
    def get_weight_with_unit(self,obj):
        if obj.weight is not None:
            return str(obj.weight) + " " + "Kg"


class CustomSymptomSerializer(serializers.ModelSerializer):
    positive = serializers.SerializerMethodField()
    class Meta:
        model = CustomSymptoms
        fields = '__all__'
        extra_kwargs = {
            'customer' : {'write_only' : True},
        }

    def get_positive(self,obj):
        for instance in obj.positive_custom_symptom.all():
            try:
                return instance.positive
            except:
                return False
        return False



class PositiveSymptomsSerializer(serializers.ModelSerializer):
    symptom = serializers.CharField(source="symptom.name")
    class Meta:
        fields = ['symptom', 'date', 'positive']
        model = PositiveSymptoms
    def to_representation(self, instance):
        representation = super(PositiveSymptomsSerializer, self).to_representation(instance)
        representation['date'] = instance.date.strftime("%d-%m-%Y")
        return representation
        

class SymptomsDisplaySerializer(serializers.ModelSerializer):
    positive_symptom = PositiveSymptomsSerializer(many=True)
    class Meta:
        fields = ['name', 'positive_symptom']
        model = Symptoms


class SymptomsInputDisplaySerializer(serializers.ModelSerializer):
    bloodSugar_with_unit = serializers.SerializerMethodField(read_only=True)
    bloodPressure_with_unit = serializers.SerializerMethodField(read_only=True)
    weight_with_unit = serializers.SerializerMethodField(read_only=True)
    class Meta:
        exclude = ['customer', 'id']
        model = SymptomsInput
    def to_representation(self, instance):
        representation = super(SymptomsInputDisplaySerializer, self).to_representation(instance)
        representation['date'] = instance.date.strftime("%d-%m-%Y")
        return representation
    def get_bloodSugar_with_unit(self,obj):
        if obj.bloodSugar is not None:
            return str(obj.bloodSugar) + " " + "(mg/dL)"
    def get_bloodPressure_with_unit(self,obj):
        if obj.bloodPressure is not None:
            return str(obj.bloodPressure) + " " + "(mmHg)"
    def get_weight_with_unit(self,obj):
        if obj.weight is not None:
            return str(obj.weight) + " " + "Lg"


class PositiveSymptomDisplaySerializer(serializers.ModelSerializer):
    symptom = serializers.CharField(source="symptom.name")
    class Meta:
        exclude = ['id']
        model = PositiveCustomSymptoms

    def to_representation(self, instance):
        representation = super(PositiveSymptomDisplaySerializer, self).to_representation(instance)
        representation['date'] = instance.date.strftime("%d-%m-%Y")
        return representation


class CustomSymptomDisplaySerializer(serializers.ModelSerializer):
    positive_custom_symptom = PositiveSymptomDisplaySerializer(many=True)
    class Meta:
        fields = ['symptom','positive_custom_symptom']
        model = CustomSymptoms


class LastWeekReport(serializers.Serializer):
    # symptom__name = serializers.CharField()
    symptom = serializers.CharField(source="symptom__name")
    count = serializers.IntegerField()


class MedicalSerializer(serializers.ModelSerializer):
    ultra_sound_filename = serializers.SerializerMethodField()
    blood_report_filename = serializers.SerializerMethodField()
    antenatal_chart_filename = serializers.SerializerMethodField()
    # customer = serializers.IntegerField(required=False)

    class Meta:
        model = Medical
        fields = '__all__'
        extra_kwargs = {
            'customer' : {'write_only' : True, 'required' : False},
            'date' : {'required' : False},
        }
    def get_ultra_sound_filename(self, obj):
        try:
            array = obj.ultraSound.url.split("/")  
            return array[3]
        except:
            return ""
    
    def get_blood_report_filename(self, obj):
        try:
            array = obj.bloodReport.url.split("/")  
            return array[3]
        except:
            return ""

    def get_antenatal_chart_filename(self, obj):
        try:
            array = obj.antenatalChart.url.split("/")  
            return array[3]
        except:
            return ""
    # def get_ultra_sound_full_url(self,obj):
    #     request = self.context.get('request')
    #     return "https://" + str(get_current_site(request))+ '/media/'  + str(obj.ultraSound)

    # def get_blood_url_full_url(self, obj):
    #     request = self.context.get('request')
    #     return "https://" + str(get_current_site(request))+ '/media/'  + str(obj.bloodReport)

    # def get_antenatal_chart_full_url(self, obj):
    #     request = self.context.get('request')
    #     return "https://" + str(get_current_site(request)) + '/media/' + str(obj.antenatalChart)



class ContractionSerializer(serializers.ModelSerializer):
    painScale = serializers.ChoiceField(choices=Contraction.PAIN_SCALE_CHOICES)
    formated_time = serializers.SerializerMethodField(read_only=True) 
    formated_interval = serializers.SerializerMethodField(read_only=True) 
    class Meta:
        model = Contraction
        fields = '__all__'
        extra_kwargs = {
            'customer' : {'write_only' : True},
            'painScale' : {'write_only' : True}
        }
    # def get_pain_scale(self, obj):
    #     return obj.painScale.name.capitalize()
    def get_pain_scale(self, obj):
        return obj.painScale.capitalize()
        
    def get_formated_time(self, obj):
        return obj.time.strftime("%I:%M %p").lstrip("0").replace(" 0", " ")

    def get_formated_interval(self, obj):
        duration = obj.interval
        days, total_seconds = duration.days, duration.seconds
        hours = days * 24 + total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours != 0:
            return "{hours} Hrs {minutes} min {seconds} sec".format(hours=hours, minutes=minutes, seconds=seconds)
        elif minutes != 0:
            return "{minutes} min {seconds} sec".format(minutes=minutes, seconds=seconds)
        else:
            return "{seconds} sec".format(seconds=seconds)


class ContractionDisplaySerializer(serializers.ModelSerializer):
    pain_scale = serializers.SerializerMethodField(read_only=True)
    formated_time = serializers.SerializerMethodField(read_only=True) 
    formated_interval = serializers.SerializerMethodField(read_only=True) 
    class Meta:
        model = Contraction
        fields = '__all__'
        extra_kwargs = {
            'customer' : {'write_only' : True},
            'painScale' : {'write_only' : True}
        }
    def get_pain_scale(self, obj):
        return obj.painScale.capitalize()
        
    def get_formated_time(self, obj):
        return obj.time.strftime("%I:%M %p").lstrip("0").replace(" 0", " ")

    def get_formated_interval(self, obj):
        duration = obj.interval
        days, total_seconds = duration.days, duration.seconds
        hours = days * 24 + total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours != 0:
            return "{hours} Hrs {minutes} min {seconds} sec".format(hours=hours, minutes=minutes, seconds=seconds)
        elif minutes != 0:
            return "{minutes} min {seconds} sec".format(minutes=minutes, seconds=seconds)
        else:
            return "{seconds} sec".format(seconds=seconds)

    def to_representation(self, instance):
        representation = super(ContractionDisplaySerializer, self).to_representation(instance)
        representation['date'] = instance.date.strftime("%d-%m-%Y")
        return representation


class MedicalDetails(serializers.ModelSerializer):
    # consultant = ConsultantInfoSerializer(many=True)
    class Meta:
        model = CustomerDetails
        exclude = ('age', 'job', 'address', 'husband')


# modules inside excersice/activity(main)
class AddActivityMainModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityMainModule
        fields = '__all__'
    

# sub modules inside Excersice or Activity(sub module)
class DailyTrackerSubModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivitySubModules
        fields = '__all__'

class CompletedExercise(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = CompletedExercises

class ExerciseSerializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()
    # completed_exercise = CompletedExercise(read_only=True, many=True)
    class Meta:
        model = Exercises
        fields = '__all__' 
        extra_kwargs = {
            'stage' : {'write_only' : True}
        }

    def get_completed(self, obj):
        # instance = obj.completed_exercise.first()
        # print(len(connection.queries))
        # try:
        #     return instance.completed
        # except:
        #     return False

        instances = obj.completed_exercise.all()
        # print(len(connection.queries))
        for instance in instances:
            return instance.completed
        return False




class CaloriesBurntSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaloriesBurnt
        fields = '__all__'
        extra_kwargs = {
            'customer' : {'write_only' : True}
        }
    def to_representation(self, instance):
        representation = super(CaloriesBurntSerializer, self).to_representation(instance)
        representation['date'] = instance.date.strftime("%d-%m-%Y")
        return representation


class CustomExerciseSerializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()
    date = serializers.DateField(format="%d-%m-%Y", read_only=True)
    class Meta:
        model = CustomExercises
        fields = '__all__'
        extra_kwargs = {
            'completed' : {'read_only': True},
            'customer' : {'write_only': True},
        }
    
    def get_completed(self, obj):
        # instance = obj.completed_custom_exercise.first()
        # print(len(connection.queries))
        # try:
        #     return instance.completed
        # except:
        #     return False
        instances = obj.completed_custom_exercise.all()
        # print(len(connection.queries))
        for instance in instances:
            return instance.completed
        return False



class GetActivityMainModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityMainModule
        fields = ['name']


