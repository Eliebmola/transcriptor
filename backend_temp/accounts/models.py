from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    free_transcriptions_used = models.PositiveIntegerField(default=0)
    paid_transcription_credits = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"Profile<{self.user.username}>"
