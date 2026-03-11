from django.db.models.signals import post_save
from django.dispatch import receiver
from billing.models import Invoice, InvoiceLineItem
from services.models import ServiceRequest
from scheduling.models import Meeting
from billing.services import bill_meeting

@receiver(post_save, sender=Meeting)
def create_meeting_invoice_on_complement(sender, instance: Meeting, created: bool, **kwargs):
    if instance.status != "FINISHED":
        return 

    if Meeting.objects.filter(meeting_request_id=instance.id).exists():
        return
    
    bill_meeting(instance)

@receiver(post_save, sender=ServiceRequest)
def create_service_invoice_on_completion(sender, instance: ServiceRequest, created: bool, **kwargs):
    if instance.status != "COMPLETED":
        return

    # avoid duplicates
    if Invoice.objects.filter(service_request_id=instance.id).exists():
        return

    service = instance.service
    invoice = Invoice.objects.create(
        company=instance.company,
        client=instance.requested_by,
        status=Invoice.Status.DRAFT,
        service_request_id=instance.id,
    )

    InvoiceLineItem.objects.create(
        invoice=invoice,
        description=f"Service: {service.name}",
        qty=1,
        unit_price_cents=service.base_price_cents,
    )

    invoice.recalc_totals()
    invoice.save()