from django.db import models
from django.utils import timezone
from accounts.models import CompanyAccount, User

# Create your models here.

class Contact(models.Model):
	class ContactType(models.TextChoices):
		CUSTOMER =  "CUSTOMER", "Customer"
		LEAD = "LEAD", "Lead"
		COMPANY = "COMPANY", "Company"
		OTHER = "OTHER", "Other"
	
	company = models.ForeignKey(CompanyAccount, on_delete=models.CASCADE, related_name="contacts")
	type = models.CharField(max_length=16, choices=ContactType.choices, default=ContactType.CUSTOMER)

	name = models.CharField(max_length=255)
	email = models.EmailField(blank=True, null=True)
	phone = models.CharField(max_length=32, blank=True, null=True)
	notes = models.TextField(blank=True, null=True)

	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"{self.name} ({self.company.name})"
	
class Task(models.Model):
	class Status(models.TextChoices):
		OPEN = "OPEN", "Open"
		IN_PROGRESS = "IN_PROGRESS", "In Progress"
		DONE = "DONE", "Done"
		CANCELLED = "CANCELLED", "Cancelled"

	company = models.ForeignKey(CompanyAccount, on_delete=models.CASCADE, related_name="tasks")
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="tasks_created")
	assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks_assigned")

	contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")

	title = models.CharField(max_length=255)
	description = models.TextField(blank=True, null=True)
	status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)

	created_at = models.DateTimeField(default=timezone.now)
	due_at = models.DateTimeField(blank=True)

	def __str__(self):
		return f"{self.title} [{self.status}]"