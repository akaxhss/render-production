from django.contrib import admin
from django.urls import path, include
from .views import *
urlpatterns = [
    path('', landingPage),

    path('registration/', registration),
    path('client-registration/', client_registration),
    path('doctor-registration/', doctor_registration),
    path('sales-registration/', sales_registration),
    path('consultant-registration/', consultant_registration),
    path('hospital-registration/', hostpital_registration),
    path('logout/' , LogoutAPI.as_view()),
    path('login/', login_view),
    path('logout/', logout_view),
    path('login-user-data/', user_data),

    # Activate or deactivate
    path('activateOrDeactivate/', activate_or_deactivate),

    # Customer profile 
    path('customer-profile/', customer_profile),
    path('profile-update/', update_profile),

    # email verification
    path('send-verification-email/', email_verification),
    # otp verification
    path('otp-verification/', otp_verification),
    # password change
    path('password-change/', password_change),

    # forgot password
    path('password-reset-template/', reset_password),
    path('password-reset/', set_password, name="setPassword"),

    path('change-role/', change_roles),
    path('dad-registration/' , dad_registration),
    path('dad-dashboard/' , dad_dashboard),
    path('banner/' , BannerView.as_view()),
    path('symptom-remedy/', SymptomRemedyView.as_view(), ),
    path('video/', VideoLinkView.as_view(), ),

    

]
