# from copy import error

from django.contrib.auth import authenticate
# from django.db.models import fields
from rest_framework import serializers
from django.contrib.auth.hashers import check_password
# from rest_framework.exceptions import ValidationError
# from rest_framework.fields import is_simple_callable
from .models import *
# from django.core.mail import send_mail
from Customer.models import LastUpdateDate

from django.conf import settings
# from django_email_verification import send_email
# for email


import random
import datetime
from django.utils import timezone
from datetime import timedelta
# import django.contrib.auth.password_validation as password_validators
from rest_framework.validators import UniqueValidator

from django.contrib.sites.shortcuts import get_current_site
from twilio.rest import Client 
account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)
# from Appointments.views import from_number, WhatsAppClient





# mobile number validation
# def isValid(mobile):
#     Pattern = re.compile("(0|91)?[7-9][0-9]{9}")
#     print(Pattern.search(mobile))
#     return Pattern.match(mobile)

class CustomerSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    doc_firstname = serializers.SerializerMethodField()
    doc_lastname = serializers.SerializerMethodField()
    dueDate = serializers.SerializerMethodField()
    week = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id','firstname', 'lastname', 'email', 'mobile','age', 'location', 'doc_firstname', 'doc_lastname', 'dueDate', 'week' , 'dateJoined']

    def get_location(self,obj):
        instance =  obj.customer_details.first()
        return instance.location

    def get_age(self, obj):
        instance =  obj.customer_details.first()
        return instance.age

    def get_doc_firstname(self,obj):
        instance =  obj.customer_details.first()
        try:
            return instance.referalId.user.firstname
        except:
            return ""

    def get_doc_lastname(self, obj):
        instance =  obj.customer_details.first()
        try:
            return instance.referalId.user.lastname
        except:
            return ""

    def get_dueDate(self, obj):
        try:
            return obj.customer_details.first().Menstruation_date + timedelta(days=280)
        except:
            return ""

    def get_week(self, obj):
        # print(len(connection.queries))
        periods_date =  obj.customer_details.first().Menstruation_date
        today = datetime.datetime.now().date()
        daysPregnant = today - periods_date
        week = daysPregnant.days/7
        return int(week)

    

        

class RegistrationSerializers(serializers.ModelSerializer):
    id = serializers.CharField( read_only=True)
    password2 = serializers.CharField(style={'input_type':'passsword'}, write_only=True, required=False)
    firstname = serializers.CharField(required=True)
    email = serializers.CharField(required=True,validators=[UniqueValidator(queryset=User.objects.all(),message="An account with this email already exists")])
    profile_pic = serializers.SerializerMethodField(read_only=True)
    fcm_token = serializers.CharField(allow_blank=True, required=False)



    class Meta:
        model = User
        fields = ['email', 'firstname', 'lastname', 'mobile', 'password', 'password2','id','profile_pic','role','fcm_token']
        extra_kwargs = {
            'password' : {'write_only':True},
            'lastname': {'required': True},
            'mobile': {'required': True},
            'role': {'required': True},
        }

    def save(self):
        password = self.validated_data.get('password', None)
        password2 = self.validated_data.get('password2', None)
        email = self.validated_data.get('email',None)
        firstname = self.validated_data.get('firstname', None)
        lastname = self.validated_data.get('lastname', None)
        mobile = self.validated_data.get('mobile', None)
        # age = self.validated_data.get('age', '')
        # patient = self.validated_data.get('patient', False)
        # doctor = self.validated_data.get('doctor', False)
        # sales = self.validated_data.get('sales', False)
        # consultant = self.validated_data.get('consultant', False)
        # hospitalManager = self.validated_data.get('hospitalManager', False)
        role = self.validated_data.get('role', None)

       
        if email is not None:
            email = email.lower()
            if role == User.CLIENT:
                user = User.objects.create_patient(email=email,password=password, firstname=firstname, lastname=lastname, mobile=mobile)
                LastUpdateDate.objects.get_or_create(customer=user)
                # sending otp to client whatsapp
                otp = random.randint(11111,99999)
                # print(timezone.timedelta(minutes=1))
                Otp.objects.get_or_create(client=user, otp=otp, validity=timezone.now() + datetime.timedelta(minutes=10))
                clientMobile = 'whatsapp:91{number}'.format(number=user.mobile)
                message = "Your One-Time Password to register with SheBirth is *{}* and it is only valid for 10 minutes".format(otp)
                # client.messages.create(from_='whatsapp:+14155238886',body=message,to=clientMobile)
            elif role == User.DOCTOR:
                user = User.objects.create_doctor(email=email,password=password, firstname=firstname, lastname=lastname, mobile=mobile)                
            elif role == User.SALES:
                user = User.objects.create_sales(email=email,password=password, firstname=firstname)
            elif role == User.CONSULTANT:
                user = User.objects.create_consultant(email=email,password=password, firstname=firstname)
            elif role == User.HOSPITAL_MANAGER:
                user = User.objects.create_hospitalManager(email=email,password=password, firstname=firstname)
            else:
                raise serializers.ValidationError({'Error':'User type not defined'})
            return user

    def validate_email(self, value):
        lower_email = value.lower()
        if User.objects.filter(email__iexact=lower_email).exists():
            raise serializers.ValidationError("An account with this email already exists")
        return lower_email

    def get_profile_pic(self, obj):
        request = self.context.get('request')
        try:
            return "https://" + str(get_current_site(request)) + "/media/" + str(obj.profile_img)
        except:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()
    fcm_token = serializers.CharField()

    def validate(self, data):
        email = data.get('email', '')
        password = data.get('password', '')

        try:
            user = User.objects.get(email__iexact=email)
            if user.role == User.CLIENT and not user.is_verified:
                raise  serializers.ValidationError({'error' : 'Your account is not otp verified'})
            if user.role == User.DOCTOR and not user.is_verified:
                raise  serializers.ValidationError({'error' : 'Your account is not verified by admin'})

        except User.DoesNotExist:
            raise serializers.ValidationError({'error' : 'Account with this email not found'})
        
        if user is not None:
            if not check_password(password, user.password):
                raise serializers.ValidationError({'password' : 'Incorrect password'})
            # check if it is client and a/c is activated and has she passed 42 weeks 
            if user.role == User.CLIENT:
                Subscription = User.objects.filter(id=user.id,is_active=True)
                if not user.is_active and Subscription:
                    raise serializers.ValidationError({"error" : "Admin needs to activate your account to login"})
                threshold_date = datetime.datetime.now().date() - timedelta(days=294) #42 weeks
                try:
                    details = user.customer_details.first()
                except CustomerDetails.DoesNotExist:
                    raise serializers.ValidationError({"error" : "customer profile not found"})
                
                if details.Menstruation_date <= threshold_date:
                    raise serializers.ValidationError({'error' : 'You have completed 42 weeks'})


        if email and password:
            user = authenticate(username=email.lower(), password=password)
            if user:
                data['user'] = user
            else:
                raise serializers.ValidationError({'credentials' : 'Invalid credentials or Account is deactivated'})
        return data


class DoctorRegSerializer(serializers.ModelSerializer):
    referalId = serializers.CharField(required=True,validators=[UniqueValidator(queryset=DoctorDetails.objects.all(),message="referal id must be unique")])
    class Meta:
        model = DoctorDetails
        fields = '__all__'


# Profile Update Serializers .
class UpdateSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(style={'input_type':'passsword'}, read_only=True)
    class Meta:
        model = User
        # fields = '__all__'
        exclude = ['password', 'last_login', 'is_staff', 'dateJoined','is_verified', 'is_active']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'mobile': {'required': True},
            'location': {'required': True},  # Make location field mandatory
            # Add other fields here with required=True as needed
        }

class CustomerDetailsSerializer(serializers.ModelSerializer):
    # idproof_filename = serializers.SerializerMethodField(read_only=True)
    class Meta: 
        model = CustomerDetails
        fields = '__all__'
        extra_kwargs = {
            'referalId': {'required': False}
        }

    def get_idproof_filename(self,obj):
        try:
            array = obj.Idproof.url.split("/")  
            return array[3]
        except:
            return ""




class DocDetailSerializer(serializers.ModelSerializer):
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

class SalesTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesTeamDetails
        fields = '__all__'


class ConsultantInfoSerializer(serializers.ModelSerializer):
    accountStatus = serializers.BooleanField(source='user.is_active', read_only=True)
    name = serializers.CharField(source='user.firstname', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    profile_pic = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsultantInfo
        fields = ['name', 'email', 'location', 'passwordString', 'accountStatus','user', 'profile_pic']

    def get_profile_pic(self, obj):
        request = self.context.get('request')
        if obj.user.profile_img:
            return "https://" + str(get_current_site(request)) + "/media/" + str(obj.user.profile_img)
        else:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")

class HospitalDetailSerializer(serializers.ModelSerializer):
    accountStatus = serializers.BooleanField(source='user.is_active', read_only=True)
    name = serializers.CharField(source='user.firstname', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    class Meta:
        model = hospitalManagerDetails
        fields = '__all__'



class DadSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self , obj):
        return {'firstname' : obj.user.firstname , 'lastname' : obj.user.lastname,
        'email' :obj.user.email,
        'mobile' : obj.user.mobile,
        'profile_img' : '/media/' + str(obj.user.profile_img),

        
        }
    class Meta:
        model = DadInfo
        fields = '__all__'
        depth = 1
     

class DadRegisterSerializer(serializers.Serializer):
    age = serializers.IntegerField()
    wife_email = serializers.EmailField()
    wife_name = serializers.CharField()
    email = serializers.EmailField()
    mobile = serializers.CharField()
    firstname = serializers.CharField()
    lastname = serializers.CharField()
    profile_img  = serializers.ImageField()
    password  = serializers.CharField()



    def create(self, validated_data):
        try:
       
            _user = User.objects.create(
                email = validated_data['email'],
                firstname = validated_data['firstname'] ,
                lastname = validated_data['lastname'],
                mobile = validated_data['mobile'],
                profile_img = validated_data['profile_img'],
                role = 7
            )
            _user.set_password(validated_data['password'])
            _user.save()

            dad = DadInfo.objects.create(
                user = _user,
                age = validated_data['age'] ,
                wife_email = validated_data['wife_email'],
                wife_name = validated_data['wife_name'],
            )

            return validated_data
        except Exception as e:
            print('@@')
            print(e)
            print('@@')

        
        return {}





class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'


class VideoLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoLink
        fields = '__all__'

class SymptomsRemedySerializer(serializers.ModelSerializer):
    class Meta:
        model = SymptomsRemedy
        fields = '__all__'