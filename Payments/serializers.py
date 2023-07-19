from rest_framework import serializers
from .models import *
from Payments.models import *

User = get_user_model()

# from datetime import timedelta
class MembershipPlanSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()






class Membership2Serializer(serializers.ModelSerializer):
    
    class Meta:
        model = MemberShip
        fields = '__all__'


class PurchasedMembershipSerializer(serializers.ModelSerializer):
    membership = Membership2Serializer()
    class Meta:
        model = PurchasedMembership
        fields = '__all__'
       # depth = 1