from django import forms
from accounts.models import Membership, User
from services.models import ServiceRequest
from .models import Task, Contact


def get_assignable_users(membership):
    if membership.role == Membership.Role.ADMIN:
        allowed_roles = {
            Membership.Role.ADMIN,
            Membership.Role.MANAGER,
            Membership.Role.STAFF,
            Membership.Role.CLIENT,
        }
    elif membership.role == Membership.Role.MANAGER:
        allowed_roles = {
            Membership.Role.MANAGER,
            Membership.Role.STAFF,
            Membership.Role.CLIENT,
        }
    elif membership.role == Membership.Role.STAFF:
        allowed_roles = {
            Membership.Role.STAFF,
            Membership.Role.CLIENT,
        }
    elif membership.role == Membership.Role.CLIENT:
        allowed_roles = {
            Membership.Role.CLIENT
        }
    else:
        allowed_roles = set()

    return User.objects.filter(
        memberships__company=membership.company,
        memberships__role__in=allowed_roles,
    ).distinct()


class TaskForm(forms.ModelForm):
    due_at = forms.DateTimeField(
        required=False,
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
    )

    class Meta:
        model = Task
        
        fields = [
            "title",
            "description",
            "assigned_to",
            "contact",
            "service_request",
            "status",
            "due_at",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, membership=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if membership is not None and membership.role == Membership.Role.CLIENT:
            self.fields["assigned_to"].queryset = User.objects.filter(pk=membership.user.pk)
            self.fields["assigned_to"].initial = membership.user
            self.fields["assigned_to"].disabled = True

        if membership is not None:
            if membership.role != Membership.Role.CLIENT:
                self.fields["assigned_to"].queryset = get_assignable_users(membership)
            self.fields["contact"].queryset = Contact.objects.filter(company=membership.company)
            self.fields["service_request"].queryset = ServiceRequest.objects.filter(company=membership.company)

        if self.instance and self.instance.pk and self.instance.due_at:
            self.initial["due_at"] = self.instance.due_at.strftime("%Y-%m-%dT%H:%M")