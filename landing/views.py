from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.timezone import now
from django.http import HttpResponseForbidden
from django.db import models
from django.urls import reverse

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
    membership = get_primary_membership(request.user)
    if membership is None:
        return HttpResponseForbidden("No company membership recognized.")

    company = membership.company
    is_client = membership.role == Membership.Role.CLIENT
    today = now()

    visible_meetings = Meeting.objects.filter(company=company)
    if is_client:
        visible_meetings = visible_meetings.filter(
            models.Q(requested_by=request.user) |
            models.Q(participants__user=request.user)
        ).distinct()
    else:
        visible_meetings = visible_meetings.filter(
            models.Q(status=Meeting.Status.REQUESTED) |
            models.Q(organizer=request.user) |
            models.Q(participants__user=request.user)
        ).distinct()

    upcoming_meetings = (
        visible_meetings
        .filter(status=Meeting.Status.ACTIVE, start_at__gte=today)
        .order_by("start_at")[:4]
    )
    pending_meetings = visible_meetings.filter(status=Meeting.Status.REQUESTED).order_by("-created_at")[:4]

    tasks = (
        Task.objects
        .filter(company=company)
        .exclude(status__in=[Task.Status.DONE, Task.Status.CANCELLED])
    )
    if is_client:
        tasks = tasks.filter(assigned_to=request.user)
    else:
        tasks = tasks.filter(models.Q(assigned_to=request.user) | models.Q(created_by=request.user))
    tasks = tasks.order_by("due_at", "-created_at")[:4]

    if is_client:
        service_requests_qs = ServiceRequest.objects.filter(company=company, requested_by=request.user)
        invoices_qs = Invoice.objects.filter(company=company, client=request.user)
    else:
        service_requests_qs = ServiceRequest.objects.filter(company=company)
        invoices_qs = Invoice.objects.filter(company=company)

    recent_service_requests = service_requests_qs.select_related("service", "requested_by").order_by("-requested_at")[:4]
    recent_invoices = invoices_qs.select_related("client").order_by("-issued_at")[:4]

    open_tasks_count = Task.objects.filter(company=company).exclude(status__in=[Task.Status.DONE, Task.Status.CANCELLED])
    if is_client:
        open_tasks_count = open_tasks_count.filter(assigned_to=request.user)
    else:
        open_tasks_count = open_tasks_count.filter(models.Q(assigned_to=request.user) | models.Q(created_by=request.user))

    stats = [
        {"label": "Open Tasks", "value": open_tasks_count.count()},
        {"label": "Pending Meetings", "value": visible_meetings.filter(status=Meeting.Status.REQUESTED).count()},
        {"label": "Service Requests", "value": service_requests_qs.exclude(status=ServiceRequest.Status.COMPLETED).count()},
        {"label": "Draft Invoices", "value": invoices_qs.filter(status=Invoice.Status.DRAFT).count()},
    ]

    modules = [
        {"name": "CRM", "icon": "bi-clipboard-check", "desc": "Contacts, tasks, and follow-through.", "url": reverse("crm:index")},
        {"name": "Services", "icon": "bi-bag-check", "desc": "Catalog items and client requests.", "url": reverse("services:services_home")},
        {"name": "Scheduling", "icon": "bi-calendar2-week", "desc": "Private meetings and requests.", "url": reverse("scheduling:index")},
        {"name": "Billing", "icon": "bi-receipt-cutoff", "desc": "Invoices, totals, and line items.", "url": reverse("billing:display_invoices")},
    ]

    if is_client:
        quick_actions = [
            {"label": "Request Meeting", "url": reverse("scheduling:create_meeting"), "icon": "bi-calendar-plus"},
            {"label": "Request Service", "url": reverse("services:services_home"), "icon": "bi-bag-plus"},
            {"label": "View Tasks", "url": reverse("crm:index"), "icon": "bi-check2-square"},
            {"label": "View Invoices", "url": reverse("billing:display_invoices"), "icon": "bi-receipt"},
        ]
    else:
        quick_actions = [
            {"label": "Create Contact", "url": reverse("crm:create_contact"), "icon": "bi-person-lines-fill"},
            {"label": "Create Task", "url": reverse("crm:create_task"), "icon": "bi-check2-square"},
            {"label": "Create Meeting", "url": reverse("scheduling:create_meeting"), "icon": "bi-calendar-plus"},
            {"label": "Services", "url": reverse("services:services_home"), "icon": "bi-bag-plus"},
        ]

    invoice_cards = [
        {
            "id": invoice.id,
            "status": invoice.status,
            "total": f"{invoice.total_cents / 100:.2f}",
        }
        for invoice in recent_invoices
    ]

    return render(request, "landing/dashboard.html", {
        "membership": membership,
        "company": company,
        "stats": stats,
        "modules": modules,
        "quick_actions": quick_actions,
        "upcoming_meetings": upcoming_meetings,
        "pending_meetings": pending_meetings,
        "tasks": tasks,
        "recent_service_requests": recent_service_requests,
        "recent_invoices": invoice_cards,
        "is_client": is_client,
        "can_manage_users": not is_client,
    })

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
    reverse("services:services_home")
    reverse("services:create_service")


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
            "actions": [{"label": "Request a Service", "url": reverse("services_home")},]

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
    {"label": "Request a Service", "url": reverse("services:services_home")},
    {"label": "Add Service", "url": reverse("services:create_service")},
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
