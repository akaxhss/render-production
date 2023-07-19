from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model() 



class Complications(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class MedicalHistory(models.Model):
    PERSONAL_DETAILS = "Personal Details"
    MEDICAL_HISTORY = "Medical history"
    FAMILY_HISTORY = "Family History"
    LIFE_STYLE = "Life Style"

    CATEGORY_CHOICES = (
        (PERSONAL_DETAILS,'Personal Details'),
        (MEDICAL_HISTORY, 'Medical Details'),
        (FAMILY_HISTORY, 'Family Details'),
        (LIFE_STYLE, 'Life Style')
    )
    category = models.CharField(choices=CATEGORY_CHOICES,blank=True,null=True, max_length=20)
    name = models.CharField(max_length=100)
    complication = models.ManyToManyField(Complications)

    def __str__(self) :
        return self.name


class CustomerMedicalHistory(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE,related_name="client")
    medical_history = models.ForeignKey(MedicalHistory, on_delete=models.CASCADE, related_name="medical")
    flag = models.BooleanField(default=False,null=True,blank=True)

    def __str__(self):
        return self.medical_history.name


class PersonalDetails(models.Model):
    # YES = "yes"
    # NO = "no"
    # DOMESTIC_CHOICE = (
    #     (YES, "yes"),
    #     (NO, "no")
    # )

    UNDERWEIGHT = "underweight"
    NORMALWEIGHT = "normal weight"
    OVERWEIGHT = "over weight"
    # OBESE = "obese"
    BMI_CHOICE = (
        (UNDERWEIGHT, "underweight"),
        (NORMALWEIGHT, "normal weight"),
        (OVERWEIGHT, "over weight"),
        # (OBESE, "obese"),
    )
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"

    BLOOD_CHOICE = (
        (A_POSITIVE, "A+"),
        (A_NEGATIVE, "A-"),
        (B_POSITIVE, "B+"),
        (B_NEGATIVE, "B-"),
        (O_POSITIVE, "O+"),
        (O_NEGATIVE, "O-"),
        (AB_POSITIVE, "AB+"),
        (AB_NEGATIVE, "AB-")
    )
    customer = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(null=True, blank=True)
    bmi = models.CharField(choices=BMI_CHOICE ,max_length=20, null=True, blank=True)
    blood_group_mom = models.CharField(choices=BLOOD_CHOICE,max_length=20, null=True, blank=True)
    blood_group_dad = models.CharField(choices=BLOOD_CHOICE,max_length=20, null=True, blank=True)
    # domestic_voilence = models.CharField(choices=DOMESTIC_CHOICE, max_length=10, null=True, blank=True)
    domestic_voilence = models.BooleanField(default=False)
    frequency_of_call = models.IntegerField(default=0)
    notes = models.CharField(max_length=500, null=True, blank=True)


