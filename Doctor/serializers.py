from logging import critical
from Accounts.models import CustomerDetails, DoctorDetails
from rest_framework import fields, serializers

from Sales.models import CriticalityChange
from .models import *
from django.contrib.auth import get_user_model
from datetime import timedelta, datetime
from django.contrib.sites.shortcuts import get_current_site

User = get_user_model() 


class MyPatientSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id")
    dueDate = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    accountStatus = serializers.BooleanField(source='user.is_active')
    criticality = serializers.SerializerMethodField()
    currentWeek = serializers.SerializerMethodField()
    days = serializers.SerializerMethodField()
    firstname = serializers.CharField(source="user.firstname")
    lastname = serializers.CharField(source="user.lastname")
    profile_pic = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerDetails
        fields = ['id', 'firstname', 'lastname', 'age', 'location', 'dueDate', 'accountStatus', 'criticality', 'currentWeek', 'days', 'profile_pic']

    def get_profile_pic(self,obj):
        request = self.context.get('request')
        if obj.user.profile_img:
            return "https://" + str(get_current_site(request)) + "/media/" + str(obj.user.profile_img)
        else:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")
            
    def get_currentWeek(self, obj):
        # instance = obj.customer_details.first()
        periods_date = obj.Menstruation_date
        daysPregnant = datetime.now().date() - periods_date
        return  int(daysPregnant.days / 7)
        # return  int((daysPregnant.days % 365) / 7)

    def get_days(self, obj):
        daysPregnant = datetime.now().date() - obj.Menstruation_date
        return daysPregnant.days

    
    def get_criticality(self, obj):
        for instance in obj.user.criticality_change.all():
            try:
                return instance.criticallity.name
            except:
                return "stable"
        return "stable"
        # try:
        #     instance = obj.user.client_investigation.first()
        #     return instance.criticallity.name
        # except:
        #     return "stable"

    def get_dueDate(self, obj):
        # instance = obj.customer_details.first()
        return obj.Menstruation_date + timedelta(days=280)

    def get_location(self, obj):
        # instance = obj.customer_details.first()
        return obj.location

    def get_age(self, obj):
        # instance = obj.customer_details.first()
        return obj.age

# clients this month serializer
class ClientThisMonthSerializers(serializers.ModelSerializer):
    dueDate = serializers.SerializerMethodField()
    firstname = serializers.CharField(source='user.firstname')
    lastname = serializers.CharField(source='user.lastname')
    accountStatus = serializers.BooleanField(source='user.is_active')
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = CustomerDetails
        fields = ['firstname', 'lastname', 'age', 'location', 'dueDate', 'accountStatus','profile_pic']


    def get_profile_pic(self,obj):
        request = self.context.get('request')
        if obj.user.profile_img:
            return "https://" + str(get_current_site(request)) + "/media/" + str(obj.user.profile_img)
        else:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")

    def get_dueDate(self, obj):
        # instance = obj.customer_details.first()
        return obj.Menstruation_date + timedelta(days=280)


    def get_age(self, obj):
        instance = obj.customer_details.first()
        return instance.age


class GraphDataSerializer(serializers.Serializer):
    month = serializers.DateField(format='%B')
    appointments = serializers.IntegerField()
    cancelled = serializers.IntegerField()
    # month = serializers.SerializerMethodField()

    # def get_month(self, obj)

    

    



class DoctorProfileSerialzer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id")
    firstname = serializers.CharField(source='user.firstname')
    lastname = serializers.CharField(source='user.lastname')
    email = serializers.EmailField(source='user.email')
    mobile = serializers.CharField(source='user.mobile')
    profile_full_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta: 
        model = DoctorDetails
        fields = '__all__'
        
    def get_profile_full_url(self, obj):
        request = self.context.get('request')
        try:
            return "https://" + str(get_current_site(request)) + "/media/" + str(obj.user.profile_img)
        except:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")