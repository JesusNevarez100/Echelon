from django import forms
from .models import Membership, User

class CreateCompanyUserForm(forms.Form):
	role = forms.ChoiceField(choices=Membership.Role.choices)

	first_name = forms.CharField(max_length=150, required=False)
	last_name = forms.CharField(max_length=150, required=False)
	email = forms.EmailField( required=False)

	def clean_email(self):
		email = self.cleaned_data["email"].strip().lower()
		if User.objects.filter(email__iexact=email).exists():
			raise forms.ValidationError("A user with this email already exists")
		return email