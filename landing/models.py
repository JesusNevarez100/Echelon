from django.db import models
from django.utils import timezone
from accounts.models import User

class CompanyApplication(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED", "Submitted"
        IN_REVIEW = "IN_REVIEW", "In Review"
        APPROVED = "APPROVED", "Approved"
        DENIED = "DENIED", "Denied"

    company_name = models.CharField(max_length=255)
    company_website = models.URLField(blank=True)
    industry = models.CharField(max_length=120, blank=True)
    team_size = models.CharField(max_length=80, blank=True)

    applicant_name = models.CharField(max_length=255)
    applicant_email = models.EmailField()
    applicant_phone = models.CharField(max_length=32, blank=True)
    applicant_title = models.CharField(max_length=120, blank=True)

    use_case = models.TextField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SUBMITTED)
    submitted_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    internal_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.company_name} - {self.applicant_name} [{self.status}]"


class TesterFeedback(models.Model):
    class FeedbackType(models.TextChoices):
        BUG = "BUG", "Bug"
        CONFUSING = "CONFUSING", "Confusing"
        MISSING_FEATURE = "MISSING_FEATURE", "Missing Feature"
        DESIGN = "DESIGN", "Design"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        NEW = "NEW", "New"
        REVIEWED = "REVIEWED", "Reviewed"
        PLANNED = "PLANNED", "Planned"
        RESOLVED = "RESOLVED", "Resolved"
        DISMISSED = "DISMISSED", "Dismissed"

    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tester_feedback")
    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    feedback_type = models.CharField(max_length=24, choices=FeedbackType.choices, default=FeedbackType.BUG)
    module = models.CharField(max_length=80, blank=True)
    page_url = models.CharField(max_length=500, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    internal_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        reporter = self.name or self.email or self.submitted_by or "Anonymous"
        return f"{self.get_feedback_type_display()} feedback from {reporter}"
