from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def landing(request):
    return render(request, "landing/landing.html")

@login_required
def dashboard(request):
    cards = [
        {"name": "CRM", "desc": "Contacts + Tasks", "url": "/crm/"},
        {"name": "Services", "desc": "Service catalog + Requests", "url": "/services/"},
        {"name": "Scheduling", "desc": "Meetings + Participants", "url": "/scheduling/"},
        {"name": "Billing", "desc": "Invoices + Line Items", "url": "/billing/"},
    ]

    print("Dashboard view is running")  # Debug

    return render(request, "landing/dashboard.html", {"cards": cards})
