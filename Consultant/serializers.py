from Accounts.models import ConsultantInfo
from rest_framework import serializers
from .models import *
from django.contrib.sites.shortcuts import get_current_site


class CustomizedPlanSerializer(serializers.ModelSerializer):
    tracker = serializers.ChoiceField(choices=CustomizedPlan.MODULE_CHOICES)
    class Meta:
        model = CustomizedPlan
        fields = '__all__'
        extra_kwargs = {
            "module" : {'write_only' : 'True'},
            "customer" : {'write_only' : 'True'},
        }


class AllMessageSerializer(serializers.Serializer):
    sender = serializers.CharField(source="sender.firstname")
    receiver = serializers.CharField(source="receiver.firstname")
    message = serializers.CharField()
    date = serializers.DateTimeField(source="timestamp",format="%d-%m-%Y")
    time = serializers.DateTimeField(source="timestamp",format="%H:%M %p")


class ConsultantSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id")
    accountStatus = serializers.BooleanField(source='user.is_active', read_only=True)
    name = serializers.CharField(source='user.firstname', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    profile_pic = serializers.SerializerMethodField()
    class Meta:
        model = ConsultantInfo
        fields = ['id', 'name', 'email', 'location', 'accountStatus','profile_pic']

    def get_profile_pic(self, obj):
        request = self.context.get('request')
        if obj.user.profile_img:
            return "https://" + str(get_current_site(request)) + "/media/" + str(obj.user.profile_img)
        else:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")


class AllconsultantSerializer(serializers.Serializer):
    firstname = serializers.SerializerMethodField()
    # lastname = serializers.CharField()

    def get_firstname(self, obj):
        if obj.sender.consultant:
            return obj.sender.firstname
        else:
            return obj.receiver.firstname