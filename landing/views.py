from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.timezone import now
from django.http import HttpResponseForbidden
from django.db import models

from accounts.models import Membership
from accounts.services import get_primary_membership
from services.models import Service, ServiceRequest
from scheduling.models import Meeting
from crm.models import Task, Contact
from billing.models import Invoice


def landing(request):
    return render(request, "landing/landing.html")

#This code manages the functionality of the blocks
@login_required
def dashboard(request):
    cards = [
        get_crm_summary(request),
        get_services_summary(request),
        get_scheduling_summary(request),
        get_billing_summary(request),
    ]

    return render(request, "landing/dashboard.html", {"cards": cards})


#-------------
#CRM display

@login_required
def get_crm_summary(request):
    membership = get_primary_membership(request.user)
    if membership is None:
        return HttpResponseForbidden("No company membership recognized.")

    company = membership.company
    is_client = membership.role == Membership.Role.CLIENT

    # users can only see their own tasks, lmk if this needs to be changed
    user_tasks_qs = (
        Task.objects.filter(company=company, assigned_to=request.user)
        .order_by("due_at", "-created_at")[:5]
    )
    user_tasks = [
        f"{task.title} (due {task.due_at.date() if task.due_at else 'No due date'})"
        for task in user_tasks_qs
    ]

    #block displays
    #client side
    if is_client:
        return {
            "name": "CRM Overview",
            "desc": "Your company and your tasks",
            "url": "/crm/",
            "sections": [
                {"title": "Your Company", "items": [company.name]},
                {"title": "Your Tasks", "items": user_tasks},
            ],
            "actions": [
                {"label": "View CRM", "url": "/crm/"},
            ],
        }

    #company side
    contacts_qs = Contact.objects.filter(company=company).order_by("name")[:10]
    contacts = [c.name for c in contacts_qs]

    return {
        "name": "CRM Overview",
        "desc": "Company contacts and your tasks",
        "url": "/crm/",
        "sections": [
            {"title": "Contacts", "items": contacts},
            {"title": "Your Tasks", "items": user_tasks},
        ],
        "actions": [
            {"label": "View CRM", "url": "/crm/"},
            {"label": "Add Contact", "url": "/crm/add-contact/"},
        ],
    }


#-------------
#Service Display
def get_services_summary(request):
    membership = get_primary_membership(request.user)
    if membership is None:
        return HttpResponseForbidden("No company membership recognized.")

    is_client = membership.role == Membership.Role.CLIENT
    company = membership.company

    # list of available services
    available_services = list(
        Service.objects.filter(company=company, active=True)
                       .values_list("name", flat=True)
    )

    # Recent requests (company side)
    recent_requests_qs = (
        ServiceRequest.objects.filter(company=company)
        .select_related("service", "requested_by")
        .order_by("-requested_at")[:5]
    )
    recent_requests = [
        f"{req.company.name} requested: {req.service.name}"
        for req in recent_requests_qs
    ]

    # Client specific requests
    client_requests_qs = (
        ServiceRequest.objects.filter(
            company=company,
            requested_by=membership.user
        )
        .select_related("service")
        .order_by("-requested_at")[:5]
    )
    client_recent_requests = [
        f"{membership.company.name} requested: {req.service.name}"
        for req in client_requests_qs
    ]

    #block displays
    #client side
    if is_client:
        return {
            "name": "Services",
            "desc": "Available services and your recent requests",
            "url": "/services/",
            "sections": [
                {"title": "Available Services", "items": available_services},
                {"title": "Your Recent Requests", "items": client_recent_requests},
            ],
            "actions": [{"label": "Request a Service", "url": "/services/request/"}],
        }

    return {
        "name": "Services",
        "desc": "Available services and client requests",
        "url": "/services/",
        "sections": [
            {"title": "Available Services", "items": available_services},
            {"title": "Recent Client Requests", "items": recent_requests},
        ],
        "actions": [
            {"label": "Request a Service", "url": "/services/request/"},
            {"label": "Add Service", "url": "/services/add/"},
        ],
    }



#-------------
#schedule display
def get_scheduling_summary(request):
    membership = get_primary_membership(request.user)
    if membership is None:
        return HttpResponseForbidden("No company membership recognized.")

    company = membership.company
    user = membership.user
    is_client = membership.role == membership.Role.CLIENT

    # upcoming meeting display
    MAX_FEATURED = 3

    upcoming_qs = (
	    Meeting.objects.filter(
	        company=company,
	        status=Meeting.Status.ACTIVE,
	        start_at__gte=now()
	    )
	    .order_by("start_at")
	)

    if is_client:
        upcoming_qs = upcoming_qs.filter(
            models.Q(client=user) |
            models.Q(organizer=user) |
            models.Q(participants__user=user)
        ).distinct()
         
    upcoming_list = list(upcoming_qs[:MAX_FEATURED])
    remaining_count = upcoming_qs.count() - len(upcoming_list)

    if upcoming_list:
        upcoming_items = [
            f"{m.title} — {m.start_at.strftime('%b %d, %Y at %I:%M %p')}"
            for m in upcoming_list
	    ]
    else:
        upcoming_items = ["No upcoming meetings"]

    if remaining_count > 0:
        upcoming_items.append(f"{remaining_count} more upcoming meeting(s)")


    #pending meetings (wip, not sure how to display yet)
    pending_qs = Meeting.objects.filter(
        company=company,
        status=Meeting.Status.ACTIVE,
        client__isnull=True,
        start_at__gte=now()
    )

    pending_count = pending_qs.count()

    pending_str = (
        f"{pending_count} pending meeting request"
        if pending_count == 1
        else f"{pending_count} pending meeting requests"
    )

    #block displays, same for both accounts
    return {
    "name": "Scheduling",
    "desc": "Make and manage meetings",
    "url": "/scheduling/",
    "sections": [
        {
            "title": "Upcoming",
            "items": upcoming_items + [pending_str],
        }
    ],
    "actions": [
        {"label": "View Calendar", "url": "/scheduling/"},
        {"label": "New Reservation", "url": "/scheduling/new/"},
    ],
}


#-------------
#Invoice display
def get_billing_summary(request):
    membership = get_primary_membership(request.user)
    if membership is None:
        return HttpResponseForbidden("No company membership recognized.")

    company = membership.company
    is_client = membership.role == Membership.Role.CLIENT

    # client side
    if is_client:
        invoices_qs = (
            Invoice.objects.filter(client=request.user)
            .order_by("-issued_at")[:5]
        )

        client_invoices = [
            f"Invoice #{inv.id} — ${inv.total_cents / 100:.2f} "
            f"(Due {inv.due_at.date() if inv.due_at else 'No due date'}) — {inv.status}"
            for inv in invoices_qs
        ]

        return {
            "name": "Billing & Invoices",
            "desc": "Your invoices and payment deadlines",
            "url": "/billing/",
            "sections": [
                {"title": "Recent Invoices", "items": client_invoices},
            ],
            "actions": [
                {"label": "View All Invoices", "url": "/billing/"},
            ],
        }

    # company side
    invoices_qs = (
        Invoice.objects.filter(company=company)
        .select_related("client")
        .order_by("-issued_at")[:5]
    )

    recent_invoices = [
        f"{inv.client.username if inv.client else 'Unknown Client'} — "
        f"${inv.total_cents / 100:.2f} "
        f"(Due {inv.due_at.date() if inv.due_at else 'No due date'}) — {inv.status}"
        for inv in invoices_qs
    ]

    return {
        "name": "Billing & Invoices",
        "desc": "Recent invoices and payment deadlines",
        "url": "/billing/",
        "sections": [
            {"title": "Recent Invoices", "items": recent_invoices},
        ],
        "actions": [
            {"label": "View All Invoices", "url": "/billing/"},
            {"label": "Create Invoice", "url": "/billing/create/"},
            {"label": "Manage Invoices", "url": "/billing/manage/"},
        ],
    }
