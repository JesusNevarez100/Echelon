from django import forms

from .models import CompanyApplication


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
