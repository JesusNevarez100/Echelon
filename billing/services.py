from billing.models import Invoice, InvoiceLineItem
from accounts.models import Membership
from scheduling.models import Meeting, MeetingRequest, compute_meeting_charge_cents

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

    client = meeting.requested_by or _first_client_participant(meeting)
    if client is None:
        raise ValueError("Billable meeting must have a client requester or participant.")

    amount_cents = compute_meeting_charge_cents(meeting)
    if amount_cents <= 0:
        raise ValueError("Billable meeting has no charge (check rate/type).")

    meeting_date = meeting.start_at.strftime("%Y-%m-%d") if meeting.start_at else "unscheduled"
    message = f"Meeting with {meeting.company.name} ({meeting_date})"
    invoice = check_invoice(meeting, client, message, amount_cents)
    invoice.meeting_requested_id = meeting.id
    invoice.save(update_fields=["meeting_requested_id"])

    return invoice

def bill_meeting_request(meeting_request: MeetingRequest) -> Invoice:
    meeting = meeting_request.meeting
    if not meeting.is_billable:
        raise ValueError("Meeting is not billable.")
    if meeting_request.requested_by_id is None:
        raise ValueError("Billable meeting request must have a client.")
    amount_cents = compute_meeting_charge_cents(meeting)
    if amount_cents <= 0:
        raise ValueError("Billable meeting has no charge (check rate/type).")

    message = f"Meeting with {meeting.company.name} ({meeting.start_at:%Y-%m-%d})"
    invoice = check_invoice(meeting_request, meeting_request.requested_by, message, amount_cents)
    invoice.meeting_requested_id = meeting_request.id
    invoice.save(update_fields=["meeting_requested_id"])

    return invoice

def _first_client_participant(meeting: Meeting):
    participant = meeting.participants.filter(
        user__memberships__company=meeting.company,
        user__memberships__role=Membership.Role.CLIENT,
    ).select_related("user").first()
    return participant.user if participant else None
