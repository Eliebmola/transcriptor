from django.urls import path

from .views import TranscriptionUploadView

urlpatterns = [
    path("process/", TranscriptionUploadView.as_view(), name="transcription-process"),
]
