
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django_email_verification import urls as email_urls #new
import debug_toolbar
from django.views.static import serve
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Accounts.urls')),
    path('customer/', include('Customer.urls')),
    path('learning/', include('LearnIt.urls')),
    path('payments/', include('Payments.urls')),
    path('doctor/', include('Doctor.urls')),
    path('appointments/', include('Appointments.urls')),
    path('sales/', include('Sales.urls')),
    path('admin-panel/', include('Admin.urls')),
    path('consultant/', include('Consultant.urls')),
    path('hospital/', include('Hospital.urls')),
    path('messages/', include('Messages.urls')),
    path('analytics/', include('Analytics.urls')),

    # verify email
    path('email/', include(email_urls)),

    # debug toolbar
    path('__debug__/', include(debug_toolbar.urls)),


    # forgot password
    path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')), 
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += staticfiles_urlpatterns()

