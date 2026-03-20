from django.urls import path

from . import views

app_name = "accounts_custom"

urlpatterns = [
    path("profile/", views.account_detail, name="account_detail"),
    path("profile/edit/", views.edit_account_detail, name="edit_account_detail"),
    path("users/", views.account_list, name="account_list"),
    path("create-user/", views.create_company_user, name="create_user"),
    path("force-profile-reset/", views.force_profile_reset, name="force_profile_reset"),
]
