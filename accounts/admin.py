from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, CompanyAccount, Membership

# Register your models here.
@admin.register(User)
class UserAdmin(DjangoUserAdmin):
	fieldsets = DjangoUserAdmin.fieldsets + (
		("Echelon", {"fields": ("status",)}),
	)
	list_display = ("username", "email", "status", "is_staff", "is_superuser")
	search_fields = ("username", "email")

@admin.register(CompanyAccount)
class CompanyAccountAdmin(admin.ModelAdmin):
	list_display = ("name", "company_id", "created_at")
	search_fields = ("name", )

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
	list_display = ("user", "company", "role", "created_at")
	list_filter = ("role",)
	search_fields = ("user__username", "user__email", "company__name")