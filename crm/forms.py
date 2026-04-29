from django import forms
from django.db.models import Q
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


def get_grouped_assignable_users(membership):
    company = membership.company

    memberships = (
        Membership.objects
        .filter(company=company)
        .select_related("user")
        .exclude(role=Membership.Role.ADMIN)
    )

    if membership.role == Membership.Role.CLIENT:
        memberships = memberships.filter(user=membership.user)
    elif membership.role == Membership.Role.STAFF:
        memberships = memberships.filter(
            Q(user=membership.user) | Q(role=Membership.Role.CLIENT)
        )
    elif membership.role == Membership.Role.MANAGER:
        # Managers can assign to everyone except admins
        pass
    else:
        memberships = Membership.objects.none()

    grouped = {
        "Managers":[],
        "Staff":[],
        "Clients": []
    }

    for member in memberships:
        label = member.user.get_full_name() or member.user.username

        if member.role == Membership.Role.MANAGER:
            grouped["Managers"].append((member.user.pk, label))
        elif member.role == Membership.Role.STAFF:
            grouped["Staff"].append((member.user.pk, label))
        elif member.role == Membership.Role.CLIENT:
            grouped["Clients"].append((member.user.pk, label))
    
    return [
        (group_name, choices)
        for group_name, choices in grouped.items()
        if choices
    ]

class TaskInlineUpdateForm(forms.ModelForm):
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
            "status",
            "due_at"
        ]

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
            # "contact",
            "service_request",
            "status",
            "due_at",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, membership=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.membership = membership

        if membership is not None:
            # self.fields["contact"].queryset = Contact.objects.filter(company=membership.company)
            self.fields["service_request"].queryset = ServiceRequest.objects.filter(company=membership.company)

            self.fields["assigned_to"].choices = get_grouped_assignable_users(membership)

            if membership.role == Membership.Role.CLIENT:
                self.fields["assigned_to"].initial = membership.user.pk
                self.fields["assigned_to"].disabled = True

        if self.instance and self.instance.pk and self.instance.due_at:
            self.initial["due_at"] = self.instance.due_at.strftime("%Y-%m-%dT%H:%M")

    def clean_assigned_to(self):
        assigned_to = self.cleaned_data.get("assigned_to")
        membership = self.membership
        
        if membership is None:
            raise forms.ValidationError("No membership found.")
        
        if membership.role == Membership.Role.CLIENT:
            return membership.user
        
        allowed_user_ids = []

        for group_name, choices in get_grouped_assignable_users(membership):
            for user_id, label in choices:
                allowed_user_ids.append(user_id)
        if assigned_to and assigned_to.pk not in allowed_user_ids:
            raise forms.ValidationError("You cannot assign a task to this user.")
        
        return assigned_to

