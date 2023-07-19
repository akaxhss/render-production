from rest_framework import serializers
from .models import *
from django.contrib.sites.shortcuts import get_current_site


class AllMessageSerializer(serializers.Serializer):
    sender = serializers.CharField(source="sender.firstname")
    receiver = serializers.CharField(source="receiver.firstname")
    message = serializers.CharField()
    date = serializers.DateTimeField(source="timestamp",format="%d-%m-%Y")
    time = serializers.DateTimeField(source="timestamp",format="%H:%M %p")



class AllUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    firstname = serializers.CharField()
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.profile_img:
            return "https://" + str(get_current_site(request)) + "/media/" + str(obj.profile_img)
        else:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")
    # lastname = serializers.CharField()

    # def get_firstname(self, obj):
    #     if not obj.sender.patient and not obj.sender.admin:
    #         return obj.sender.firstname
    #     else:
    #         return obj.receiver.firstname


class AllClientSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="user.id")
    firstname = serializers.CharField(source="user.firstname")
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.user.profile_img:
            return "https://" + str(get_current_site(request)) + "/media/" + str(obj.user.profile_img)
        else:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")