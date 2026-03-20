from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import PasswordChangeView
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from accounts.forms import AccountProfileForm, CreateCompanyUserForm, ForceProfileResetForm
from accounts.models import Membership, User
from accounts.services import can_create_role, get_primary_membership
from accounts.utils import create_temp_password, create_temp_username

# Do not need yet, good to have
class ForcePasswordChangeView(PasswordChangeView):
    template_name = "registration/password_change_form.html"
    success_url = reverse_lazy("password_change_done")

    def form_valid(self, form):
        response = super().form_valid(form)

        user = self.request.user
        if user.must_change_password:
            user.must_change_password = False
            user.save(update_fields=["must_change_password"])

        if getattr(user, "must_change_profile", False):
            return redirect("accounts_custom:force_profile_reset")

        return response


@login_required
def account_detail(request):
    membership = get_primary_membership(request.user)
    return render(
        request,
        "accounts/account_detail.html",
        {
            "account_user": request.user,
            "membership": membership,
        },
    )


@login_required
def edit_account_detail(request):
    if request.method == "POST":
        form = AccountProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("accounts_custom:account_detail")
    else:
        form = AccountProfileForm(instance=request.user)

    membership = get_primary_membership(request.user)
    return render(
        request,
        "accounts/account_edit.html",
        {
            "form": form,
            "membership": membership,
        },
    )


@login_required
def account_list(request):
    if request.user.is_superuser:
        memberships = Membership.objects.select_related("user", "company").order_by(
            "company__name", "user__username"
        )
    else:
        membership = get_primary_membership(request.user)
        if not membership or membership.role != Membership.Role.ADMIN:
            return HttpResponseForbidden("Admin access is required.")
        memberships = Membership.objects.select_related("user", "company").filter(
            company=membership.company
        ).order_by("user__username")

    return render(
        request,
        "accounts/account_list.html",
        {
            "memberships": memberships,
        },
    )


@login_required
def force_profile_reset(request):
    user = request.user
    must_change_profile = getattr(user, "must_change_profile", False)
    must_change_password = getattr(user, "must_change_password", False)

    if not must_change_profile and not must_change_password:
        return redirect("/dashboard/")

    if request.method == "POST":
        form = ForceProfileResetForm(
            request.POST,
            user=user,
            require_profile_change=must_change_profile,
            require_password_change=must_change_password,
        )
        if form.is_valid():
            user.username = form.cleaned_data["username"]
            user.email = form.cleaned_data["email"]

            if form.cleaned_data.get("new_password1"):
                user.set_password(form.cleaned_data["new_password1"])

            user.must_change_profile = False
            user.must_change_password = False
            user.save(
                update_fields=[
                    "username",
                    "email",
                    "password",
                    "must_change_profile",
                    "must_change_password",
                ]
            )
            if form.cleaned_data.get("new_password1"):
                update_session_auth_hash(request, user)
            return redirect("/dashboard/")
    else:
        form = ForceProfileResetForm(
            user=user,
            require_profile_change=must_change_profile,
            require_password_change=must_change_password,
            initial={"username": user.username, "email": user.email},
        )

    return render(request, "accounts/force_profile_reset.html", {"form": form})


@login_required
def create_company_user(request):
    membership = get_primary_membership(request.user)
    if not membership:
        return HttpResponseForbidden("No company membership recognized.")
    MSR = Membership.Role
    allowed_roles = []
    if membership.role == MSR.ADMIN:
        allowed_roles = [MSR.MANAGER.value, MSR.STAFF.value, MSR.CLIENT.value]
    elif membership.role == MSR.MANAGER:
        allowed_roles = [MSR.MANAGER.value, MSR.STAFF.value, MSR.CLIENT.value]
    elif membership.role == MSR.STAFF:
        allowed_roles = [MSR.CLIENT.value]
    
    if request.method == "POST":
        form = CreateCompanyUserForm(request.POST, allowed_roles=allowed_roles)
        if form.is_valid():
            target_role = form.cleaned_data["role"]

            if not can_create_role(membership.role, target_role):
                return HttpResponseForbidden("You do not have permission to create this role.")

            temp_username = create_temp_username(prefix=target_role.lower())
            temp_password = create_temp_password()

            new_user = User.objects.create(
                username=temp_username,
                first_name=form.cleaned_data.get("first_name", ""),
                last_name=form.cleaned_data.get("last_name", ""),
                must_change_password=True,
                must_change_profile=True,
                status=User.Status.ACTIVE,
            )

            new_user.set_password(temp_password)
            new_user.save()

            Membership.objects.create(
                user=new_user,
                company=membership.company,
                role=target_role,
            )

            return render(
                request,
                "accounts/user_created.html",
                {
                    "new_user": new_user,
                    "temp_username": temp_username,
                    "temp_password": temp_password,
                    "role": target_role,
                    "company": membership.company,
                },
            )

    else:
        form = CreateCompanyUserForm(allowed_roles=allowed_roles)

    return render(
        request,
        "accounts/create_company_user.html",
        {
            "form": form,
            "company": membership.company,
            "creator_role": membership.role,
        },
    )
