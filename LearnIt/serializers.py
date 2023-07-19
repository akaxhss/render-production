from django.db.models import fields
from django.db.models.base import Model
from rest_framework import serializers
from .models import *
from Accounts.models import CustomerDetails
from django.contrib.auth import get_user_model
User = get_user_model() 


class AddVideoSerializers(serializers.ModelSerializer):
    video_id = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Videos
        fields = '__all__'
        extra_kwargs = {
            'module' : {'write_only' : True},
            'stage' : {'write_only' : True},
        }

    def get_video_id(self, obj):
        video_url = obj.url
        if video_url is not None:
            array = obj.url.split("watch?v=")
            if len(array) >=2:
                return array[1]
            else:
                return None



class NoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notes
        fields = '__all__'
        extra_kwargs = {
            'module' : {'write_only' : True},
            'stage' : {'write_only' : True},
            'customer' : {'write_only' : True},
        }



