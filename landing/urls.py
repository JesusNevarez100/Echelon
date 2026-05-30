from django.urls import path
from . import views

app_name = "landing"

urlpatterns = [
	path("", views.landing, name="landing"),
	path("apply/", views.company_application, name="company_application"),
	path("dashboard/", views.dashboard, name="dashboard"),
]
