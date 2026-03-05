from django.urls import path
from . import views

app_name = "accounts_custom"

urlpatterns = [
	path("create-user/", views.create_company_user, name="create_user"),


]