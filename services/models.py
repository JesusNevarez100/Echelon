from django.db import models
from django.utils import timezone
from accounts.models import CompanyAccount, User

# Create your models here.
class Service(models.Model):
	company = models.ForeignKey(CompanyAccount, on_delete=models.CASCADE, related_name="services")
	name = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	active = models.BooleanField(default=True)
	base_price_cents = models.BigIntegerField(default=0)

	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"{self.name} ({self.company.name})"
	
class ServiceRequested(models.Model):
	class Status(models.TextChoices):
		REQUESTED = "REQUESTED", "Requested"
		ACCEPTED = "ACCEPTED", "Accepted"
		IN_PROGRESS = "IN_PROGRESS", "In Progress"
		COMPLETED = "COMPLETED", "Completed"
		CANCELLED = "CANCELLED", "Cancelled"

	company = models.ForeignKey(CompanyAccount, on_delete=models.CASCADE, related_name="service_requested")
	service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="requests")

	requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="service_requests")
	status = models.CharField(max_length=16, choices=Status.choices, default=Status.REQUESTED) 

	requested_at = models.DateTimeField(default=timezone.now)
	completed_at = models.DateTimeField(blank=True, null=True)

	notes = models.TextField(blank=True, null=True)

	def __str__(self):
		return f"{self.service.name} -> {self.company.name} [{self.status}]"

