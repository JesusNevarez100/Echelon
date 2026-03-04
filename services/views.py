from django.shortcuts import render
from .models import Service, ServiceRequest

# Create your views here.
def index(request):
	return render(request, "services/index.html")

def displayServices(request):
	# Should only display a companies services
	services = Service.objects.filter(company=request.user.company)

	context = {
		"services": services,
	}
	return render(request, "services/displayServices.html", context=context)