from django.contrib import admin
from .models import Contact, Task

# Register your models here.
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
	list_display = ("name", "company", "type", "email", "phone", "created_at", "created_by")
	list_filter = ("type", "company")
	search_fields = ("name", "email", "phone", "company__name")

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
	list_display = ("title", "company", "status", "assigned_to", "due_at", "created_at")
	list_filter = ("status", "company")
	search_fields = ("title", "company__name", "assigned_to__email")