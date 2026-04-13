import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <div className="page-stack">
      <section className="hero-panel">
        <div className="hero-main">
          <span className="eyebrow">Transcripcion profesional</span>
          <h1>Sube tu audio y descarga PDF, Word y TXT en un solo ZIP.</h1>
          <p>
            La plataforma procesa archivos de audio, transcribe con IA y entrega los formatos listos
            para descargar. Los archivos no quedan almacenados permanentemente y cada audio puede durar
            hasta 45 minutos.
          </p>
          <div className="cta-row">
            <Link className="primary-link" to="/auth">
              Crear cuenta
            </Link>
            <Link className="ghost-link" to="/plan">
              Ver planes
            </Link>
          </div>
        </div>

        <aside className="hero-aside">
          <strong>Modelo de negocio</strong>
          <p>2 intentos gratis por usuario.</p>
          <p>Pago por uso desde 1.5 USD por transcripcion.</p>
          <p>Plan mensual ilimitado por 6 USD con activacion automatica por pago.</p>
          <p>Descarga inmediata sin almacenamiento permanente de resultados.</p>
        </aside>
      </section>

      <section className="feature-grid">
        <article className="feature-card">
          <h2>Frontend multipagina</h2>
          <p>Inicio, acceso, dashboard, transcripcion y pagos con una navegacion mucho mas clara.</p>
        </article>
        <article className="feature-card">
          <h2>Backend robusto</h2>
          <p>Autenticacion por token, reglas de uso, billing, webhooks y transcripcion temporal.</p>
        </article>
        <article className="feature-card">
          <h2>Flujo operativo simple</h2>
          <p>El usuario sube, transcribe, descarga y el sistema consume prueba gratis, credito o plan.</p>
        </article>
      </section>
    </div>
  );
}
