import { Link, NavLink } from "react-router-dom";

import { useAuth } from "../state/AuthContext";

export function AppLayout({ children }) {
  const { isAuthenticated, logout } = useAuth();

  return (
    <div className="app-shell">
      <header className="topbar">
        <Link className="brand" to="/">
          <span className="brand-mark">T</span>
          <div>
            <strong>Transcriptor</strong>
            <span>SaaS de transcripcion</span>
          </div>
        </Link>

        <nav className="nav">
          <NavLink to="/">Inicio</NavLink>
          <NavLink to="/dashboard">Dashboard</NavLink>
          <NavLink to="/transcribir">Transcribir</NavLink>
          <NavLink to="/plan">Plan</NavLink>
        </nav>

        <div className="topbar-actions">
          {isAuthenticated ? (
            <button className="ghost-button" type="button" onClick={logout}>
              Cerrar sesion
            </button>
          ) : (
            <Link className="primary-link" to="/auth">
              Entrar
            </Link>
          )}
        </div>
      </header>

      <div className="page-shell">{children}</div>
    </div>
  );
}
