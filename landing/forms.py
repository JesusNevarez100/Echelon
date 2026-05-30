from django import forms

from .models import CompanyApplication, TesterFeedback


class CompanyApplicationForm(forms.ModelForm):
    class Meta:
        model = CompanyApplication
        fields = [
            "company_name",
            "company_website",
            "industry",
            "team_size",
            "applicant_name",
            "applicant_email",
            "applicant_phone",
            "applicant_title",
            "use_case",
        ]
        widgets = {
            "use_case": forms.Textarea(attrs={"rows": 5}),
        }
        labels = {
            "company_name": "Company name",
            "company_website": "Company website",
            "team_size": "Team size",
            "applicant_name": "Your name",
            "applicant_email": "Work email",
            "applicant_phone": "Phone",
            "applicant_title": "Your title",
            "use_case": "How will your company use Echelon?",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-input")


class TesterFeedbackForm(forms.ModelForm):
    class Meta:
        model = TesterFeedback
        fields = [
            "name",
            "email",
            "feedback_type",
            "module",
            "page_url",
            "message",
        ]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 6}),
        }
        labels = {
            "feedback_type": "Feedback type",
            "page_url": "Page or URL",
            "message": "What happened?",
        }

    def __init__(self, *args, user=None, initial_url="", **kwargs):
        super().__init__(*args, **kwargs)

        if initial_url and not self.initial.get("page_url"):
            self.initial["page_url"] = initial_url

        if user and user.is_authenticated:
            full_name = user.get_full_name()
            if full_name and not self.initial.get("name"):
                self.initial["name"] = full_name
            if user.email and not self.initial.get("email"):
                self.initial["email"] = user.email

        self.fields["module"].widget.attrs.setdefault("placeholder", "Scheduling, Services, Dashboard, etc.")

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-input")
