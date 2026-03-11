from django.shortcuts import redirect
from django.urls import reverse

# Forces user to change account information
class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            if getattr(user, "must_change_password", False) or getattr(user, "must_change_profile", False):
                allowed = [
                    reverse("accounts_custom:force_profile_reset"),
                    reverse("logout"),
                ]
                if request.path not in allowed and not request.path.startswith("/admin/"):
                    return redirect("accounts_custom:force_profile_reset")

        return self.get_response(request)
