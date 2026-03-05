from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

import uuid

# Create your models here.
class User(AbstractUser):
	"""
	Custom user model. Keep username for simplicity initially, 
	switch to e-mail log in later
	"""
	class Status(models.TextChoices):
		ACTIVE = "ACTIVE", "Active"
		SUSPENDED = "SUSPENDED", "Suspended"
		DELETED = "DELETED", "Deleted"

	status = models.CharField(
		max_length=16,
		choices=Status.choices,
		default=Status.ACTIVE
	)

	email = models.EmailField(unique=True)

	must_change_password = models.BooleanField(default=False)

class CompanyAccount(models.Model):
	company_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=255, unique=True)
	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self) -> str:
		return self.name
	
class Membership(models.Model):
	class Role(models.TextChoices):
		ADMIN = "ADMIN", "Admin"
		STAFF = "STAFF", "Staff"
		MANAGER = "MANAGER", "Manager"
		CLIENT = "CLIENT", "Client"
	
	membership_id = models.BigAutoField(primary_key=True)

	user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name="memberships",
	)
	company = models.ForeignKey(
		CompanyAccount,
		on_delete=models.CASCADE,
		related_name="memberships"
	)
	role = models.CharField(
		max_length=10,
		choices=Role.choices,
		default=Role.CLIENT
	)

	created_at = models.DateTimeField(default=timezone.now)

	class Meta:
		unique_together = ("user", "company")

	def __str__(self) -> str:
		return f"{self.user.username} @ {self.company.name} ({self.role})"