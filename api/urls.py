from django.urls import path

from api.views import articles_view, validate_item_view, validate_all_view

urlpatterns = [
    path("articles/", articles_view, name="index"),
    path("validate/item/", validate_item_view, name="validate_item"),
    path("validate/all/", validate_all_view, name="validate_all"),
]