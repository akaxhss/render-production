from rest_framework import serializers
from .models import *
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone
from django.utils.timezone import make_aware


class AllMessageSerializer(serializers.Serializer):
    sender = serializers.CharField(source="sender.firstname")
    receiver = serializers.CharField(source="receiver.firstname")
    message = serializers.CharField()
    date = serializers.DateTimeField(source="timestamp",format="%d-%m-%Y")
    time = serializers.DateTimeField(source="timestamp",format="%H:%M %p")
    ist_time = serializers.DateTimeField(source="ist_timestamp", format="%d-%m-%Y %H:%M %p", required=False)



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
    custom_date = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.user.profile_img:
            return "https://" + str(get_current_site(request)) + "/media/" + str(obj.user.profile_img)
        else:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")

    def get_custom_date(self, obj):
        user = obj.user
        logged_in_user = self.context.get('request').user

        if user.role == User.CLIENT:
            messages_sent = Messages.objects.filter(sender=user, receiver=logged_in_user)
            messages_received = Messages.objects.filter(receiver=user, sender=logged_in_user)

            last_message_sent = messages_sent.latest('timestamp').timestamp if messages_sent.exists() else None
            last_message_received = messages_received.latest('timestamp').timestamp if messages_received.exists() else None

            if last_message_sent is None and last_message_received is None:
                return user.dateJoined.strftime('%Y-%m-%d %H:%M:%S') if user.dateJoined else None

            if last_message_sent and last_message_received:
                last_message = max(last_message_sent, last_message_received)
            elif last_message_sent:
                last_message = last_message_sent
            else:
                last_message = last_message_received

            ist_time = last_message + timedelta(hours=5, minutes=30)
            return ist_time.strftime('%Y-%m-%d %H:%M:%S')

        return user.dateJoined.strftime('%Y-%m-%d %H:%M:%S') if user.dateJoined else None