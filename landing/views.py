from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def landing(request):
    return render(request, "landing/landing.html")


@login_required
def dashboard(request):
    cards = [

		get_crm_summary(),
        get_services_summary(),
        get_scheduling_summary(),
        get_billing_summary(),
    ]

    return render(request, "landing/dashboard.html", {"cards": cards})

#-------------
#CRM display
def get_crm_summary():
    # Placeholder data
    upcoming_tasks = [
        "Follow up with Parallel Cloak (due Mar 10)",
        "Prepare proposal for Black Sol (due Mar 14)",
    ]

    companies = [
        "Parallel Cloak",
        "Black Sol",
        "NMT co.",
        "Umbrella Corp",
    ]

    return {
    "name": "CRM Overview",
    "desc": "Upcoming tasks and company list",
    "url": "/crm/",
    "sections": [
        {"title": "Companies", "items": companies},
        {"title": "Upcoming Tasks", "items": upcoming_tasks},
    ],
    "actions": [
        {"label": "View CRM", "url": "/crm/"},
        {"label": "Add Company", "url": "/crm/"},
    ],
}

#-------------
#Service Display
def get_services_summary():
    # Placeholder data so I can test stuff
    available_services = [
        "Tech Support",
        "Maintenance",
        "Consulting",
    ]

    recent_requests = [
    f"Parallel Cloak requested: {available_services[0]}",
    f"Black Sol requested: {available_services[1]}",
    f"NMT co. requested: {available_services[2]}",
]

    return {
    "name": "Services",
    "desc": "Available services and recent requests",
    "url": "/services/",
    "sections": [
        {
            "title": "Available Services",
            "items": available_services,
        },
        {
            "title": "Recent Requests",
            "items": recent_requests,
        },
    ],
    "actions": [
        {"label": "Request a Service", "url": "/services/"}
    ],
}


#-------------
#schedule display
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
def get_billing_summary():
    # Placeholder data
    recent_invoices = [
        {"company": "Parallel Cloak", "amount": "$250", "due": "Mar 20"},
        {"company": "Black Sol", "amount": "$480", "due": "Mar 22"},
        {"company": "NMT co.", "amount": "$150", "due": "Mar 25"},
    ]

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
        {"label": "Create Invoice", "url": "/billing/"},
    ],
}



