from django.contrib import admin
from django.urls import path

from sellship.views import sendRegister_view, sendRegisterEbay_view, sendRegisterOtherSites_view

urlpatterns = [
    path("sendRegister", sendRegister_view, name="sendRegister"),
    path("sendRegister/ebay/", sendRegisterEbay_view, name="sendRegisterEbay"),
    path("sendRegister/other-sites/", sendRegisterOtherSites_view, name="sendRegisterOtherSites"),
]
