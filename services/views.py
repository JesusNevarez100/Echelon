from django.shortcuts import render, get_object_or_404
from .models import Service, ServiceRequest
from accounts.models import Membership
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

def displayServices(request, membership_id):
    membership = get_object_or_404(Membership, membership_id=membership_id)

    company = membership.company
    services = Service.objects.filter(company=company)

    return render(request, "services/displayServices.html", {
        "services": services,
        "company": company,
        "membership": membership
    })


@login_required
def servicesHome(request):
    membership = get_object_or_404(Membership, user=request.user)
    return redirect("services:company_services", membership_id=membership.membership_id)

def createService(request, membership_id):
    membership = get_object_or_404(Membership, pk=membership_id)
    company = membership.company

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")

        Service.objects.create(
            company=company,
            name=name,
            description=description,
            base_price=price
        )

        return redirect("services:company_services", membership_id=membership_id)

    return render(request, "services/createService.html", {
        "company": company,
        "membership": membership
    })
