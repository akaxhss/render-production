# from django.db.models import fields
from rest_framework import serializers
from django.utils.timezone import make_aware
from .models import *
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site

User = get_user_model() 


class BookingSerializer(serializers.ModelSerializer):   
    formated_date = serializers.DateTimeField(source="schedule", format="%d-%m-%Y", read_only=True)
    formated_time = serializers.DateTimeField(source="schedule",read_only=True, format="%I:%M %p") 
    clientName = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    meeting_open = serializers.BooleanField(default=False, read_only=True)
    week = serializers.SerializerMethodField(read_only=True)
    days = serializers.SerializerMethodField(read_only=True)
    client_profile_pic = serializers.SerializerMethodField()
    doctor_profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = Appointments
        fields = '__all__'
        extra_kwargs = {
            'completed' : {'write_only' : True},
            'approved' : {'write_only' : True},
            'rejected' : {'write_only' : True},
            'rescheduled_by_doctor' : {'write_only' : True},
            'rescheduled_by_client' : {'write_only' : True},
            'doctor' : {'write_only' : True},
            'customer' : {'write_only' : True},
        }

    def get_week(self, obj):
        periods_date =  obj.customer.Menstruation_date
        today = datetime.now().date()
        daysPregnant = today - periods_date
        week = daysPregnant.days/7
        return int(week)

    def get_days(self, obj):
        periods_date =  obj.customer.Menstruation_date
        today = datetime.now().date()
        days_pregnant = today - periods_date
        days_completed = (days_pregnant.days % 365) % 7
        return int(days_completed)

    def get_client_profile_pic(self, obj):
        profile_img =  obj.customer.user.profile_img
        request = self.context.get('request')
        if profile_img:
            return "https://" + str(get_current_site(request)) + "/media/" + str(profile_img)
        else:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")

    def get_doctor_profile_pic(self, obj):
        profile_img =  obj.doctor.user.profile_img
        request = self.context.get('request')
        if profile_img:
            return "https://" + str(get_current_site(request)) + "/media/" + str(profile_img)
        else:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")

        



    def get_clientName(self, obj):
        lastname = obj.customer.user.lastname
        if lastname != None:
            return obj.customer.user.firstname + " " + lastname
        return obj.customer.user.firstname 
        

    def get_location(self, obj):
        location = obj.customer.location
        if location != None:
            return location
        return ""


class CompletedSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    doctor = serializers.SerializerMethodField()
    experience = serializers.IntegerField(source='doctor.experience')
    qualification = serializers.CharField(source='doctor.qualification')
    time = serializers.DateTimeField(format="%I:%M %p", source="schedule")
    date = serializers.DateTimeField(format="%d-%m-%Y", source="schedule")
    client_profile_pic = serializers.SerializerMethodField()
    doctor_profile_pic = serializers.SerializerMethodField()

    def get_client_profile_pic(self, obj):
        profile_img =  obj.customer.user.profile_img
        request = self.context.get('request')
        if profile_img:
            return "https://" + str(get_current_site(request)) + "/media/" + str(profile_img)
        else:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")

    def get_doctor_profile_pic(self, obj):
        profile_img =  obj.doctor.user.profile_img
        request = self.context.get('request')
        if profile_img:
            return "https://" + str(get_current_site(request)) + "/media/" + str(profile_img)
        else:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")


    def get_time(self, obj):
        return obj.time.strftime("%I:%M %p")

    def get_doctor(self, obj):
        if obj.doctor.user.lastname is not None:
            return obj.doctor.user.firstname + " " + obj.doctor.user.lastname
        return obj.doctor.user.firstname
            

class TodaysAppointmentSerializer(serializers.ModelSerializer):
    firstname = serializers.CharField(source='customer.user.firstname')
    lastname = serializers.CharField(source='customer.user.lastname')
    time = serializers.DateTimeField(source="schedule", format="%H:%M %p")
    date = serializers.DateTimeField(source="schedule", format="%d-%m-%Y")
    meeting_open = serializers.BooleanField(default=False)
    location = serializers.CharField(source="customer.location")
    week = serializers.SerializerMethodField()
    days = serializers.SerializerMethodField()
    client_profile_pic = serializers.ImageField(source='customer.user.profile_img')
    doctor_profile_pic = serializers.ImageField(source='doctor.user.profile_img')

    class Meta:
        model = Appointments
        fields = ['id', 'firstname','lastname','time','date', 'meeting_url','meeting_open', 'location', 'week', 'days','doctor_profile_pic', 'client_profile_pic']

    def get_week(self, obj):
        periods_date =  obj.customer.Menstruation_date
        today = datetime.now().date()
        daysPregnant = today - periods_date
        week = daysPregnant.days/7
        return int(week)

    def get_days(self, obj):
        periods_date =  obj.customer.Menstruation_date
        today = datetime.now().date()
        days_pregnant = today - periods_date
        days_completed = (days_pregnant.days % 365) % 7
        return int(days_completed)


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointments
        fields = '__all__'
        depth = 2


class ClientAppointmentPaymentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    doctor_firstname = serializers.CharField(source="doctor.user.firstname")
    doctor_lastname = serializers.CharField(source="doctor.user.lastname")
    doctor_qualification = serializers.CharField(source="doctor.qualification")
    doctor_experience = serializers.CharField(source="doctor.experience")
    payment = serializers.IntegerField(source="doctor.price")


class UpcomingAppointmentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    doctor_firstname = serializers.CharField(source="doctor.user.firstname")
    doctor_lastname = serializers.CharField(source="doctor.user.lastname")
    doctor_qualification = serializers.CharField(source="doctor.qualification")
    doctor_experience = serializers.IntegerField(source="doctor.experience")
    date = serializers.DateTimeField(source="schedule" ,format="%d-%m-%Y")
    time = serializers.DateTimeField(source="schedule",format="%I:%M %p")
    meeting_url = serializers.CharField()
    client_profile_pic = serializers.SerializerMethodField()
    doctor_profile_pic = serializers.SerializerMethodField()

    def get_client_profile_pic(self, obj):
        profile_img =  obj.customer.user.profile_img
        request = self.context.get('request')
        if profile_img:
            return "https://" + str(get_current_site(request)) + "/media/" + str(profile_img)
        else:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")

    def get_doctor_profile_pic(self, obj):
        profile_img =  obj.doctor.user.profile_img
        request = self.context.get('request')
        if profile_img:
            return "https://" + str(get_current_site(request)) + "/media/" + str(profile_img)
        else:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")


class SummarySerializerClientSide(serializers.Serializer):
    doctor_firstname = serializers.CharField(source="doctor.user.firstname")
    doctor_lastname = serializers.CharField(source="doctor.user.lastname")
    qualification = serializers.CharField(source="doctor.qualification")
    experience = serializers.CharField(source="doctor.experience")
    profile_img = serializers.SerializerMethodField()
    mobile = serializers.IntegerField(source="doctor.user.mobile")

    def get_profile_img(self, obj):
        profile_img =  obj.doctor.user.profile_img
        request = self.context.get('request')
        if profile_img:
            return "https://" + str(get_current_site(request)) + "/media/" + str(profile_img)
        else:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")


class SummarySerializerDoctorSide(serializers.Serializer):
    client_firstname = serializers.CharField(source="customer.user.firstname")
    client_lastname = serializers.CharField(source="customer.user.lastname")
    age = serializers.CharField(source="customer.age")
    profile_img = serializers.SerializerMethodField()
    mobile = serializers.IntegerField(source="doctor.user.mobile")

    def get_profile_img(self, obj):
        profile_img =  obj.customer.user.profile_img
        request = self.context.get('request')
        if profile_img:
            return "https://" + str(get_current_site(request)) + "/media/" + str(profile_img)
        else:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")
