
from enum import unique
from faulthandler import disable
from logging import critical
from re import S
from django.db import models
from datetime import datetime
from django.db.models.fields import DateField, DateTimeField
from django.utils.html import word_split_re
from django.utils.timezone import make_aware
from django.utils.timezone import now
from LearnIt.models import Stage
from Sales.models import CriticalityChange, InvestigationCriticallity
from Analytics.models import Complications
from django.contrib.auth import get_user_model
User = get_user_model()


class BabyPics(models.Model):
    week = models.IntegerField()
    description = models.TextField(default='')
    length = models.CharField(max_length=50, null=True,blank=True)
    weigth = models.CharField(max_length=50,null=True,blank=True)
    size = models.CharField(max_length=50, default=0)
    image = models.ImageField(upload_to='BabyPics')

    # lookalike = models.ImageField(upload_to='BabyPics', null=True,blank=True)

    def __str__(self):
        return str(self.week) + " week"

    class Meta:
        verbose_name = 'Client Login Foetal Image'



# Excersice or Activity

# custom 

# ! activity and exercise 
class DailyTrackerModule(models.Model):
    name = models.CharField(max_length=100, null=True, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'daily tracker module'
        verbose_name_plural = 'daily tracker modules'


# ?modules inside activity(main modules)
class ActivityMainModule(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=500, null=True)
    url = models.URLField()
    description = models.TextField()
    disabled = models.BooleanField(default=False)

    class Meta:
        unique_together = ['stage', 'name'] #'dailyTrackerModule'

    def __str__(self):
        if self.name is not None:
            return self.name
        else:
            return ""


# ?sub modules inside Activity(sub modules)
class ActivitySubModules(models.Model):
    # dailyTrackerModule = models.ForeignKey(DailyTrackerModule, on_delete=models.CASCADE, null=True)
    ActivityMainModule = models.ForeignKey(ActivityMainModule, on_delete=models.CASCADE, related_name="sub_module",null=True)
    subModuleName = models.CharField(max_length=300,null=True)
    disabled = models.BooleanField(default=False)

    def __str__(self):
        return str(self.subModuleName)

    class Meta:
        verbose_name = 'Activity Sub modules'


# to record the completed exercise/activity
class CompletedActivity(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    daily_tracker_submodules = models.ForeignKey(ActivitySubModules, on_delete=models.CASCADE,related_name="Completed_activity",null=True)
    date = models.DateField()
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ['customer','date', 'daily_tracker_submodules']
        ordering = ['-date']


class CustomActivity(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    # DailyTrackerModule = models.ForeignKey(DailyTrackerModule, on_delete=models.CASCADE)  # exercise or activity
    name = models.CharField(max_length=200)


class CompletedCustomActivity(models.Model):
    # customer = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.ForeignKey(CustomActivity, on_delete=models.CASCADE, related_name='completedCustom')
    date = models.DateField()
    completed = models.BooleanField(default=False)


# diet tracker start
class Meal(models.Model):
    name = models.CharField(max_length=300, null=True, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Meal (Manual)"


class DietTracker(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, null=True)
    date = models.DateField(null=True)
    food = models.CharField(max_length=200)
    time = models.CharField(max_length=50)

    class Meta:
        unique_together = ['customer', 'date', 'meal']
        ordering = ['-date']

    def __str__(self):
        return self.food
# diet tracker end


# medicine tracker start
# ? morning, night, afternoon ...
class MedicineTime(models.Model):
    name = models.CharField(max_length=100, null=True, unique=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Medicine time(manual)'

# medicines taken by clients
class Medicines(models.Model):
    date = DateField(auto_now_add=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.ForeignKey(MedicineTime, on_delete=models.CASCADE, related_name="Medicines") 
    name = models.CharField(max_length=300, null=True)

    # def __str__(self):
    #     return self.name

    class Meta:
        unique_together = ['customer', 'time', 'name']


# to record the taken medicine
class TakenMedicine(models.Model):
    medicine = models.ForeignKey(Medicines, on_delete=models.CASCADE, related_name='MedicineDetail', null=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date = models.DateField()
    taken = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']
        unique_together = ['medicine', 'customer', 'date']


class SymptomsCategory(models.Model):
    name = models.CharField(max_length=100,primary_key=True)

    def __str__(self):
        return self.name


class Symptoms(models.Model):
    category = models.ForeignKey(SymptomsCategory, on_delete=models.CASCADE, null=True, blank=True,related_name="symptoms")
    name = models.CharField(max_length=200,null=True)
    criticality = models.ForeignKey(InvestigationCriticallity, on_delete=models.CASCADE, null=True, blank=True)
    complication = models.ManyToManyField(Complications, blank=True)
    
    def __str__(self):
        try:
            return self.name
        except:
            return "empty symptom"


class PositiveSymptoms(models.Model):
    symptom = models.ForeignKey(Symptoms, on_delete=models.CASCADE,related_name="positive_symptom")
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    positive = models.BooleanField(default=False)


class SymptomsInput(models.Model): 
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    others = models.CharField(max_length=500,null=True,blank=True) 
    bloodSugar = models.DecimalField(default=0, decimal_places=2, max_digits=100,null=True,blank=True)
    bloodPressure = models.DecimalField(default=0, decimal_places=2, max_digits=100,null=True,blank=True)
    weight = models.DecimalField(default=0, decimal_places=2, max_digits=100,null=True,blank=True)

    class Meta:
        unique_together = ['customer', 'date']


class CustomSymptoms(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    # date = models.DateField(null=True, blank=True)
    name = models.CharField(max_length=200, default="empty custom symptom")


class PositiveCustomSymptoms(models.Model):
    symptom = models.ForeignKey(CustomSymptoms, on_delete=models.CASCADE, related_name='positive_custom_symptom')
    date = models.DateField(null=True)
    positive = models.BooleanField(default=False)


class Exercises(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    name = models.CharField(max_length=500, null=False)
    disabled = models.BooleanField(default=False)


    def __str__(self):
        return self.name


class CompletedExercises(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercises, on_delete=models.CASCADE, related_name='completed_exercise')
    completed = models.BooleanField(default=False)
    date = models.DateField()

    def __str__(self):
        return self.exercise.name


class ExerciseVideos(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    url = models.URLField()


class CustomExercises(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['customer','name']
    

class CompletedCustomeExercises(models.Model):
    exercise = models.ForeignKey(CustomExercises, on_delete=models.CASCADE, related_name='completed_custom_exercise')
    date = models.DateField()
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ['exercise','date']



class Medical(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

    appointmentDate = models.DateField(null=True, blank=True)
    scantDate = models.DateField(null=True, blank=True)

    ultraSound = models.FileField(upload_to='ultrasound', null=True, blank=True) #ultraSound
    bloodReport = models.FileField(upload_to='bloodreport', null=True, blank=True)
    antenatalChart = models.FileField(upload_to='antenatal', null=True, blank=True)

    bp = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)

    question = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.customer.firstname

class PainScale(models.Model):
    name = models.CharField(max_length=200,null=True)

    class Meta:
        verbose_name = 'Pain Scale (manual)'
    
    def __str__(self):
        return self.name

class Contraction(models.Model):
    WORST_PAIN = "worst pain"
    SEVERE = 'severe'
    MODERATE = 'moderate'
    MILD = 'mild'
    NO_PAIN = 'no pain'
    PAIN_SCALE_CHOICES = (
        (WORST_PAIN,'worst pain'),
        (SEVERE, 'severe'),
        (MODERATE, 'moderate'),
        (MILD, 'mild'),
        (NO_PAIN, 'no pain')
    )
    painScale = models.CharField(choices=PAIN_SCALE_CHOICES,default=NO_PAIN,null=False,max_length=20)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    # painScale = models.ForeignKey(PainScale, on_delete=models.CASCADE, null=True)
    time_stamp = models.DateTimeField(auto_now_add=True)
    date = models.DateField(auto_now_add=True, null=True)
    time = models.TimeField()
    # contraction = models.CharField(max_length=10, null=True, blank=True)
    # interval = models.CharField(max_length=20, null=True, blank=True)
    contraction = models.IntegerField(null=True, blank=True)
    interval = models.DurationField(null=True)

    def __str__(self) :
        return self.customer.firstname

class LastUpdateDate(models.Model):
    date = datetime.now()
    timezone_aware_date = make_aware(date)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="last_update")
    diet = models.DateTimeField(default=now)
    medicine = models.DateTimeField(default=now)
    activity = models.DateTimeField(default=now)
    symptom = models.DateTimeField(default=now)
    exercise = models.DateTimeField(default=now)
    contraction = models.DateTimeField(default=now)

    def __str__(self):
        return self.customer.email

class CaloriesBurnt(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    value = models.DecimalField(default=0, decimal_places=5, max_digits=100)


class ExerciseConsent(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    criticalityChange = models.ForeignKey(CriticalityChange, on_delete=models.CASCADE, null=True)
    date = models.DateField()
    consent = models.BooleanField(default=False)