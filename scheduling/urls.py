from django.urls import path
from . import views

app_name = "scheduling"

urlpatterns = [
	path("", views.index, name="index"),
    path("api/meetings/", views.meetings_json, name="meetings_json"),
    path("api/meetings/create/", views.create_meeting, name="create_meeting")
]
