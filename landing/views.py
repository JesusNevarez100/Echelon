from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseForbidden
from types import SimpleNamespace
from accounts.models import Membership
from accounts.services import get_primary_membership

def landing(request):
    return render(request, "landing/landing.html")

#Manages the functionality of the blocks
@login_required
def dashboard(request):
    cards = [

		get_crm_summary(request),
        get_services_summary(request),
        get_scheduling_summary(),
        get_billing_summary(request),
    ]

    return render(request, "landing/dashboard.html", {"cards": cards})


#THIS IS FOR TESTING CAUSE I WASN'T SURE HOW TO CREATE THE ACCOUNTS! 
#If you wanna test with this, embed the link with dashboard/?as=client or dashboard/?as=company
def get_fake_membership_for_superuser(mode="company"):
    if mode == "client":
        role = Membership.Role.CLIENT
    else:
        role = Membership.Role.MANAGER

    return SimpleNamespace(
        role=role,
        company=SimpleNamespace(name="Test Company"),
    )

#-------------
#CRM display

@login_required
def get_crm_summary(request):
    # Toggles superuser stuff for testing purposes
    if request.user.is_superuser:
        mode = request.GET.get("as", "company") 
        membership = get_fake_membership_for_superuser(mode)
        is_client = membership.role == Membership.Role.CLIENT
    else:
        membership = get_primary_membership(request.user)
        if membership is None:
            return HttpResponseForbidden("No company membership recognized.")
        is_client = membership.role == Membership.Role.CLIENT

    #Test data (replace later)
    test_company_clients = ["Parallel Cloak", "Black Sol", "NMT co.", "Umbrella Corp",]
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
        summary = {
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

    #COMPANY SIDE
    else:
        summary = {
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

    return summary

#-------------
#Service Display
def get_services_summary(request):
    # same superuser stuff as before
    if request.user.is_superuser:
        mode = request.GET.get("as", "company")
        membership = get_fake_membership_for_superuser(mode)
        is_client = membership.role == Membership.Role.CLIENT
    else:
        membership = get_primary_membership(request.user)
        if membership is None:
            return HttpResponseForbidden("No company membership recognized.")
        is_client = membership.role == Membership.Role.CLIENT

    # more test data-
    available_services = [
        "Tech Support",
        "Maintenance",
        "Consulting",
    ]

    # Pretend these are service requests from clients
    recent_requests = [
        f"Parallel Cloak requested: {available_services[0]}",
        f"Black Sol requested: {available_services[1]}",
        f"NMT co. requested: {available_services[2]}",
    ]

    # clients can see the requests they put in
    client_recent_requests = [
        f"{membership.company.name} requested: {available_services[0]}"
    ]
    # ---------------------------------------------------

    #CLIENT SIDE
    if is_client:
        summary = {
            "name": "Services",
            "desc": "Available services and your recent requests",
            "url": "/services/",
            "sections": [
                {
                    "title": "Available Services",
                    "items": available_services,
                },
                {
                    "title": "Your Recent Requests",
                    "items": client_recent_requests,
                },
            ],
            "actions": [
                {"label": "Request a Service", "url": "/services/request/"}
            ],
        }

    #COMPANY SIDE
    else:
        summary = {
            "name": "Services",
            "desc": "Available services and client requests",
            "url": "/services/",
            "sections": [
                {
                    "title": "Available Services",
                    "items": available_services,
                },
                {
                    "title": "Recent Client Requests",
                    "items": recent_requests,
                },
            ],
            "actions": [
                {"label": "Request a Service", "url": "/services/request/"},
                {"label": "Add Service", "url": "/services/add/"},
            ],
        }

    return summary

#-------------
#schedule display
#Changed literally nothing, this one should be universal I feel
def get_scheduling_summary():
    upcoming = [
        "Upcoming meeting: March 12, 2026 at 3:00 PM",
        "2 pending reservation requests",
    ]

    return {
        "name": "Scheduling",
        "desc": "Make and manage meetings",
        "url": "/scheduling/",
        "sections": [
            {
                "title": "Upcoming",
                "items": upcoming,
            }
        ],
        "actions": [
            {"label": "View Calendar", "url": "/scheduling/"},
            {"label": "New Reservation", "url": "/scheduling/"},
        ],
    }

#-------------
#Invoice display
def get_billing_summary(request):
    # you know the drill
    if request.user.is_superuser:
        mode = request.GET.get("as", "company")
        membership = get_fake_membership_for_superuser(mode)
        is_client = membership.role == Membership.Role.CLIENT
    else:
        membership = get_primary_membership(request.user)
        if membership is None:
            return HttpResponseForbidden("No company membership recognized.")
        is_client = membership.role == Membership.Role.CLIENT

    # test data
    recent_invoices = [
        {"company": "Parallel Cloak", "amount": "$250", "due": "Mar 20"},
        {"company": "Black Sol", "amount": "$480", "due": "Mar 22"},
        {"company": "NMT co.", "amount": "$150", "due": "Mar 25"},
    ]

    # invoices sent by company
    client_invoices = [
        f"{membership.company.name} — $250 (Due Mar 20)"
    ]

    #CLIENT SIDE
    if is_client:
        summary = {
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
                # No create invoice button for clients
            ],
        }

    #COMPANY SIDE
    else:
        summary = {
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

    return summary
