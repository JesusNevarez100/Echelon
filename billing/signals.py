from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from billing.models import Invoice, InvoiceLineItem
from services.models import ServiceRequest
from scheduling.models import Meeting, MeetingRequest
from billing.services import bill_meeting, bill_meeting_request, check_invoice

@receiver(post_save, sender=Meeting)
def create_meeting_invoice_on_completion(sender, instance: Meeting, created: bool, **kwargs):
    if instance.status != Meeting.Status.FINISHED:
        return

    if Invoice.objects.filter(meeting_requested_id=instance.id).exists():
        return

    bill_meeting(instance)

@receiver(post_save, sender=MeetingRequest)
def create_legacy_meeting_request_invoice_on_completion(sender, instance: MeetingRequest, created: bool, **kwargs):
    if instance.status != MeetingRequest.Status.FINISHED:
        return 

    # avoid duplicates
    if Invoice.objects.filter(meeting_requested_id=instance.id).exists():
        return
    
    bill_meeting_request(instance)

@receiver(post_save, sender=ServiceRequest)
def create_service_invoice_on_completion(sender, instance: ServiceRequest, created: bool, **kwargs):
    if instance.status != "COMPLETED":
        return

    if Invoice.objects.filter(service_requested_id=instance.id).exists():
        return

    service=instance.service
    message=f"Service: {service.name}"
    check_invoice(instance, instance.requested_by, message, service.base_price)

@receiver(post_save, sender=InvoiceLineItem)
def sync_invoice_totals_on_lineitem_save(sender, instance: InvoiceLineItem, **kwargs):
    invoice = instance.invoice
    invoice.recalc_totals()
    invoice.save(update_fields=["subtotal_cents", "total_cents"])

@receiver(post_delete, sender=InvoiceLineItem)
def sync_invoice_totals_on_lineitem_delete(sender, instance: InvoiceLineItem, **kwargs):
    invoice = instance.invoice
    invoice.recalc_totals()
    invoice.save(update_fields=["subtotal_cents", "total_cents"])
