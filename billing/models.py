from django.db import models
from django.utils import timezone
from accounts.models import CompanyAccount, User

# Create your models here.
class Invoice(models.Model):
	class Status(models.TextChoices):
		DRAFT = "DRAFT", "Draft"
		SENT = "SENT", "Sent"
		PAID = "PAID", "Paid"
		VOIDED = "VOIDED", "Voided"

	company = models.ForeignKey(CompanyAccount, on_delete=models.CASCADE, related_name="invoices")
	client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="invoices")
	
	status = models.CharField(
		max_length=10,
		choices=Status.choices,
		default=Status.DRAFT,
	)

	issued_at = models.DateTimeField(default=timezone.now)
	due_at = models.DateTimeField(blank=True, null=True)
	paid_at = models.DateTimeField(blank=True, null=True)

	subtotal_cents = models.BigIntegerField(default=0)
	tax_cents = models.BigIntegerField(default=0)
	total_cents = models.BigIntegerField(default=0)

	service_requested_id = models.BigIntegerField(blank=True, null=True)

	def __str__(self) -> str:
		return f"Invoice #{self.id} ({self.company.name}) - {self.status}"
	
	def recalc_totals(self) -> None:
		subtotal = sum(li.line_total_cents for li in self.line_items.all())
		self.subtotal_cents = subtotal
		self.total_cents = subtotal + (self.tax_cents or 0)

class InvoiceLineItem(models.Model):
	invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="line_items")
	description = models.CharField(max_length=255)
	qty = models.PositiveIntegerField(default=1)
	unit_price_cents = models.BigIntegerField(default=0)
	line_total_cents = models.BigIntegerField(default=0)

	def save(self, *args, **kwargs):
		self.line_total_cents = int(self.qty) * int(self.unit_price_cents)
		super().save(*args, **kwargs)

	def __str__(self) -> str:
		return f"{self.description} x{self.qty}"
	
