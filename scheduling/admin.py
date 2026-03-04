from django.contrib import admin
from .models import Meeting, MeetingParticipant

# Register your models here.
@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
	list_display = ("title", "company", "organizer", "start_at", "end_at", "location", "is_billable", "billing_type", "bill_rate_cents", "invoice")
	list_filter = ("company", "is_billable", "billing_type")
	search_field = ("title", "company__name", "organizer__email")

@admin.register(MeetingParticipant)
class Meeting(admin.ModelAdmin):
	list_display = ("meeting", "user")
	search_fields = ("meeting__title", "user__email") 
