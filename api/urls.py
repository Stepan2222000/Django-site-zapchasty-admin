from django.urls import path

from api.views import articles_view

urlpatterns = [
    path("articles/", articles_view, name="index"),
]