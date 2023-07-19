
from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path("add-videos/", add_videos),
    path("add-notes/", add_notes),
    path('get-module-data/', get_module_data),
]
