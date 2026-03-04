from django.urls import path
from . import views

app_name = "scheduling"

urlpatterns = [
	path("", views.index, name="index")
]

