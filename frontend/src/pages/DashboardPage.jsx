import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { StatusBanner } from "../components/StatusBanner";
import { fetchWithToken } from "../lib/api";
import { useAuth } from "../state/AuthContext";

export function DashboardPage() {
  const { token, user, refreshMe } = useAuth();
  const [billing, setBilling] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    void loadData();
  }, []);

  async function loadData() {
    try {
      const [billingStatus] = await Promise.all([
        fetchWithToken("/api/billing/status/", token),
        refreshMe(),
      ]);
      setBilling(billingStatus);
      setError("");
    } catch (loadError) {
      setError(loadError.message);
    }
  }

  return (
    <div className="page-stack">
      <section className="page-card">
        <div className="section-head">
          <div>
            <span className="eyebrow">Dashboard</span>
            <h1>Resumen de la cuenta</h1>
          </div>
          <button className="ghost-button" type="button" onClick={() => void loadData()}>
            Actualizar
          </button>
        </div>

        <div className="stats-grid">
          <article className="stat-card">
            <span>Usuario</span>
            <strong>{user?.username}</strong>
          </article>
          <article className="stat-card">
            <span>Intentos gratis</span>
            <strong>{user?.free_transcriptions_remaining ?? 0}</strong>
          </article>
          <article className="stat-card">
            <span>Creditos pagos</span>
            <strong>{user?.paid_transcription_credits ?? 0}</strong>
          </article>
          <article className="stat-card">
            <span>Plan activo</span>
            <strong>{billing?.has_active_subscription ? "Si" : "No"}</strong>
          </article>
        </div>

        <StatusBanner tone="danger">{error}</StatusBanner>
      </section>

      <section className="feature-grid">
        <article className="feature-card">
          <h2>Transcripcion inmediata</h2>
          <p>Sube un audio de hasta 45 minutos y descarga un ZIP con PDF, DOCX y TXT al terminar.</p>
          <Link className="ghost-link" to="/transcribir">
            Ir a transcribir
          </Link>
        </article>
        <article className="feature-card">
          <h2>Planes y creditos</h2>
          <p>Activa acceso ilimitado por un mes o compra 1 transcripcion individual por uso.</p>
          <Link className="ghost-link" to="/plan">
            Ver pagos
          </Link>
        </article>
      </section>
    </div>
  );
}
