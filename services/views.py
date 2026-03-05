from django.shortcuts import render, get_object_or_404
from .models import Service, ServiceRequest
from accounts.models import CompanyAccount

# Create your views here.
def index(request):
	return render(request, "services/index.html")

def displayServices(request, company_id):
    # Fetch the company, 404 if it doesn’t exist
    company = get_object_or_404(CompanyAccount, company_id=company_id)

    # Filter services for that company
    services = Service.objects.filter(company=company)

    return render(request, "services/displayServices.html", {
        "services": services,
        "company": company
    })
