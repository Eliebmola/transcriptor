from __future__ import annotations

from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TranscriptionRequest
from .permissions import can_user_transcribe, consume_transcription_access
from .serializers import TranscriptionUploadSerializer
from .services import build_zip_bundle


class TranscriptionUploadView(APIView):
    def post(self, request):
        serializer = TranscriptionUploadSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        allowed, message = can_user_transcribe(request.user)
        if not allowed:
            return Response(
                {
                    "detail": message,
                    "download_notice": "Los archivos transcritos no se almacenan permanentemente. Deben descargarse de inmediato.",
                },
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        audio_file = serializer.validated_data["audio_file"]
        language = serializer.validated_data["language"] or "auto"
        model_name = serializer.validated_data["model"] or "small"

        try:
            archive_bytes, archive_name = build_zip_bundle(
                upload_name=audio_file.name,
                upload_bytes=audio_file.read(),
                model_name=model_name,
                language=language,
            )
            TranscriptionRequest.objects.create(
                user=request.user,
                original_filename=audio_file.name,
                language=language,
                status=TranscriptionRequest.Status.COMPLETED,
            )
            consume_transcription_access(request.user)
        except Exception as exc:
            TranscriptionRequest.objects.create(
                user=request.user,
                original_filename=audio_file.name,
                language=language,
                status=TranscriptionRequest.Status.FAILED,
                error_message=str(exc),
            )
            return Response(
                {
                    "detail": "Ocurrio un error durante la transcripcion.",
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response = HttpResponse(archive_bytes, content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{archive_name}"'
        response["X-Download-Notice"] = "Descarga este archivo ahora. No se almacena permanentemente."
        return response
