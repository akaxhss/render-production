
import re
from rest_framework import serializers

from Customer.models import Exercises,ActivityMainModule,ActivitySubModules
from .models import *
from Accounts.models import CustomerDetails, SalesTeamDetails, DoctorDetails
from django.contrib.auth import get_user_model
from datetime import datetime
from Payments.models import *
from datetime import datetime
# from django.db import connection
from django.db.models.query import Prefetch
from Sales.models import  CriticalityChange
from django.contrib.sites.shortcuts import get_current_site

User = get_user_model()

from datetime import timedelta


class totalClientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id')
    email = serializers.CharField(source='user.email')
    firstname = serializers.CharField(source='user.firstname')
    lastname = serializers.CharField(source='user.lastname')
    dateJoined = serializers.DateTimeField(source='user.dateJoined')
    subscription = serializers.SerializerMethodField()
    dueDate = serializers.SerializerMethodField()
    doctor_firstname = serializers.CharField(source='referalId.user.firstname')
    doctor_lastname = serializers.CharField(source='referalId.user.lastname')
    is_active = serializers.BooleanField(source='user.is_active')
    criticality = serializers.SerializerMethodField()
    week = serializers.SerializerMethodField()
    profile_pic = serializers.ImageField(source="user.profile_img")
    
    class Meta:
        model = CustomerDetails
        fields = ['id', 'firstname', 'lastname', 'email', 'age', 'location','dateJoined', 'dueDate', 'doctor_firstname', 'doctor_lastname', 'is_active','subscription','criticality', 'week', 'profile_pic']

    def get_week(self, obj):
        try:
            periods_date =  obj.Menstruation_date
            today = datetime.today().date()
            daysPregnant = today - periods_date
            week = daysPregnant.days/7
            return int(week)
        except Exception as e:
            return 1

    def get_criticality(self, obj):
        for instance in obj.user.criticality_change.all():
            try:
                return instance.criticallity.name
            except:
                return "stable"
        return "stable"

    def get_subscription(self, obj):
        membership = PurchasedMembership.objects.filter(user = obj.user,is_paid = True).order_by('-pk')


        if membership.exists():
            return membership[0].membership.membership_name
        
                   
        return "No plans"
        

    def get_dueDate(self, obj):
        try:
            return obj.Menstruation_date + timedelta(days=280)
        except Exception as e:
            return 0

    @staticmethod
    def pre_loader(queryset):
        queryset = queryset.prefetch_related(
            'user',
            'referalId',
            'referalId__user',
            Prefetch('user__criticality_change', queryset=CriticalityChange.objects.all().order_by('-date','-criticallity__criticality')), 
            Prefetch("user__sub_client", queryset=Subscriptions.objects.filter(is_active=True).prefetch_related('membership'))
        )
        return queryset

class NewDoctorSerializer(serializers.ModelSerializer):
    appointments  = serializers.SerializerMethodField()
   
    firstname = serializers.CharField(source='user.firstname')
    lastname = serializers.CharField(source='user.lastname')
    email = serializers.CharField(source='user.email')
    is_verified = serializers.CharField(source='user.is_verified')
    profile_full_url = serializers.SerializerMethodField()
    
    
    def get_serializer_context(self):
        return {'sort_by': self.request.GET.get('sort_by')}


    def get_appointments(self ,obj):
        from Appointments.serializers import AppointmentSerializer
        from django.db.models import Q
        from django.utils.timezone import make_aware
        queryset = Appointments.objects.filter(doctor = obj)
        
        print('########')
        print(queryset)
        print('########')

        if self.context.get('sort_by') == 'completed':
            dateTimeCompleted = datetime.now() - timedelta(minutes=60)
            queryset = queryset.filter(doctor=obj,approved=True,
            schedule__lte=make_aware(dateTimeCompleted)).order_by('-schedule')

            # queryset = queryset.filter(completed = True).order_by('date')
        
        if self.context.get('sort_by') == 'upcoming':
            queryset = queryset.filter(schedule__gte  = datetime.now(), rejected = False, approved = True).order_by('date')

        if self.context.get('search'):
            search = self.context.get('search')
            queryset = queryset.filter(
                Q(customer__user__firstname__icontains = search) |
                Q(customer__user__lastname__icontains = search) |
                Q(customer__age__icontains = search) |
                Q(schedule__icontains = search) 
            ).order_by('date')




    


        serializer = AppointmentSerializer(queryset , many = True)
        return serializer.data

    def get_profile_full_url(self, obj):
        request = self.context.get('request')
        try:
            return "https://" + str(get_current_site(request)) + "/media/" + str(obj.user.profile_img)
        except:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")



    class Meta:
        model = DoctorDetails
        fields = ['id' ,'firstname', 'hospitals','lastname', 'email', 'age', 'location',  'experience','qualification','speciality',  'gender', 'languages', 'referalId', 'is_verified', 'profile_full_url','appointments' ,]




class DoctorDetailSerializer(serializers.ModelSerializer):
    accountStatus = serializers.BooleanField(source='user.is_active')
    hospital_manager = serializers.SerializerMethodField()
    profile_full_url = serializers.SerializerMethodField()

    # new
    id = serializers.CharField(source='user.id')
    firstname = serializers.CharField(source='user.firstname')
    lastname = serializers.CharField(source='user.lastname')
    email = serializers.CharField(source='user.email')
    is_verified = serializers.CharField(source='user.is_verified')



    class Meta:
        model = DoctorDetails
        fields = ['id' ,'firstname', 'hospitals','lastname', 'email', 'age', 'location', 'councilRegNo', 'experience','qualification','speciality', 'accountStatus', 'price', 'gender', 'languages','hospital_manager', 'referalId', 'is_verified', 'profile_full_url']

    def get_profile_full_url(self, obj):
        request = self.context.get('request')
        try:
            return "https://" + str(get_current_site(request)) + "/media/" + str(obj.user.profile_img)
        except:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")

    def get_hospital_manager(self, obj):
        try:
            return obj.hospitalManager.user.firstname
        except:
            return ""

    # def get_age(self,obj):
    #     details = obj.docDetails.first()
    #     if details is not None:
    #         return details.age

    def get_gender(self,obj):
        details = obj.docDetails.first()
        if details is not None:
            return details.gender

    def get_languages(self,obj):
        details = obj.docDetails.first()
        if details is not None:
            return details.languages

    def get_price(self,obj):
        details = obj.docDetails.first()
        if details is not None:
            return details.price

    def get_location(self,obj):
        details = obj.docDetails.first()
        if details is not None:
            return details.location
    
    def get_councilRegNo(self,obj):
        details = obj.docDetails.first()
        if details is not None:
            return details.councilRegNo 
    
    def get_experience(self,obj):
        details = obj.docDetails.first()
        if details is not None:
            return details.experience 

    def get_qualification(self,obj):
        detail = obj.docDetails.first()
        if detail is not None:
            return detail.qualification

    def get_speciality(self,obj): 
        detail = obj.docDetails.first()
        if detail is not None:
            return detail.speciality





class SalesTeamSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='user.id')
    firstname = serializers.CharField(source='user.firstname')
    email = serializers.EmailField(source='user.email')
    accountStatus = serializers.BooleanField(source='user.is_active')
    password = serializers.CharField(source='passwordString')

    class Meta:
        model = SalesTeamDetails 
        fields = '__all__'
        extra_kwargs = {
            'passwordString' : {'write_only' : True},
            'user' : {'write_only' : True},
        }


class adminDashboardCountsSerializer(serializers.Serializer):
    totalConsultant = serializers.IntegerField()
    totalSalesTeam = serializers.IntegerField()
    activeClients = serializers.IntegerField()
    disabledDoctors = serializers.IntegerField()
    totalHospitals = serializers.IntegerField()
    totalDoctors = serializers.IntegerField()
    totalClients = serializers.IntegerField()



class AllExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercises
        exclude = ['stage']

class SubModuleSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="subModuleName")
    class Meta:
        model = ActivitySubModules
        fields = ['id', 'name', 'disabled'] #, 'date'


class ActivityMainModuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = ActivityMainModule
        exclude = ['stage']


class PositiveCriticalSymptomsSerializer(serializers.ModelSerializer):
    symptom = serializers.CharField(source="symptom.name")
    class Meta:
        fields = ['symptom', 'date', 'positive']
        model = PositiveCriticalSymptoms

    def to_representation(self, instance):
        representation = super(PositiveCriticalSymptomsSerializer, self).to_representation(instance)
        representation['date'] = instance.date.strftime("%d-%m-%Y")
        return representation

class CriticalSymptomSerializer(serializers.ModelSerializer):
    positive = serializers.SerializerMethodField()
    class Meta:
        model = CriticalSymptoms
        fields = ['id', 'name', 'positive']
        extra_kwargs = {
            'customer' : {'write_only' : True},
        }
    def get_positive(self,obj):
        for instance in obj.positive_symptom.all():
            try:
                return instance.positive
            except Exception:
                return False
        return False
    


class FreeContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreeContent
        fields = '__all__'