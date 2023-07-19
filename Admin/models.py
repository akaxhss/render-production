from Analytics.models import Complications
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class CriticalSymptoms(models.Model):
    name = models.CharField(max_length=200, unique=True)
    complication = models.ManyToManyField(Complications)

    def __str__(self):
        # try:
        return self.name
        # except:
        #     return "empty symptom"


# class PositiveCriticalSymptoms(models.Model):
#     symptom = models.ForeignKey(CriticalSymptoms, on_delete=models.CASCADE,related_name="positive_symptom")
#     customer = models.ForeignKey(User, on_delete=models.CASCADE)
#     date = models.DateField()
#     positive = models.BooleanField(default=False)


class PositiveCriticalSymptoms(models.Model):
    symptom = models.ForeignKey(CriticalSymptoms, on_delete=models.CASCADE,related_name="positive_symptoms")
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    positive = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class FreeContent(models.Model):
    name = models.CharField(max_length=100)
    video_url = models.TextField()
    crew = models.CharField(max_length=1000)