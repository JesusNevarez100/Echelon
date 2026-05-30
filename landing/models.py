from django.db import models
from django.utils import timezone

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
