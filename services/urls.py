from django.urls import path
from . import views

# Display Services URLs

app_name = "services"

urlpatterns = [
    path("all/", views.allServices, name="all_services"),
    path('<uuid:company_id>/', views.displayServices, name='company_services'),
]

