from django.contrib import admin

from .models import TranscriptionRequest


@admin.register(TranscriptionRequest)
class TranscriptionRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "original_filename", "language", "status", "created_at")
