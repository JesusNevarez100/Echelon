from django.urls import path
from . import views
from .views import create_meeting

app_name = "scheduling"

urlpatterns = [
    path("", views.index, name="index"),
    path("meetings/", views.meetings_json),
    path("create/", views.create_meeting),
]
