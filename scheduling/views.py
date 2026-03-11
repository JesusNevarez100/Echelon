from django.shortcuts import render
from django.http import JsonResponse
from .models import Meeting
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
import json

# Create your views here.
def index(request):
	return render(request, "scheduling/index.html")


# Meeting request format
def meetings_json(request):
    meetings = Meeting.objects.all()

    events = []
    for m in meetings:
        events.append({
            "id": m.id,
            "title": m.title,
            "start": m.start_at.isoformat(),
            "end": m.end_at.isoformat(),
        })

    return JsonResponse(events, safe=False)

#Meeting creator
@csrf_exempt
def create_meeting(request):
    attendees = data.get("attendees", "")
    if request.method == "POST":
        data = json.loads(request.body)

        meeting = Meeting.objects.create(
            title=data["title"],
            start_at=parse_datetime(data["start"]),
            end_at=parse_datetime(data["end"]),
            organizer=request.user if request.user.is_authenticated else None,
            company=request.user.companyaccount if request.user.is_authenticated else None,
        )

        return JsonResponse({"status": "ok", "id": meeting.id})
