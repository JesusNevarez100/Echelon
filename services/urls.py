from django.urls import path
from . import views

# Display Services URLs

app_name = "services"

urlpatterns = [
    path("", views.servicesHome, name="services_home"),
    path("<int:membership_id>/", views.displayServices, name="company_services"),
    path("<int:membership_id>/create/", views.createService, name="create_service"),
]

