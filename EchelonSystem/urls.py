"""
URL configuration for EchelonSystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

# Still need Billing, Scheduling, messaging, crypto, maybe audit
urlpatterns = [
    path("admin/", admin.site.urls),
	path("accounts/", include("django.contrib.auth.urls")),
	path("apps/accounts/", include("accounts.urls")),
    path("", include("landing.urls")),
	path("crm/", include("crm.urls")),
    path("services/", include("services.urls")),
	path("scheduling/", include("scheduling.urls")),
	path("billing/", include("billing.urls")),
	path('api/meetings/', include('scheduling.urls')),
	path(
		"password-change/done/",
		auth_views.PasswordChangeDoneView.as_view(),
		name="password_change_done"
	)
]
