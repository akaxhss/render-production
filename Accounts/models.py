from pyexpat import model
from statistics import mode
from django.core import validators
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
# from rest_framework.authtoken.models import Token
# from django.core.validators import RegexValidator
# from django.utils.html import MLStripper
# from Customer.models import LastUpdateDate
from .validators import *
# from django.contrib.auth import get_user_model
# User = get_user_model() 
# from django.db.models.signals import post_save
# from django.dispatch import receiver

# from datetime import datetime




class UserManager(BaseUserManager):

    def create_user(self, email,  password, firstname, lastname=None, mobile=None):
        if not email:
            raise ValueError('User must have an email')
                    
        if not password:
            raise ValueError('User must have a password')

        user = self.model(
            email = self.normalize_email(email)
        )

        user.set_password(password)
        user.firstname = firstname
        user.lastname = lastname
        user.mobile = mobile
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password, firstname, lastname):
        
        user = self.create_user(
            email,
            password=password,           
            firstname=firstname,           
            lastname=lastname,           
        )
        user.admin = True
        user.is_staff = True
        user.save(using=self._db)

        return user

    def create_patient(self,  email, password, firstname, lastname, mobile):
    
        user = self.create_user(
            email,
            password=password,
            firstname=firstname,
            lastname=lastname,
            mobile = mobile
        )
        user.role = User.CLIENT
        # user.patient = True
        user.is_active=True
        # user.is_otp_verified=False
        user.save(using=self._db)
        return user

    def create_doctor(self,  email, password, firstname, lastname, mobile):
    
        user = self.create_user(
            email,
            password=password,
            firstname=firstname,
            lastname=lastname,
            mobile = mobile
        )
        user.is_active=False
        # user.is_verified = False
        user.role = User.DOCTOR
        user.save(using=self._db)

        return user
    
    def create_sales(self,  email, password, firstname):
    
        user = self.create_user(
            email,
            password=password,
            firstname=firstname,
        )
        user.role = User.SALES
        # user.sales = True
        user.save(using=self._db)

        return user
    
    def create_consultant(self,  email, password, firstname):
        user = self.create_user(
            email,
            password=password,
            firstname=firstname,
        )
        # user.consultant = True
        user.role = User.CONSULTANT
        user.save(using=self._db)
        return user
    
    def create_hospitalManager(self,  email, password, firstname):
        user = self.create_user(
            email,
            password=password,
            firstname=firstname,
        )
        # user.hospitalManager = True
        user.role = User.HOSPITAL_MANAGER
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    ADMIN = 1
    DOCTOR = 2
    CLIENT = 3
    SALES = 4
    CONSULTANT = 5
    HOSPITAL_MANAGER = 6
    DAD = 7

    ROLE_CHOICES = (
        (ADMIN,'admin'),
        (DOCTOR, 'doctor'),
        (CLIENT, 'client'),
        (SALES, 'sales'),
        (CONSULTANT, 'consultant'),
        (HOSPITAL_MANAGER,'hospital_manager'),
        (DAD,'dad')

    )
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES,blank=True,null=True)
    email = models.EmailField(unique=True,max_length=300, default="example@email.com",blank=False)
    firstname = models.CharField(max_length=100, default="firstname", validators=[CheckIfAlpha])
    lastname = models.CharField(max_length=100, null=True, validators=[CheckIfAlpha])
    mobile = models.CharField(validators=[phone_regex], max_length=12, null=True, blank=True)
    profile_img = models.ImageField(upload_to='ProfilePic/', null=True,blank=True, default= '/ProfilePic/default.jpg')

    is_staff = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True) #to activate/deactivate account
    is_verified = models.BooleanField(default=True) #client = otp verification and doctor = admin aproval
    dateJoined = models.DateTimeField(auto_now_add=True, editable=True)
    fcm_token = models.TextField(null= True , blank=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    objects = UserManager()

    # def __str__(self):
    #     return self.id

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_admin(self):
        return self.admin
    
    class Meta:
        ordering =[ "email"]


class hospitalManagerDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='hospitalManagerDetails')
    location = models.CharField(max_length=200)
    passwordString = models.CharField(max_length=500)


class DoctorDetails(models.Model):
    FEMALE = "female"
    MALE = "male"

    GENDER_CHOICES = (
        (FEMALE,'female'),
        (MALE, 'male'),
    )

    # OBSTRETICIAN = "obstretician"
    # PAEDIATRICIAN = "paediatrician"
    # PSYCHIATRIST = "psychiatrist"
    # DEITICIAN = "deitician"
    # PSYCHOLOGIST = "psychologist"

    # SPECIALITY_CHOICES = (
    #     (OBSTRETICIAN, "obstretician"),
    #     (PAEDIATRICIAN, "paediatrician"),
    #     (PSYCHIATRIST, "psychiatrist"),
    #     (DEITICIAN, "deitician"),
    #     (PSYCHOLOGIST, "psychologist")
    # )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='docDetails',null=True)
    speciality = models.CharField(max_length=200, null=True)
    qualification = models.CharField(max_length=200, null=True)
    medicalCouncil = models.CharField(max_length=20, null=True)
    councilRegNo = models.CharField(max_length=200, null=True)
    hospitals = models.CharField(max_length=300, null=True)
    interests = models.CharField(max_length=200, null=True)
    placeOfWork = models.CharField(max_length=200, null=True)
    onlineConsultation = models.CharField(max_length=100, null=True)
    experience = models.IntegerField(default=0)
    age = models.IntegerField(default=0)
    languages = models.CharField(max_length=500 ,default='')
    location = models.CharField(max_length=200, null=True,blank=True)
    referalId = models.CharField(max_length=100, null=True,unique=True)
    price =  models.IntegerField(default=0)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=100, null=True, blank=True)
    # profile_img = models.ImageField(upload_to='ProfilePic/', null=True,blank=True)
    hospitalManager = models.ForeignKey(hospitalManagerDetails, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        if self.user is not None:
            return self.user.email
        else:
            return self.user.firstname


class ConsultantInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='consultantDetails')
    # age = models.IntegerField()
    location = models.CharField(max_length=200, null=True, blank=True)
    passwordString = models.CharField(max_length=500)

    def __str__(self) -> str:
        try:
            return self.user.email
        except Exception as e:
            return f'{self.id} this info deleted'


class CustomerDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='customer_details')
    age = models.IntegerField(null=True,blank=True)
    weight = models.IntegerField(null=True)
    job = models.CharField(max_length=100, null=True,blank=True, validators=[CheckIfAlpha])
    address = models.TextField(blank=True, null=True)
    husband = models.CharField(max_length=100, null=True,blank=True, validators=[CheckIfAlpha])
    location = models.CharField(max_length=100, null=True,blank=True)
    Idproof = models.FileField(upload_to='Idproof/', null=True,blank=True)

    marriedSince = models.DateField(null=True,blank=True)
    babies_number = models.IntegerField(null=True,blank=True)
    abortions = models.CharField(max_length=20, null=True,blank=True, validators=[yes_or_no_regex])
    twins = models.CharField(max_length=20, null=True,blank=True, validators=[yes_or_no_regex]) #, validators=[yes_or_no_Validation]
    diabetes = models.CharField(max_length=20, null=True,blank=True, validators=[yes_or_no_regex])
    allergic_reaction = models.CharField(max_length=200, null=True,blank=True)
    surgery = models.CharField(max_length=200, null=True,blank=True)
    Menstruation = models.CharField(max_length=200, null=True,blank=True) #integer field
    Menstruation_date = models.DateField(null=True,blank=False)

    hereditory = models.CharField(max_length=200, null=True,blank=True)
    gynacology = models.CharField(max_length=200, null=True,blank=True)
    no_of_babies_pregnant_with = models.CharField(max_length=200, null=True,blank=True) #integer field
    doctor_final_visit = models.DateField(null=True,blank=True)
    prescription = models.FileField(upload_to='Prescriptions/', null=True,blank=True)
    drugUse = models.CharField(max_length=10, null=True, blank=True,validators=[yes_or_no_regex])
    # patient of 
    referalId = models.ForeignKey(DoctorDetails, on_delete=models.CASCADE, null=True,blank=True, related_name='referal_doc')
    fcm_token = models.TextField(null = True , blank=True)

    def __str__(self):
        if self.user is not None:
            return self.user.email
        else:
            return ""

class FirebaseFcm(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='fcm_tokens')
    fcm_token = models.TextField(unique= True)



    




class SalesTeamDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='salesDetails')
    # age = models.IntegerField()
    location = models.CharField(max_length=200, null=True, blank=True)
    passwordString = models.CharField(max_length=500)


class Otp(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.IntegerField()
    validity = models.DateTimeField()



class DadInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='dad_details')
    age = models.IntegerField()
    wife_email  = models.CharField(max_length=500)
    wife_name  = models.CharField(max_length=500)

    def __str__(self) -> str:
        if self.user:
            return self.user.email
        
        return self.id




class Banner(models.Model):
    image = models.ImageField(upload_to = "banner")

# class LastUpdateDate(models.Model):
#     customer = models.ForeignKey(User, on_delete=models.CASCADE)
#     date = models.DateTimeField()

# @receiver(post_save, sender=User) 
# def tracker_last_update_date(sender, instance, created, **kwargs):
#     if created:
#         date = datetime.now()    
#         LastUpdateDate.objects.create(customer=instance, date=date)


class VideoLink(models.Model):
    text = models.CharField(max_length=100)
    link = models.TextField()

    def __str__(self) -> str:
        return self.text


class SymptomsRemedy(models.Model):
    symptom = models.CharField(max_length=100)
    remedy = models.TextField()

    def __str__(self) -> str:
        return self.symptom
