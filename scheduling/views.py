from django.shortcuts import render
from django.http import JsonResponse, HttpResponseNotAllowed
from .models import Meeting
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.utils.timezone import localtime, make_aware
from accounts.models import Membership
import json


# Create your views here.
def index(request):
    return render(request, "scheduling/index.html")


def meetings_json(request):
    meetings = Meeting.objects.all()
    data = [
        {
            "id": m.id,
            "title": m.title,
            "start": localtime(m.start_at).isoformat(),
            "end": localtime(m.end_at).isoformat(),
        }
        for m in meetings
    ]
    return JsonResponse(data, safe=False)


@csrf_exempt
def create_meeting(request):
    print("METHOD:", request.method)
    print("BODY RAW:", request.body)
    print("USER:", request.user)
    print("AUTH:", request.user.is_authenticated)

    try:
        data = json.loads(request.body)
    except Exception as e:
        print("JSON ERROR:", e)
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    title = data.get("title", "")
    start = make_aware(parse_datetime(data.get("start")))
    end = make_aware(parse_datetime(data.get("end")))


	# This makes sure companies can create meetings, clients don't have permission yet sorry :(
	# Find the user's membership with role MANAGER
    membership = request.user.memberships.filter(role=Membership.Role.MANAGER).first()

    if membership is None:
        return JsonResponse({"status": "error", "message": "Manager role required"}, status=403)

    company = membership.company


    meeting = Meeting.objects.create(
	    title=title,
	    start_at=start,
	    end_at=end,
	    organizer=request.user,
	    company=company,
	)

    return JsonResponse({"status": "ok", "id": meeting.id})
