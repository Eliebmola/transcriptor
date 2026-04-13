from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "free_transcriptions_used", "paid_transcription_credits")

# Register your models here.
