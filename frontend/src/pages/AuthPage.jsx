import { useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { StatusBanner } from "../components/StatusBanner";
import { useAuth } from "../state/AuthContext";

const defaultForm = {
  username: "",
  email: "",
  password: "",
};

export function AuthPage() {
  const { login, register, authLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState(defaultForm);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const nextPath = useMemo(() => location.state?.from || "/dashboard", [location.state]);

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setMessage("");

    try {
      if (mode === "register") {
        await register(form.username, form.email, form.password);
        setMessage("Cuenta creada correctamente.");
      } else {
        await login(form.username, form.password);
        setMessage("Sesion iniciada.");
      }
      setForm(defaultForm);
      navigate(nextPath, { replace: true });
    } catch (submitError) {
      setError(submitError.message);
    }
  }

  return (
    <section className="page-card auth-card">
      <div className="section-head">
        <div>
          <span className="eyebrow">Acceso</span>
          <h1>{mode === "register" ? "Crea tu cuenta" : "Inicia sesion"}</h1>
        </div>
        <button
          className="ghost-button"
          type="button"
          onClick={() => setMode((current) => (current === "register" ? "login" : "register"))}
        >
          {mode === "register" ? "Ya tengo cuenta" : "Crear cuenta"}
        </button>
      </div>

      <form className="form-grid" onSubmit={handleSubmit}>
        <label>
          Usuario
          <input name="username" value={form.username} onChange={updateField} required />
        </label>

        {mode === "register" ? (
          <label>
            Correo
            <input name="email" type="email" value={form.email} onChange={updateField} required />
          </label>
        ) : null}

        <label>
          Contrasena
          <input name="password" type="password" value={form.password} onChange={updateField} required />
        </label>

        <button className="primary-button" type="submit" disabled={authLoading}>
          {authLoading ? "Procesando..." : mode === "register" ? "Crear cuenta" : "Entrar"}
        </button>
      </form>

      <StatusBanner tone="success">{message}</StatusBanner>
      <StatusBanner tone="danger">{error}</StatusBanner>
    </section>
  );
}
