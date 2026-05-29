from django.contrib import admin
from .models import Meeting, MeetingParticipant, MeetingRequest

# Register your models here.
@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
	list_display = ("title", "company", "organizer", "start_at", "end_at", "location", "status", "is_billable", "billing_type", "bill_rate_cents")
	list_filter = ("company", "status", "is_billable", "billing_type")
	search_fields = ("title", "company__name", "organizer__email")

@admin.register(MeetingRequest)
class MeetingRequestAdmin(admin.ModelAdmin):
	list_display = ("meeting", "company", "status", "requested_by", "requested_at", "completed_at")
	list_filter = ("meeting", "company", "status")
	search_fields = ("meeting__title", "company__name", "requested_by__email")

@admin.register(MeetingParticipant)
class MeetingParticipantAdmin(admin.ModelAdmin):
	list_display = ("meeting", "user")
	search_fields = ("meeting__title", "user__email") 
