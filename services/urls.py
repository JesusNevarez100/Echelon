from django.urls import path
from . import views

# Display Services URLs

app_name = "services"

urlpatterns = [
	path("", views.index, name="index"),
	path("all/", views.displayServices, name="all")
]

