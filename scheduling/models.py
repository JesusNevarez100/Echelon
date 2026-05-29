from django.db import models
from django.utils import timezone
from accounts.models import CompanyAccount, User
import math

# Create your models here.
class Meeting(models.Model):
	class BillingType(models.TextChoices):
		HOURLY = "HOURLY", "Hourly"
		FLAT = "FLAT", "Flat fee"
	
	class Status(models.TextChoices):
		REQUESTED = "REQUESTED", "Requested"
		ACTIVE = "ACTIVE", "Active",
		FINISHED = "FINISHED","Finished"
		CANCELED = "CANCELED", "Canceled"

	status = models.CharField(
		max_length=10,
		choices=Status.choices,
		default=Status.ACTIVE
	)

	company = models.ForeignKey(CompanyAccount, on_delete=models.CASCADE, related_name="meeting")
	organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="meetings_organizer")
	requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="meetings_requested")

	title = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	location = models.CharField(max_length=255, blank=True, null=True)
	start_at = models.DateTimeField(blank=True, null=True)
	end_at = models.DateTimeField(blank=True, null=True)
	notes = models.TextField(blank=True, null=True)
	created_at = models.DateTimeField(default=timezone.now)

	is_billable = models.BooleanField(default=False)
	billing_type = models.CharField(
		max_length=10,
		choices=BillingType.choices,
		default=BillingType.HOURLY
	)

	bill_rate_cents = models.BigIntegerField(blank=True, null=True)
	billable_minutes_override = models.PositiveIntegerField(blank=True, null=True)

	def duration_minutes(self) -> int:
		if self.start_at is None or self.end_at is None:
			return 0
		delta = self.end_at - self.start_at
		return max(0, int(delta.total_seconds() // 60))
	
	def billable_minutes(self) -> int:
		return int(self.billable_minutes_override) if self.billable_minutes_override is not None else self.duration_minutes()

	def __str__(self) -> str:
		return f"{self.title} ({self.company.name})"

class MeetingRequest(models.Model):
	class Status(models.TextChoices):
		REQUESTED = "REQUESTED", "Requested"
		ACCEPTED = "ACCEPTED", "Accepted"
		FINISHED = "FINISHED", "Finished"
		CANCELED = "CANCELED", "Canceled"

	company = models.ForeignKey(CompanyAccount, on_delete=models.CASCADE, related_name="meeting_requests")
	meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="requests")
	requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="meeting_requests")
	status = models.CharField(max_length=16, choices=Status.choices, default=Status.REQUESTED)

	requested_at = models.DateTimeField(default=timezone.now)
	completed_at = models.DateTimeField(blank=True, null=True)
	notes = models.TextField(blank=True, null=True)

	def __str__(self) -> str:
		return f"{self.meeting.title} -> {self.company.name} [{self.status}]"

def compute_meeting_charge_cents(meeting: Meeting) -> int:
    if not meeting.is_billable or meeting.bill_rate_cents is None:
        return 0

    if meeting.billing_type == Meeting.BillingType.FLAT:
        return int(meeting.bill_rate_cents)

    # HOURLY: round up to next 15 minutes (common billing practice)
    minutes = meeting.billable_minutes()
    minutes_rounded = int(math.ceil(minutes / 15) * 15)
    hours = minutes_rounded / 60.0
    return int(round(hours * int(meeting.bill_rate_cents)))
	
class MeetingParticipant(models.Model):
	meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE,related_name="participants")
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meeting_participant")	

	class Meta:
		unique_together = ("meeting", "user")

	def __str__(self) -> str:
		return f"{self.user.email} in {self.meeting.title}"
