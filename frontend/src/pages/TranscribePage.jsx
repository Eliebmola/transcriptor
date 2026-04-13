import { useState } from "react";

import { StatusBanner } from "../components/StatusBanner";
import { API_BASE_URL } from "../lib/api";
import { useAuth } from "../state/AuthContext";

export function TranscribePage() {
  const { token, refreshMe } = useAuth();
  const [uploadForm, setUploadForm] = useState({
    audioFile: null,
    language: "auto",
    model: "tiny",
  });
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState(
    "Los archivos transcritos deben descargarse de inmediato. La plataforma no los almacena permanentemente.",
  );
  const [error, setError] = useState("");

  function updateUploadField(event) {
    const { name, value, files } = event.target;
    if (name === "audioFile") {
      setUploadForm((current) => ({ ...current, audioFile: files?.[0] || null }));
      return;
    }
    setUploadForm((current) => ({ ...current, [name]: value }));
  }

  async function handleUpload(event) {
    event.preventDefault();
    if (!uploadForm.audioFile) {
      setError("Selecciona un archivo de audio antes de continuar.");
      return;
    }

    setIsUploading(true);
    setError("");
    setMessage("Procesando audio. La descarga empezara en cuanto el ZIP este listo.");

    const formData = new FormData();
    formData.append("audio_file", uploadForm.audioFile);
    formData.append("language", uploadForm.language);
    formData.append("model", uploadForm.model);

    try {
      const response = await fetch(`${API_BASE_URL}/api/transcriptions/process/`, {
        method: "POST",
        headers: {
          Authorization: `Token ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const payload = await response.json();
        throw new Error(payload.detail || payload.error || "La transcripcion fallo.");
      }

      const blob = await response.blob();
      const filename = getFilename(response.headers.get("content-disposition")) || "transcripcion.zip";
      const blobUrl = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = blobUrl;
      anchor.download = filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(blobUrl);

      setMessage("Descarga iniciada. Guarda el ZIP ahora porque el sistema no almacena los archivos.");
      await refreshMe();
    } catch (uploadError) {
      setError(uploadError.message);
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <section className="page-card">
      <div className="section-head">
        <div>
          <span className="eyebrow">Transcripcion</span>
          <h1>Sube tu audio</h1>
        </div>
      </div>

      <p className="section-copy">
        Se aceptan audios de hasta 45 minutos. Si no tienes plan activo, el sistema usara primero
        tus creditos pagos y despues tus pruebas gratis disponibles.
      </p>

      <form className="form-grid" onSubmit={handleUpload}>
        <label>
          Archivo de audio
          <input name="audioFile" type="file" accept="audio/*" onChange={updateUploadField} required />
        </label>

        <label>
          Idioma
          <select name="language" value={uploadForm.language} onChange={updateUploadField}>
            <option value="auto">Detectar automaticamente</option>
            <option value="es">Espanol</option>
            <option value="en">Ingles</option>
            <option value="pt">Portugues</option>
            <option value="fr">Frances</option>
          </select>
        </label>

        <label>
          Modelo
          <select name="model" value={uploadForm.model} onChange={updateUploadField}>
            <option value="tiny">tiny</option>
            <option value="base">base</option>
            <option value="small">small</option>
          </select>
        </label>

        <button className="primary-button" type="submit" disabled={isUploading}>
          {isUploading ? "Transcribiendo..." : "Transcribir y descargar ZIP"}
        </button>
      </form>

      <StatusBanner tone="neutral">{message}</StatusBanner>
      <StatusBanner tone="danger">{error}</StatusBanner>
    </section>
  );
}

function getFilename(contentDisposition) {
  if (!contentDisposition) return "";
  const match = contentDisposition.match(/filename=\"(.+?)\"/i);
  return match?.[1] || "";
}
