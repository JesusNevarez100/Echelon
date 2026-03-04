from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
def landing(request):
	return render(request, "landing/landing.html")

@login_required
def dashboard(request):
	return render(request, "landing/dashboard.html")