from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from .models import Service, ServiceRequest
from accounts.models import Membership
from accounts.services import get_primary_membership

@method_decorator(login_required, name="dispatch")
class DisplayServicesView(View):
    template_name = "services/displayServices.html"
    company_roles = {Membership.Role.MANAGER, Membership.Role.STAFF, Membership.Role.ADMIN}
    client_roles = {Membership.Role.CLIENT}

    def _is_company_member(self, membership):
        return membership.role in self.company_roles

    def _is_client_member(self, membership):
        return membership.role in self.client_roles
        
    def _get_requested_services(self, membership):
        if self._is_company_member(membership):
            return ServiceRequest.objects.filter(
                service__company=membership.company
            ).select_related("service", "requested_by", "company")

        if self._is_client_member(membership):
            return ServiceRequest.objects.filter(
                requested_by=membership.user,
                service__company=membership.company
            ).select_related("service", "requested_by", "company")
        
        return ServiceRequest.objects.none()
    
    def get(self, request, *args, **kwargs):
        membership = get_primary_membership(request.user)
        company = membership.company
        services = Service.objects.filter(company=company)
        requested_services = self._get_requested_services(membership)

        return render(request, self.template_name, {
            "services": services,
            "company": company,
            "membership": membership, 
            "requested_services": requested_services,
            "can_request_services": self._is_client_member(membership),
            "can_update_services": self._is_company_member(membership),
            "can_view_all_requests": self._is_company_member(membership)
        })
    
    def post(self, request, *args, **kwargs):
        membership = get_primary_membership(request.user)
        action = request.POST.get("action")

        if action == "request_service" and self._is_client_member(membership):
            service_id = request.POST.get("service_id")
            if not service_id:
                return redirect("services:services_home")
            service = get_object_or_404(Service, id=service_id, company=membership.company)
            ServiceRequest.objects.create(
                service=service,
                company=membership.company,
                requested_by=membership.user
            )
        elif action == "update_service" and self._is_company_member(membership):
            service_id = request.POST.get("service_id")
            if not service_id:
                return redirect("services:services_home")
            service = get_object_or_404(
                Service,
                id=service_id,
                company=membership.company,
            )

            service.name = request.POST.get("name", service.name)
            service.description = request.POST.get("description", service.description)
            service.base_price = request.POST.get("price", service.base_price)
            service.save()

        elif action == "complete_request" and self._is_company_member(membership):
            request_id = request.POST.get("request_id")
            if not request_id:
                return redirect("services:services_home")

            service_request = get_object_or_404(
                ServiceRequest,
                id=request_id,
                company=membership.company,
            )
            service_request.status = ServiceRequest.Status.COMPLETED
            service_request.save()

        elif action == "delete_service" and self._is_company_member(membership):
            service_id = request.POST.get("service_id")
            if not service_id:
                return redirect("services:services_home")

            service = get_object_or_404(
                Service,
                id=service_id,
                company=membership.company,
            )
            service.delete()

        elif action == "delete_request" and self._is_company_member(membership):
            request_id = request.POST.get("request_id")
            if not request_id:
                return redirect("services:services_home")

            service_request = get_object_or_404(
                ServiceRequest,
                id=request_id,
                company=membership.company,
            )
            service_request.delete()

        return redirect("services:services_home")
displayServices = DisplayServicesView.as_view()
def createService(request):
    # membership = get_object_or_404(Membership, pk=membership_id)
    membership = get_primary_membership(request.user)
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

        return redirect("services:services_home")

    return render(request, "services/createService.html", {
        "company": company,
        "membership": membership
    })
