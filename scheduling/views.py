from accounts.models import Membership
from accounts.services import get_primary_membership
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import localtime
from django.views import View
from django.utils.decorators import method_decorator

from .forms import ClientMeetingRequestForm, MeetingForm
from .models import Meeting


COMPANY_ROLES = {Membership.Role.ADMIN, Membership.Role.MANAGER, Membership.Role.STAFF}
CLIENT_ROLES = {Membership.Role.CLIENT}


def _is_company_member(membership):
    return membership.role in COMPANY_ROLES


def _is_client_member(membership):
    return membership.role in CLIENT_ROLES


def _visible_meetings(membership):
    meetings = Meeting.objects.filter(company=membership.company).prefetch_related("participants__user")

    if _is_company_member(membership):
        return meetings.filter(
            Q(status=Meeting.Status.REQUESTED)
            | Q(organizer=membership.user)
            | Q(participants__user=membership.user)
        ).distinct()

    if _is_client_member(membership):
        return meetings.filter(
            Q(requested_by=membership.user)
            | Q(participants__user=membership.user)
        ).distinct()

    return Meeting.objects.none()


@method_decorator(login_required, name="dispatch")
class SchedulingIndexView(View):
    template_name = "scheduling/index.html"

    def get(self, request, *args, **kwargs):
        membership = get_primary_membership(request.user)
        visible_meetings = _visible_meetings(membership)
        pending_meetings = visible_meetings.filter(status=Meeting.Status.REQUESTED).order_by("-created_at")
        scheduled_meetings = visible_meetings.exclude(status=Meeting.Status.REQUESTED).order_by("start_at", "-created_at")

        return render(request, self.template_name, {
            "company": membership.company,
            "membership": membership,
            "meetings": scheduled_meetings,
            "pending_meetings": pending_meetings,
            "can_request_meetings": _is_client_member(membership),
            "can_update_meetings": _is_company_member(membership),
        })

    def post(self, request, *args, **kwargs):
        membership = get_primary_membership(request.user)
        action = request.POST.get("action")

        if action == "update_meeting" and _is_company_member(membership):
            meeting = _get_staff_reviewable_meeting(request, membership)
            form = MeetingForm(request.POST, instance=meeting, company=membership.company)
            if form.is_valid():
                meeting = form.save(commit=False)
                if meeting.status == Meeting.Status.ACTIVE and meeting.organizer_id is None:
                    meeting.organizer = membership.user
                meeting.save()
                form.save_participants(meeting)

        elif action == "deny_meeting" and _is_company_member(membership):
            meeting = _get_company_meeting(request, membership)
            if meeting.status == Meeting.Status.REQUESTED:
                meeting.status = Meeting.Status.CANCELED
                meeting.save(update_fields=["status"])

        elif action == "delete_meeting" and _is_company_member(membership):
            meeting = _get_company_meeting(request, membership)
            meeting.delete()

        return redirect("scheduling:index")


index = SchedulingIndexView.as_view()


@login_required
def create_meeting(request):
    membership = get_primary_membership(request.user)

    if _is_company_member(membership):
        form_class = MeetingForm
        template_context = {"is_client_request": False}
        form_kwargs = {"company": membership.company}
    elif _is_client_member(membership):
        form_class = ClientMeetingRequestForm
        template_context = {"is_client_request": True}
        form_kwargs = {}
    else:
        return redirect("scheduling:index")

    if request.method == "POST":
        form = form_class(request.POST, **form_kwargs)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.company = membership.company

            if _is_company_member(membership):
                meeting.organizer = membership.user
                if meeting.status == Meeting.Status.REQUESTED:
                    meeting.status = Meeting.Status.ACTIVE
            else:
                meeting.requested_by = membership.user
                meeting.status = Meeting.Status.REQUESTED

            meeting.save()

            if _is_company_member(membership):
                form.save_participants(meeting)

            return redirect("scheduling:index")
    else:
        form = form_class(**form_kwargs)

    context = {
        "company": membership.company,
        "membership": membership,
        "form": form,
    }
    context.update(template_context)
    return render(request, "scheduling/createMeeting.html", context)


@login_required
def meetings_json(request):
    membership = get_primary_membership(request.user)
    meetings = _visible_meetings(membership).exclude(
        status__in=[Meeting.Status.REQUESTED, Meeting.Status.CANCELED],
    ).exclude(
        start_at__isnull=True,
    ).exclude(
        end_at__isnull=True,
    )

    data = [
        {
            "id": meeting.id,
            "title": meeting.title,
            "start": localtime(meeting.start_at).isoformat(),
            "end": localtime(meeting.end_at).isoformat(),
            "color": _calendar_color(meeting.status),
        }
        for meeting in meetings
    ]
    return JsonResponse(data, safe=False)


def _get_company_meeting(request, membership):
    meeting_id = request.POST.get("meeting_id")
    return get_object_or_404(Meeting, id=meeting_id, company=membership.company)


def _get_staff_reviewable_meeting(request, membership):
    meeting = _get_company_meeting(request, membership)
    if meeting.status == Meeting.Status.REQUESTED:
        return meeting
    return get_object_or_404(
        _visible_meetings(membership),
        id=meeting.id,
        company=membership.company,
    )


def _calendar_color(status):
    return {
        Meeting.Status.ACTIVE: "#22c55e",
        Meeting.Status.FINISHED: "#8ca5d7",
        Meeting.Status.CANCELED: "#dc2626",
    }.get(status, "#8ca5d7")
