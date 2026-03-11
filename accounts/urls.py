from django.urls import path

from . import views

app_name = "accounts_custom"

urlpatterns = [
    path("create-user/", views.create_company_user, name="create_user"),
    path("force-profile-reset/", views.force_profile_reset, name="force_profile_reset"),
]
