import os
from decouple import config
from pathlib import Path
from corsheaders.defaults import default_headers

# from rest_framework_api_key.permissions import BaseHasAPIKey

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-0^sp62isgl$w#+q4nzs0qmb^dsp0hu@f+s+(%0b4oi69_1ut34'

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = config('DEBUG', cast=bool)


ALLOWED_HOSTS = ['*','shebirth.herokuapp.com','localhost', '35.85.63.165']

# SMS_BACKEND = 'sms.backends.console.SmsBackend'
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # custom added
    'Accounts',
    'Admin',
    'Customer',
    'LearnIt',
    'Payments',
    'Doctor',
    'Appointments',
    'Sales',
    'Consultant',
    'EmailNotifications',
    'Messages',
    'Analytics',

    # external
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_api_key',
    'razorpay',
    # 'django_celery_beat',
    'django_email_verification',
    'debug_toolbar',
    'django_rest_passwordreset',
     'django_crontab',
    # 'django_otp',
    # 'django_otp.plugins.otp_totp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1',
]

ROOT_URLCONF = 'Shebirth.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Shebirth.wsgi.application'
DEBUG =True # False

DB = False

if DB:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
# else:
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.postgresql',
#             'NAME': 'july20',  # myproject
#             'USER': 'postgres',  # myprojectuser
#             'PASSWORD': '',  # password
#             'HOST': 'localhost',
#             'PORT': '5435',  # 5432
#         }
#     }
else:
    DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'defaultdb',  # myproject
                'USER': 'avnadmin',  # myprojectuser
                'PASSWORD': 'AVNS_zi4QhZLu6B3mU-FI3G4', # password
                'HOST': 'shebirthtest-satheeshakash07.aivencloud.com',
                'PORT': '17230',  # 5432
    }
}


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'shebirth2', #  myproject
#         'USER': 'postgres', # myprojectuser
#         'PASSWORD': '0480', # password
#         'HOST': 'localhost',
#         'PORT': '5432', #5432
#     }
# }


import dj_database_url
db_from_env = dj_database_url.config(conn_max_age=600)
DATABASES['default'].update(db_from_env)


PASSWORD =  'K*Pye*#li4$20z*21VDIk'




REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
          'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        # "rest_framework_api_key.permissions.HasAPIKey",
        # 'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}
# settings.py
API_KEY_CUSTOM_HEADER = "HTTP_API_KEY"




# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },

    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_L10N = True
USE_TZ = True
AUTH_USER_MODEL = 'Accounts.User'


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') 



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# CORS
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    'api-key',
]

# CORS_ALLOW_HEADERS = [
#     'accept',
#     'accept-encoding',
#     'authorization',
#     'content-type',
#     'dnt',
#     'origin',
#     'user-agent',
#     'x-csrftoken',
#     'x-requested-with',
#     'api-key'
# ]


# shebirth api
# wvX2ssin.THCtLxyXLXvBw7Blx0nfG4C2x9RUIHRS

# email notification settings

# EMAIL_USE_TLS = True
# EMAIL_PORT = 587
# EMAIL_HOST = 'smtp.hostinger.com'
# EMAIL_HOST_USER = 'buddy@shebirth.com'
# EMAIL_HOST_PASSWORD = 'Shebirth12345.'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'shebirthmail@gmail.com'
EMAIL_HOST_PASSWORD = 'lohtmicdvxihecel'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'





# twillio
SMS_BACKEND = 'sms.backends.twilio.SmsBackend'
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default="ad")
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default="ad")

# whatsapp number
WHATSAPP_NUMBER = config('WHATSAPP_NUMBER', default="ad")

# zoom api
ZOOM_API_KEY = "vxRe6uymSJeiwiyarLrgWw"
ZOOM_API_SEC = "YjcA6xKrwfPhUPZJSmefvlXHM9OtTB46exw8"



# Razor Pay
RAZOR_TEST_KEY_ID = "rzp_test_NssBWlBNPqnkAX"
RAZOR_TEST_API_ID = "xZLVuIuzWPtXGQHh9FuY2ZR9"


RAZOR_KEY_ID = "rzp_live_ZzpnKBVjhdD60I"
RAZOR_API_ID = "238bzTsxBqRKS00tCUHEgy0Y"


# 1 - 10
# 3 - 2

# KEY = config('KEY', default="ad")
# API = config('API', default="ad")


CELERY_BROKER_URL = 'redis://redis.oublme.ng.0001.usw2.cache.amazonaws.com:6379'
# CELERY_BROKER_URL = "amqp://localhost"
CELERY_RESULT_BACKEND = 'redis://redis.oublme.ng.0001.usw2.cache.amazonaws.com:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SELERLIZER = 'json'



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django_password_validators.password_character_requirements.password_validation.PasswordCharacterValidator',
        'OPTIONS': {
            'min_length_digit': 1,
            'min_length_special': 1,
            'min_length_upper': 1,
            'special_characters': "~!@#$%^&*()_+{}\":;'[]"
        },
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
]


# token expiry time in hours for forgot pasword
DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME = 1



CRONJOBS = [
    ('0 10 * * *', 'EmailNotifications.tasks.CurrentPlanExpiry'),
    ('0 10 * * *', 'EmailNotifications.tasks.NotUpdatedWithin7days'),

   
]
