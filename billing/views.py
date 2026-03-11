from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render

from accounts.models import Membership
from accounts.services import get_primary_membership
from .models import Invoice


def index(request):
    return render(request, "billing/index.html")


def _visible_invoices_for_membership(user, membership):
    base_qs = (
        Invoice.objects.select_related("company", "client")
        .prefetch_related("line_items")
        .filter(company=membership.company)
        .order_by("-issued_at", "-id")
    )

    if membership.role == Membership.Role.CLIENT:
        return base_qs.filter(
            client=user,
            status__in=[Invoice.Status.SENT, Invoice.Status.PAID],
        )

    return base_qs.filter(
        status__in=[
            Invoice.Status.SENT,
            Invoice.Status.PAID,
            Invoice.Status.DRAFT,
            Invoice.Status.VOIDED,
        ]
    )


@login_required
def displayInvoice(request):
    membership = get_primary_membership(request.user)
    if membership is None:
        return HttpResponseForbidden("No company membership recognized.")

    invoices = _visible_invoices_for_membership(request.user, membership)

    context = {
        "invoices": invoices,
        "membership": membership,
        "is_client": membership.role == Membership.Role.CLIENT,
    }
    return render(request, "billing/displayInvoices.html", context)


@login_required
def displayInvoiceDetail(request, invoice_id):
    membership = get_primary_membership(request.user)
    if membership is None:
        return HttpResponseForbidden("No company membership recognized.")

    visible_invoices = _visible_invoices_for_membership(request.user, membership)
    invoice = get_object_or_404(visible_invoices, id=invoice_id)

    context = {
        "invoice": invoice,
        "line_items": invoice.line_items.all(),
        "membership": membership,
        "is_client": membership.role == Membership.Role.CLIENT,
    }
    return render(request, "billing/InvoiceDetail.html", context)
