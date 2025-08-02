from django.contrib import admin
from django.urls import path

from sellship.views import sendRegister_view

urlpatterns = [
    path("sendRegister", sendRegister_view, name="index"),
]
