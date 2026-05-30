from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("landing", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TesterFeedback",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=255)),
                ("email", models.EmailField(blank=True, max_length=254)),
                (
                    "feedback_type",
                    models.CharField(
                        choices=[
                            ("BUG", "Bug"),
                            ("CONFUSING", "Confusing"),
                            ("MISSING_FEATURE", "Missing Feature"),
                            ("DESIGN", "Design"),
                            ("OTHER", "Other"),
                        ],
                        default="BUG",
                        max_length=24,
                    ),
                ),
                ("module", models.CharField(blank=True, max_length=80)),
                ("page_url", models.CharField(blank=True, max_length=500)),
                ("message", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("NEW", "New"),
                            ("REVIEWED", "Reviewed"),
                            ("PLANNED", "Planned"),
                            ("RESOLVED", "Resolved"),
                            ("DISMISSED", "Dismissed"),
                        ],
                        default="NEW",
                        max_length=16,
                    ),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("internal_notes", models.TextField(blank=True)),
                (
                    "submitted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="tester_feedback",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
