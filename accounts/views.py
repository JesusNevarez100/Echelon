from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect

from accounts.forms import CreateCompanyUserForm
from accounts.models import User, Membership
from accounts.services import get_primary_membership, can_create_role
from accounts.utils import create_temp_password, create_temp_username


# Create your views here.

class ForcePasswordChangeView(PasswordChangeView):
	template_name = "registration/password_change_form.html"
	success_url = reverse_lazy("password_change_done")

	def form_valid(self, form):
		response = super().form_valid(form)

		user = self.request.user
		if user.must_change_password:
			user.must_change_password = False
			user.save(update_fields=["must_change_password"])
		return response

@login_required
def create_company_user(request):
	membership = get_primary_membership(request.user)
	if not membership:
		return HttpResponseForbidden("No company membership recognized.")
	if request.method == "POST":
		form = CreateCompanyUserForm(request.POST)
		if form.is_valid():
			target_role = form.cleaned_data["role"]

			if not can_create_role(membership.role, target_role):
				return HttpResponseForbidden("You do not have permission to create this role.")
			
			temp_username = create_temp_username(prefix=target_role.lower())
			temp_password = create_temp_password()

			new_user = User.objects.create(
				username=temp_username,
				email=form.cleaned_data["email"],
				first_name=form.cleaned_data.get("first_name", ""),
				last_name=form.cleaned_data.get("last_name", ""),
				must_change_password=True,
				# How to check if users are active or not?
				status=User.Status.ACTIVE,
			)

			new_user.set_password(temp_password)
			new_user.save()

			Membership.objects.create(
				user=new_user,
				company=membership.company,
				role=target_role
			)

			return render(request, "accounts/user_created.html", {
				"new_user":new_user,
				"temp_username":temp_username,
				"temp_password": temp_password,
				"role": target_role,
				"company": membership.company
			})
		
	else:
		form = CreateCompanyUserForm()
	
	return render(request, "accounts/create_company_user.html", {
		"form":form, 
		"company":membership.company,
		"creator_role":membership.role
	})
