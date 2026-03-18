from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.utils import timezone

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


class DisplayInvoiceDetailView(View):
    template_name = "billing/InvoiceDetail.html"
    company_roles = {Membership.Role.MANAGER, Membership.Role.STAFF, Membership.Role.ADMIN}
    can_remove = (Membership.Role.MANAGER, Membership.Role.ADMIN)
    client_roles = {Membership.Role.CLIENT}

    def _is_company_member(self, membership):
        return membership.role in self.company_roles
    
    def _is_client_member(self, membership):
        return membership.role in self.client_roles
    
    def _can_remove_invoice(self, membership):
        return membership.role in self.can_remove
    
    def _get_invoice(self, request, membership):
        invoice_id = self.kwargs.get("invoice_id")
        visible_invoices = _visible_invoices_for_membership(request.user, membership)
        return get_object_or_404(visible_invoices, id=invoice_id)
    
    
    def get(self, request, *args, **kwargs):
        membership = get_primary_membership(request.user)
        if not membership:
            return HttpResponseForbidden("No company membership")
    
        invoice_id = self.kwargs.get("invoice_id")
        visible_invoices = _visible_invoices_for_membership(request.user, membership)

        invoice = get_object_or_404(visible_invoices, id=invoice_id)

        return render(request ,self.template_name, {
            "invoice": invoice,
            "line_items": invoice.line_items.all(),
            "membership": membership,
            "is_company": self._is_company_member(membership),
            "is_client": self._is_client_member(membership),
            "can_remove_invoice": self._can_remove_invoice(membership)
        }
        )

    def post(self, request, *args, **kwargs):
        membership = get_primary_membership(request.user)
        if not membership:
            return HttpResponseForbidden("No company membership")
        
        # invoice = self._get_invoice(membership)
        invoice_id = kwargs.get("invoice_id")
        visible_invoices = _visible_invoices_for_membership(request.user, membership)
        invoice = get_object_or_404(visible_invoices, id=invoice_id)

        action = request.POST.get("action")
        

        # Send, Edit, Delete, and pay
        if action=="send_invoice" and self._is_company_member(membership):
            invoice.status = Invoice.Status.SENT
            invoice.save()
            messages.success(request, "Invoice sent successfully.")
            return redirect("billing:invoice_detail", invoice_id=invoice_id)            

        elif action=="remove_invoice" and self._can_remove_invoice(membership):
            invoice.delete()
            messages.success(request, "Invoice deleted successfully. ")
            return redirect("billing:display_invoices")

        elif action=="pay_invoice" and self._is_client_member(membership):
            invoice.status = Invoice.Status.PAID
            invoice.save()
            messages.success(request, "Invoice has been paid successfully.")
            # Collect Payment information
            return redirect("billing:display_invoices")
        
        elif action=="return":
            return redirect("billing:display_invoices")


        return redirect("billing:invoice_detail", invoice.id)
    
DisplayInvoiceView = DisplayInvoiceDetailView.as_view()