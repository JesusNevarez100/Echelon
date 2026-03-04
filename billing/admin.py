from django.contrib import admin
from .models import Invoice, InvoiceLineItem

# Register your models here.

class InvoiceLineItemInLine(admin.TabularInline):
	model = InvoiceLineItem
	extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
	list_display = ("id", "company", "client", "status", "total_cents", "issued_at", "due_at", "paid_at")
	list_filter = ("status", "company")
	search_fields = ("company__name", "client__email")
	inlines = [InvoiceLineItemInLine]
