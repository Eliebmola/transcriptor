import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { StatusBanner } from "../components/StatusBanner";
import { fetchWithToken } from "../lib/api";
import { useAuth } from "../state/AuthContext";

export function BillingPage() {
  const { token } = useAuth();
  const [searchParams] = useSearchParams();
  const [billing, setBilling] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isStartingCheckout, setIsStartingCheckout] = useState(false);

  useEffect(() => {
    void loadBilling();
  }, []);

  useEffect(() => {
    const paymentStatus = searchParams.get("payment_status");
    if (paymentStatus === "success") {
      setMessage("Pago recibido. El webhook terminara de confirmar la compra en cuanto Mercado Pago notifique el evento.");
    } else if (paymentStatus === "pending") {
      setMessage("Tu pago quedo pendiente. Apenas sea aprobado, el acceso se actualizara automaticamente.");
    } else if (paymentStatus === "failure") {
      setError("El pago no pudo completarse. Puedes intentarlo de nuevo.");
    }
  }, [searchParams]);

  async function loadBilling() {
    try {
      const payload = await fetchWithToken("/api/billing/status/", token);
      setBilling(payload);
      setError("");
    } catch (loadError) {
      setError(loadError.message);
    }
  }

  async function startCheckout(kind) {
    setIsStartingCheckout(true);
    setError("");

    try {
      const order = await fetchWithToken("/api/billing/checkout/", token, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ kind }),
      });
      if (!order.checkout_url) {
        throw new Error("El proveedor no devolvio una URL de pago.");
      }
      window.location.href = order.checkout_url;
    } catch (checkoutError) {
      setError(checkoutError.message);
      setIsStartingCheckout(false);
    }
  }

  return (
    <div className="page-stack">
      <section className="page-card">
        <div className="section-head">
          <div>
            <span className="eyebrow">Planes</span>
            <h1>Pagos y activacion</h1>
          </div>
          <button className="ghost-button" type="button" onClick={() => void loadBilling()}>
            Actualizar estado
          </button>
        </div>

        <div className="plan-grid">
          <article className="plan-card highlight">
            <span className="plan-label">Plan mensual</span>
            <strong>
              {billing?.currency} {billing?.annual_plan_price}
            </strong>
            <p>Referencia comercial: USD {billing?.annual_plan_price_usd}</p>
            <p>Duracion: {billing?.plan_duration_days} dias con transcripciones ilimitadas.</p>
            <p>Proveedor: Mercado Pago Checkout Pro, ideal para pagos locales como PSE.</p>
            <button className="primary-button" type="button" onClick={() => void startCheckout("monthly")} disabled={isStartingCheckout}>
              {isStartingCheckout ? "Redirigiendo..." : "Pagar plan mensual"}
            </button>
          </article>

          <article className="plan-card">
            <span className="plan-label">Pago por uso</span>
            <strong>
              {billing?.currency} {billing?.pay_per_use_price}
            </strong>
            <p>Referencia comercial: USD {billing?.pay_per_use_price_usd}</p>
            <p>Compra 1 credito para 1 transcripcion individual.</p>
            <p>Creditos disponibles: {billing?.paid_transcription_credits ?? 0}</p>
            <button className="ghost-button" type="button" onClick={() => void startCheckout("pay_per_use")} disabled={isStartingCheckout}>
              {isStartingCheckout ? "Redirigiendo..." : "Comprar 1 credito"}
            </button>
          </article>
        </div>

        <div className="plan-grid single-row">
          <article className="plan-card">
            <span className="plan-label">Estado actual</span>
            <strong>{billing?.has_active_subscription ? "Plan activo" : "Sin plan activo"}</strong>
            <p>
              {billing?.active_subscription_end
                ? `Vence el ${new Date(billing.active_subscription_end).toLocaleDateString()}.`
                : "Puedes activar el plan cuando quieras."}
            </p>
            <p>El checkout puede ofrecer PSE segun los medios habilitados en tu cuenta de Mercado Pago.</p>
          </article>
        </div>

        <StatusBanner tone="success">{message}</StatusBanner>
        <StatusBanner tone="danger">{error}</StatusBanner>
      </section>
    </div>
  );
}
