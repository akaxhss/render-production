
from rest_framework import serializers
from .models import *
# from django.contrib.auth import get_user_model
from datetime import timedelta
from datetime import timedelta, datetime
from django.contrib.sites.shortcuts import get_current_site
from Payments.models import PurchasedMembership

import sys, os

class RequestApprovalSerializer(serializers.ModelSerializer):
    doctor_firstname = serializers.CharField(source='doctor.user.firstname')
    doctor_lastname = serializers.CharField(source='doctor.user.lastname')

    client_firstname = serializers.CharField(source='customer.user.firstname')
    client_lastname = serializers.CharField(source='customer.user.lastname')
    class Meta:
        model = PatientDetailsApporval
        fields = '__all__'


class InvestigationSerializer(serializers.ModelSerializer):
    criticallity_value = serializers.CharField(source='criticallity.name', read_only=True)
    class Meta:
        model = Investigation
        fields = '__all__'


class InvestigationWithDescSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvestigationWithDescriptions
        fields = '__all__'

class CustomInvestigationSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomInvestigation
        fields = '__all__'



# filter for last updated 24hrs
# class Filtered2HoursUpdate(serializers.ListSerializer):
#     def to_representation(self, data):
#         data = data.filter(customer__is_active=True)
#         return super(Filtered2HoursUpdate, self).to_representation(data)


class CustomerLastUpdated24hoursSerilializer(serializers.Serializer):
    id = serializers.IntegerField(source='customer.id')
    firstname = serializers.CharField(source='customer.firstname')
    lastname = serializers.CharField(source='customer.lastname')
    accountStatus = serializers.BooleanField(source='customer.is_active')
    doctor_name = serializers.SerializerMethodField()
    dueDate = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    def get_doctor_name(self, obj):
        try:
            customerDetails = obj.customer.customer_details.first()
            return customerDetails.referalId.user.firstname + " " + customerDetails.referalId.user.lastname
        except:
            return ""
            
    def get_age(self, obj):
        try:
            customerDetails = obj.customer.customer_details.first()
            return customerDetails.age
        except:
            return ""
    
    def get_location(self, obj):
        try:
            customerDetails = obj.customer.customer_details.first()
            return customerDetails.location
        except:
            return ""

    def get_dueDate(self, obj):
        try:
            customerDetails = obj.customer.customer_details.first()
            return customerDetails.Menstruation_date + timedelta(days=280)
        except:
            return ""

    # class Meta:
    #     list_serializer_class = Filtered2HoursUpdate


class CustomerCallReposnseSerializer(serializers.ModelSerializer):
    # reponse = serializers.PrimaryKeyRelatedField(queryset=CallResponses.objects.all())
    callResponse = serializers.CharField(source='response.response', read_only=True)
    class Meta:
        model = CustomerCallReposnses
        fields = '__all__'
        extra_kwargs = {
            'customer' : {'write_only' : True},
            'response' : {'write_only' : True},
            'sales' : {'write_only' : True}
        }

# class CustomerCallReposnseSerializer(serializers.ModelSerializer):
#     # callResponse = serializers.CharField(source='response.response', read_only=True)
#
#     class Meta:
#         model = CustomerCallReposnses
#         fields = '__all__'
#         extra_kwargs = {
#             'customer': {'write_only': True},
#             'response': {'write_only': True},
#             'sales': {'write_only': True}
#         }
#
#     def create(self, validated_data):
#         customer = validated_data['customer']
#         date = validated_data['date']
#
#         # Create a new entry for the same customer and date
#         instance = CustomerCallReposnses.objects.create(
#             customer=customer,
#             date=date,
#             response=validated_data['response'],
#             sales=validated_data['sales']
#         )
#         return instance
class SalesSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='user.id')
    firstname = serializers.CharField(source='user.firstname')
    # lastname = serializers.CharField(source='user.lastname')
    email = serializers.EmailField(source='user.email')
    accountStatus = serializers.BooleanField(source='user.is_active')
    profile_pic = serializers.SerializerMethodField()

    def get_profile_pic(self, obj):
        request = self.context.get('request')
        if obj.user.profile_img:
            return "https://" + str(get_current_site(request)) + "/media/" + str(obj.user.profile_img)
        else:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")

    class Meta:
        model = SalesTeamDetails 
        fields = '__all__'
        extra_kwargs = {
            'passwordString' : {'write_only' : True},
            'user' : {'write_only' : True},
        }


class DisplayCallReposnseSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    response = serializers.CharField(source='response.response')
    class Meta:
        model = CustomerCallReposnses
        exclude = ['sales']

    def get_customer(self, obj):
        return obj.customer.firstname + ' ' + obj.customer.lastname


class ClientDetialSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    firstName = serializers.SerializerMethodField()
    lastName = serializers.SerializerMethodField()
    doctorFirstName = serializers.SerializerMethodField()
    doctorLastName = serializers.SerializerMethodField()
    dueDate = serializers.SerializerMethodField()
    week = serializers.SerializerMethodField()
    day = serializers.SerializerMethodField()
    criticality = serializers.SerializerMethodField()
    membership =serializers.SerializerMethodField()
    # location = serializers.SerializerMethodField()

    class Meta:
        model = CustomerDetails
        fields = ['id','membership' ,'firstName', 'lastName', 'doctorFirstName','doctorLastName', 'location', 'age', 'dueDate', 'week', 'day', 'criticality']

    def get_day(self, obj):
        try:
            daysPregnant = datetime.now().date() - obj.Menstruation_date
            return daysPregnant.days

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
        return 0

    def get_criticality(self, obj):
        for instance in obj.user.criticality_change.all():
            try:
                return instance.criticallity.name
            except:
                return "stable"
        return "stable"
    
    def get_membership(self ,obj):
        try:
            
            membership = PurchasedMembership.objects.filter(user = obj.user , is_paid = True).order_by('-pk')

            print("@@@@@@@")
            print(membership)
            print("@@@@@@@")


            return membership[0].membership.membership_name if membership.exists() else  "No Plans"
        except Exception as e:
            print(e)

        return "No Plans"



    def get_week(self, obj):
        try:
            periods_date =  obj.Menstruation_date
            today = datetime.now().date()
            daysPregnant = today - periods_date
            week = daysPregnant.days/7
            return int(week)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
        
        return 0


    def get_id(self, obj):
        return obj.user.id

    def get_firstName(self, obj):
        return obj.user.firstname

    def get_lastName(self, obj):
        return obj.user.lastname


    def get_doctorFirstName(self,obj):
        try:
            return obj.referalId.user.firstname
        except:
            return ""

    def get_doctorLastName(self, obj):
        try:
            return obj.referalId.user.lastname
        except:
            return ""

    def get_dueDate(self, obj):
        try:
            return obj.Menstruation_date + timedelta(days=280)
        except:
            return ""

    # def get_week(self, obj):
    #     # print(len(connection.queries))
    #     periods_date =  obj.customer_details.first().Menstruation_date
    #     today = datetime.now().date()
    #     daysPregnant = today - periods_date
    #     week = daysPregnant.days/7
    #     return int(week)

class CriticalityChangeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='customer.id')
    date = serializers.DateField(format="%d-%m-%Y")
    formated_date = serializers.DateField(source='date')
    criticallity = serializers.CharField(source="criticallity.name")
    class Meta:
        model = CriticalityChange
        fields = ['id' ,'date', 'criticallity','formated_date']



class SalesTeamCalledSerializer(serializers.ModelSerializer):
    customer_id = serializers.SerializerMethodField()
    callResponse = serializers.CharField(source='response')  # Use 'callResponse' as the source
    note = serializers.CharField()
    date = serializers.DateField()

    class Meta:
        model = SalesTeamCalled  # Use the correct model name
        fields = ['customer_id', 'callResponse', 'note', 'date']

    def get_customer_id(self, obj):
        return obj.customer.id


class CustomerCallReposnsesSerializer(serializers.ModelSerializer):
    response = serializers.CharField(source='response.response', read_only=True)  # Use 'response.response' as the source

    class Meta:
        model = CustomerCallReposnses
        fields = ['customer_id', 'response', 'note', 'date']