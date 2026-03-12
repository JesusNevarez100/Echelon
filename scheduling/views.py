from django.shortcuts import render
from django.http import JsonResponse, HttpResponseNotAllowed
from .models import Meeting
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
import json

# Create your views here.
def index(request):
    return render(request, "scheduling/index.html")


def meetings_json(request):
    meetings = Meeting.objects.all().values(
        "id", "title", "start_at", "end_at"
    )
    return JsonResponse(list(meetings), safe=False)

#Handles meeting stuff, updated to post correctly, idk how great it works cause it doesn't have superuser perms
@csrf_exempt
def create_meeting(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    title = data.get("title", "")
    start = parse_datetime(data.get("start"))
    end = parse_datetime(data.get("end"))


    # This makes sure companies can create meetings, clients don't have permission yet sorry :(
    company = getattr(request.user, "companyaccount", None)
    if company is None:
        return JsonResponse({"status": "error", "message": "Company is required"}, status=400)

    meeting = Meeting.objects.create(
        title=title,
        start_at=start,
        end_at=end,
        organizer=request.user if request.user.is_authenticated else None,
        company=company,
    )

    return JsonResponse({"status": "ok", "id": meeting.id})
