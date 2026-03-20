from django import forms
from django.contrib.auth.password_validation import validate_password

from .models import Membership, User


class CreateCompanyUserForm(forms.Form):
    role = forms.ChoiceField(choices=Membership.Role.choices)

    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    ## Email not needed for created account; it is collected later in the reset details.
    # email = forms.EmailField(required=False)

    def __init__(self, *args, allowed_roles=None, **kwargs):
        super().__init__(*args, **kwargs)

        role_choices = set(Membership.Role.choices)
        if allowed_roles is not None:
            allowed_roles = set(allowed_roles)
            role_choices = [
                (value, label)
                for value, label in role_choices
                if value in allowed_roles
            ]
        self.fields["role"].choices = role_choices
        


class AccountProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


class ForceProfileResetForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    new_password1 = forms.CharField(
        label="New password",
        strip=False,
        widget=forms.PasswordInput,
        required=False,
    )
    new_password2 = forms.CharField(
        label="Confirm new password",
        strip=False,
        widget=forms.PasswordInput,
        required=False,
    )

    def __init__(self, *args, user: User, require_profile_change: bool, require_password_change: bool, **kwargs):
        self.user = user
        self.require_profile_change = require_profile_change
        self.require_password_change = require_password_change
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if self.require_profile_change and username == self.user.username:
            raise forms.ValidationError("Choose a new username different from the temporary one.")
        if User.objects.filter(username__iexact=username).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if self.require_profile_change and email == (self.user.email or "").strip().lower():
            raise forms.ValidationError("Choose a new email different from the temporary one.")
        if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if self.require_password_change:
            if not password1 or not password2:
                raise forms.ValidationError("Enter and confirm your new password.")
            if password1 != password2:
                raise forms.ValidationError("New password fields did not match.")
            validate_password(password1, self.user)
        elif password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("New password fields did not match.")
            validate_password(password1, self.user)

        return cleaned_data
