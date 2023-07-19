from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from Customer.models import DailyTrackerModule
# Create your models here.

class CustomizedPlan(models.Model):
    DIET = 1
    EXERCISE = 2
    MODULE_CHOICES = (
        (DIET,'diet'),
        (EXERCISE, 'exercise'),
    )
    tracker = models.PositiveSmallIntegerField(choices=MODULE_CHOICES,blank=True,null=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    # module = models.ForeignKey(DailyTrackerModule, on_delete=models.CASCADE, null=True)
    # stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time = models.DateTimeField(auto_now_add=True, null=True)
    url = models.URLField()



