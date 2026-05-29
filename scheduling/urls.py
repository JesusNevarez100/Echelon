from django.urls import path
from . import views

app_name = "scheduling"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_meeting, name="create_meeting"),
    path("meetings/", views.meetings_json, name="meetings_json"),
]
