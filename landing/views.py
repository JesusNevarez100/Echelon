from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.timezone import now
from django.http import HttpResponseForbidden
from django.db import models

from accounts.models import Membership
from accounts.services import get_primary_membership
from services.models import Service, ServiceRequest
from scheduling.models import Meeting


def landing(request):
    return render(request, "landing/landing.html")

#Manages the functionality of the blocks
@login_required
def dashboard(request):
    cards = [
        get_crm_summary(request),
        get_services_summary(request),
        get_scheduling_summary(request),
        get_billing_summary(request),
    ]

    return render(request, "landing/dashboard.html", {"cards": cards})


#THIS IS FOR TESTING CAUSE I WASN'T SURE HOW TO CREATE THE ACCOUNTS! 
#If you wanna test with this, embed the link with dashboard/?as=client or dashboard/?as=company

#-------------
#CRM display

@login_required
def get_crm_summary(request):
    membership = get_primary_membership(request.user)
    if membership is None:
        return HttpResponseForbidden("No company membership recognized.")

    is_client = membership.role == Membership.Role.CLIENT

    # Test data (still static for now)
    test_company_clients = ["Parallel Cloak", "Black Sol", "NMT co.", "Umbrella Corp"]
    test_client_tasks = [
        "Follow up with Parallel Cloak (due Mar 10)",
        "Prepare proposal for Black Sol (due Mar 14)",
    ]
    test_company_tasks = [
        "Review quarterly CRM metrics",
        "Assign leads to sales team",
    ]

    # CLIENT SIDE
    if is_client:
        return {
            "name": "CRM Overview",
            "desc": "Your company and your tasks",
            "url": "/crm/",
            "sections": [
                {"title": "Your Company", "items": [membership.company.name]},
                {"title": "Your Tasks", "items": test_client_tasks},
            ],
            "actions": [
                {"label": "View CRM", "url": "/crm/"},
            ],
        }

    # COMPANY SIDE
    return {
        "name": "CRM Overview",
        "desc": "Company clients and tasks",
        "url": "/crm/",
        "sections": [
            {"title": "Clients", "items": test_company_clients},
            {"title": "Company Tasks", "items": test_company_tasks},
        ],
        "actions": [
            {"label": "View CRM", "url": "/crm/"},
            {"label": "Add Client", "url": "/crm/add-client/"},
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

    # Available services
    available_services = list(
        Service.objects.filter(company=company, active=True)
                       .values_list("name", flat=True)
    )

    # Recent requests (company view)
    recent_requests_qs = (
        ServiceRequest.objects.filter(company=company)
        .select_related("service", "requested_by")
        .order_by("-requested_at")[:5]
    )
    recent_requests = [
        f"{req.company.name} requested: {req.service.name}"
        for req in recent_requests_qs
    ]

    # Client-specific requests
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

    # Build summary
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

    # UPCOMING MEETINGS
    MAX_FEATURED = 3

    # UPCOMING MEETINGS
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

    # Add “+ X more upcoming meetings”
    if remaining_count > 0:
        upcoming_items.append(f"{remaining_count} more upcoming meeting(s)")


    # PENDING MEETINGS (optional)
    # If you want to treat "pending" as meetings without a client assigned:
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

    # -----------------------------
    # BUILD CARD
    # -----------------------------
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

    is_client = membership.role == Membership.Role.CLIENT

    # Static test data
    recent_invoices = [
        {"company": "Parallel Cloak", "amount": "$250", "due": "Mar 20"},
        {"company": "Black Sol", "amount": "$480", "due": "Mar 22"},
        {"company": "NMT co.", "amount": "$150", "due": "Mar 25"},
    ]

    # Client-specific invoices
    client_invoices = [
        f"{membership.company.name} — $250 (Due Mar 20)"
    ]

    # CLIENT SIDE
    if is_client:
        return {
            "name": "Billing & Invoices",
            "desc": "Your invoices and payment deadlines",
            "url": "/billing/",
            "sections": [
                {
                    "title": "Recent Invoices",
                    "items": client_invoices,
                }
            ],
            "actions": [
                {"label": "View All Invoices", "url": "/billing/"},
            ],
        }

    # COMPANY SIDE
    return {
        "name": "Billing & Invoices",
        "desc": "Recent invoices and payment deadlines",
        "url": "/billing/",
        "sections": [
            {
                "title": "Recent Invoices",
                "items": [
                    f"{inv['company']} — {inv['amount']} (Due {inv['due']})"
                    for inv in recent_invoices
                ],
            }
        ],
        "actions": [
            {"label": "View All Invoices", "url": "/billing/"},
            {"label": "Create Invoice", "url": "/billing/create/"},
            {"label": "Manage Invoices", "url": "/billing/manage/"},
        ],
    }
