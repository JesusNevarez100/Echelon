from django.utils import timezone
from billing.models import Invoice, InvoiceLineItem
from scheduling.models import Meeting, compute_meeting_charge_cents

def bill_meeting(meeting: Meeting) -> Invoice:
    if not meeting.is_billable:
        raise ValueError("Meeting is not billable.")
    if meeting.invoice_id is not None:
        return meeting.invoice  # already billed / linked

    if meeting.client_id is None:
        raise ValueError("Billable meeting must have a client.")

    amount_cents = compute_meeting_charge_cents(meeting)
    if amount_cents <= 0:
        raise ValueError("Billable meeting has no charge (check rate/type).")

    invoice = Invoice.objects.create(
        company=meeting.company,
        client=meeting.client,
        status=Invoice.Status.DRAFT,
    )

    InvoiceLineItem.objects.create(
        invoice=invoice,
        description=f"Meeting: {meeting.title} ({meeting.start_at:%Y-%m-%d})",
        qty=1,
        unit_price_cents=amount_cents,
    )

    invoice.recalc_totals()
    invoice.save()

    meeting.invoice = invoice
    meeting.billed_at = timezone.now()
    meeting.save(update_fields=["invoice", "billed_at"])

    return invoice