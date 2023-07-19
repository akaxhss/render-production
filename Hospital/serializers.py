from rest_framework import serializers
from .models import *
from Accounts.models import DoctorDetails

class DoctorDetailSerializer(serializers.ModelSerializer):
    firstname = serializers.CharField(source='user.firstname')
    lastname = serializers.CharField(source='user.lastname')
    email = serializers.EmailField(source='user.email')
    # age = serializers.SerializerMethodField()
    # location = serializers.SerializerMethodField()
    # councilRegNo = serializers.SerializerMethodField()
    # experience = serializers.SerializerMethodField()
    accountStatus = serializers.BooleanField(source='user.is_active')

    class Meta:
        model = DoctorDetails
        fields = ['id' ,'firstname', 'lastname', 'email', 'age', 'location', 'councilRegNo', 'experience', 'accountStatus']

    def get_name(self,obj):
        return obj.user.firstname + ' ' + obj.user.lastname