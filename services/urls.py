from django.urls import path
from . import views

# Display Services URLs

app_name = "services"

urlpatterns = [
    path("", views.displayServices, name="services_home"),
    path("create/", views.createService, name="create_service")
]

