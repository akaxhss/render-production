from rest_framework import serializers
from .models import PersonalDetails, MedicalHistory

class PersonalDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalDetails
        fields = '__all__'

class MedicalHistorySerializer(serializers.ModelSerializer):
    flag = serializers.SerializerMethodField()
    class Meta:
        model = MedicalHistory
        exclude = ['complication']

    def get_flag(self, obj):
        for i in obj.medical.all():
            try:
                return i.flag
            except:
                return False
        return False
        