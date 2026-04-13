from django.conf import settings
from django.db import models


class TranscriptionRequest(models.Model):
    class Status(models.TextChoices):
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transcription_requests")
    original_filename = models.CharField(max_length=255)
    language = models.CharField(max_length=20, default="auto")
    status = models.CharField(max_length=20, choices=Status.choices)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
