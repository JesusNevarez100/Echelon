from billing.models import Invoice, InvoiceLineItem
from scheduling.models import Meeting, compute_meeting_charge_cents

def check_invoice(instance, client, message, price) -> Invoice:
    drafted_invoice = Invoice.objects.filter(
        company=instance.company,
        client=client,
        status=Invoice.Status.DRAFT,
    ).first()
    if drafted_invoice is None:
        invoice = Invoice.objects.create(
            company=instance.company,
            client=client,
            status=Invoice.Status.DRAFT,
            service_requested_id=instance.id,
        )
    else:
        invoice = drafted_invoice
    

    InvoiceLineItem.objects.create(
        invoice=invoice,
        description=message,
        qty=1,
        unit_price_cents=price,
    )

    invoice.recalc_totals()
    invoice.save(update_fields=["subtotal_cents", "total_cents"])

    return invoice

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

    message = f"Meeting with {meeting.company.name} ({meeting.start_at:%Y-%m-%d})"
    client = meeting.client
    invoice = check_invoice(meeting, client, message, amount_cents)

    return invoice
