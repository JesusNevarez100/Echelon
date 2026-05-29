from django import forms

from accounts.models import Membership, User
from .models import Meeting, MeetingParticipant


class ClientMeetingRequestForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = [
            "title",
            "description",
            "location",
            "notes",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-input")


class MeetingForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Participants",
        help_text="Choose users from this company who should participate in the meeting.",
    )

    start_at = forms.DateTimeField(
        required=True,
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
    )
    end_at = forms.DateTimeField(
        required=True,
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
    )

    class Meta:
        model = Meeting
        fields = [
            "title",
            "description",
            "location",
            "status",
            "notes",
            "start_at",
            "end_at",
            "is_billable",
            "billing_type",
            "bill_rate_cents",
            "billable_minutes_override",
        ]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

        labels = {
            "bill_rate_cents": "Billing rate cents",
            "billable_minutes_override": "Billable minutes override",
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)
        self.company = company

        if company is not None:
            self.fields["participants"].queryset = User.objects.filter(
                memberships__company=company,
            ).distinct().order_by("last_name", "first_name", "username")

        if self.instance and self.instance.pk:
            self.fields["participants"].initial = self.instance.participants.values_list("user_id", flat=True)
            if self.instance.start_at:
                self.initial["start_at"] = self.instance.start_at.strftime("%Y-%m-%dT%H:%M")
            if self.instance.end_at:
                self.initial["end_at"] = self.instance.end_at.strftime("%Y-%m-%dT%H:%M")

        self.fields["participants"].label_from_instance = self._participant_label

        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-input")

        self.fields["is_billable"].widget.attrs.setdefault("class", "checkbox-input")

    def _participant_label(self, user):
        display_name = user.get_full_name() or user.username
        membership = None
        if self.company is not None:
            membership = user.memberships.filter(company=self.company).first()
        role_label = membership.get_role_display() if membership else "User"
        email = f" - {user.email}" if user.email else ""
        return f"{display_name} ({role_label}){email}"

    def clean(self):
        cleaned_data = super().clean()
        start_at = cleaned_data.get("start_at")
        end_at = cleaned_data.get("end_at")

        if start_at and end_at and end_at <= start_at:
            self.add_error("end_at", "End time must be after the start time.")

        return cleaned_data

    def save_participants(self, meeting):
        participant_users = self.cleaned_data.get("participants")
        if participant_users is None:
            return

        MeetingParticipant.objects.filter(meeting=meeting).delete()
        MeetingParticipant.objects.bulk_create([
            MeetingParticipant(meeting=meeting, user=user)
            for user in participant_users
        ])
