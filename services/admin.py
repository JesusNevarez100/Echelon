from django.contrib import admin
from .models import Service, ServiceRequest


# Register your models here.
@admin.register(Service)
class ServicesAdmin(admin.ModelAdmin):
	list_display = ("name", "company", "active", "base_price_cents", "created_at")
	list_filter = ("active", "company")
	search_fields = ("name", "company__name")

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
	list_display = ("service", "company", "status", "requested_by", "requested_at", "completed_at")
	list_filter = ("service", "company")
	search_fields = ("service__name", "company__name", "requested_by__email")

