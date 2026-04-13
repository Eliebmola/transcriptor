from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
import whisper

try:
    from docx import Document
except ImportError:  # pragma: no cover
    Document = None


@dataclass(slots=True)
class TranscriptionArtifacts:
    transcript: str
    pdf_path: Path
    txt_path: Path
    docx_path: Path | None


def sanitize_text(text: str) -> str:
    return " ".join(text.split()).strip()


def transcribe_audio(model, audio_path: Path, language: str | None) -> str:
    result = model.transcribe(str(audio_path), language=language, fp16=False, verbose=False)
    parts: list[str] = []
    for segment in result.get("segments", []):
        text = sanitize_text(segment.get("text", ""))
        if text:
            parts.append(text)
    return "\n\n".join(parts)


def wrap_line(text: str, font_name: str, font_size: int, max_width: float) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if stringWidth(candidate, font_name, font_size) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def write_pdf(title: str, transcript: str, output_path: Path) -> None:
    pdf = canvas.Canvas(str(output_path), pagesize=LETTER)
    width, height = LETTER
    left = 54
    top = height - 54
    bottom = 54
    line_height = 15
    body_font = "Helvetica"
    title_font = "Helvetica-Bold"

    def new_page() -> float:
        pdf.showPage()
        pdf.setFont(body_font, 11)
        return top

    y = top
    pdf.setTitle(title)
    pdf.setFont(title_font, 14)
    pdf.drawString(left, y, title)
    y -= 28
    pdf.setFont(body_font, 11)

    max_width = width - (left * 2)
    for paragraph in transcript.split("\n"):
        lines = wrap_line(paragraph, body_font, 11, max_width) if paragraph else [""]
        for line in lines:
            if y <= bottom:
                y = new_page()
            pdf.drawString(left, y, line)
            y -= line_height
        y -= 6

    pdf.save()


def write_txt(transcript: str, output_path: Path) -> None:
    output_path.write_text(transcript + "\n", encoding="utf-8")


def write_docx(title: str, transcript: str, output_path: Path) -> Path | None:
    if Document is None:
        return None

    document = Document()
    document.add_heading(title, level=1)
    for paragraph in transcript.split("\n"):
        document.add_paragraph(paragraph)
    document.save(str(output_path))
    return output_path


def generate_transcription_artifacts(
    audio_path: Path,
    output_dir: Path,
    model_name: str = "small",
    language: str | None = "es",
) -> TranscriptionArtifacts:
    output_dir.mkdir(parents=True, exist_ok=True)

    model = whisper.load_model(model_name)
    transcript = transcribe_audio(model, audio_path.resolve(), language)
    if not transcript:
        transcript = "[No se detecto texto en el audio.]"

    title = f"Transcripcion de {audio_path.name}"
    pdf_path = output_dir / f"{audio_path.stem}.pdf"
    txt_path = output_dir / f"{audio_path.stem}.txt"
    docx_path = output_dir / f"{audio_path.stem}.docx"

    write_pdf(title, transcript, pdf_path)
    write_txt(transcript, txt_path)
    generated_docx = write_docx(title, transcript, docx_path)

    return TranscriptionArtifacts(
        transcript=transcript,
        pdf_path=pdf_path,
        txt_path=txt_path,
        docx_path=generated_docx,
    )
