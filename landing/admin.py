from django.contrib import admin
from django.utils import timezone

from .models import CompanyApplication, TesterFeedback


@admin.register(CompanyApplication)
class CompanyApplicationAdmin(admin.ModelAdmin):
    list_display = ("company_name", "applicant_name", "applicant_email", "status", "submitted_at")
    list_filter = ("status", "industry", "submitted_at")
    search_fields = ("company_name", "applicant_name", "applicant_email", "industry")
    readonly_fields = ("submitted_at",)
    fieldsets = (
        ("Company", {
            "fields": ("company_name", "company_website", "industry", "team_size"),
        }),
        ("Applicant", {
            "fields": ("applicant_name", "applicant_email", "applicant_phone", "applicant_title"),
        }),
        ("Review", {
            "fields": ("use_case", "status", "reviewed_at", "internal_notes"),
        }),
        ("Audit", {
            "fields": ("submitted_at",),
        }),
    )

    def save_model(self, request, obj, form, change):
        if change and "status" in form.changed_data and obj.status in {
            CompanyApplication.Status.APPROVED,
            CompanyApplication.Status.DENIED,
        } and obj.reviewed_at is None:
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(TesterFeedback)
class TesterFeedbackAdmin(admin.ModelAdmin):
    list_display = ("feedback_type", "module", "status", "submitted_by", "name", "email", "created_at")
    list_filter = ("feedback_type", "status", "module", "created_at")
    search_fields = ("message", "module", "page_url", "name", "email", "submitted_by__username")
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Reporter", {
            "fields": ("submitted_by", "name", "email"),
        }),
        ("Feedback", {
            "fields": ("feedback_type", "module", "page_url", "message"),
        }),
        ("Review", {
            "fields": ("status", "reviewed_at", "internal_notes"),
        }),
        ("Audit", {
            "fields": ("created_at",),
        }),
    )

    def save_model(self, request, obj, form, change):
        if change and "status" in form.changed_data and obj.status != TesterFeedback.Status.NEW and obj.reviewed_at is None:
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)
