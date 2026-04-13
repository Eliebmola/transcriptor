from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile

from rest_framework import serializers

from .permissions import get_transcription_access_kind


class TranscriptionUploadSerializer(serializers.Serializer):
    audio_file = serializers.FileField()
    language = serializers.CharField(required=False, allow_blank=True, default="auto")
    model = serializers.CharField(required=False, allow_blank=True, default="small")

    def validate_audio_file(self, value):
        max_size = 30 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("El audio supera el limite de 30 MB.")

        duration_seconds = probe_audio_duration(value)
        request = self.context.get("request")
        access_kind = get_transcription_access_kind(request.user) if request and request.user.is_authenticated else None
        max_duration_seconds = 45 * 60
        if access_kind == "free" and duration_seconds > max_duration_seconds:
            raise serializers.ValidationError("El audio supera el limite de 45 minutos.")
        return value


def probe_audio_duration(uploaded_file) -> float:
    suffix = Path(uploaded_file.name).suffix or ".audio"
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_path = Path(temp_file.name)

        uploaded_file.seek(0)
        ffprobe_executable = resolve_ffprobe_executable()
        completed = subprocess.run(
            [
                str(ffprobe_executable),
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "json",
                str(temp_path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(completed.stdout or "{}")
        return float(payload.get("format", {}).get("duration", 0.0))
    except Exception as exc:
        raise serializers.ValidationError(f"No fue posible validar la duracion del audio: {exc}") from exc
    finally:
        uploaded_file.seek(0)
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)


def resolve_ffprobe_executable() -> Path:
    configured_dir = os.getenv("FFMPEG_BIN_DIR", "").strip()
    if configured_dir:
        candidate = Path(configured_dir) / "ffprobe.exe"
        if candidate.exists():
            return candidate

    winget_root = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"
    if winget_root.exists():
        for candidate in winget_root.glob("**/ffprobe.exe"):
            if candidate.exists():
                return candidate

    return Path("ffprobe")
