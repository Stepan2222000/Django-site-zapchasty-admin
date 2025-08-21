from django.contrib import admin
from django.urls import path

from sellship.views import index_view, sendRegister_view, sendRegisterEbay_view, sendRegisterOtherSites_view, items_view, delete_shipping_item, edit_shipping_item

urlpatterns = [
    path("", index_view, name="index"),
    path("items/", items_view, name="items"),
    path("items/delete/<int:item_id>/", delete_shipping_item, name="delete_shipping_item"),
    path("items/edit/<int:item_id>/", edit_shipping_item, name="edit_shipping_item"),
    path("sendRegister", sendRegister_view, name="sendRegister"),
    path("sendRegister/ebay/", sendRegisterEbay_view, name="sendRegisterEbay"),
    path("sendRegister/other-sites/", sendRegisterOtherSites_view, name="sendRegisterOtherSites"),
]
