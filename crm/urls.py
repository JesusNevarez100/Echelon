from django.urls import path
from . import views

app_name = "crm"

urlpatterns = [
    path("", views.index, name="index"),
    path("tasks/create/", views.create_task, name="create_task"),
    path("contacts/create/", views.create_contact, name="create_contact")
]