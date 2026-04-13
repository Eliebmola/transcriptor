import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "../state/AuthContext";

export function ProtectedRoute({ children }) {
  const { authReady, isAuthenticated } = useAuth();
  const location = useLocation();

  if (!authReady) {
    return <section className="page-card">Cargando sesion...</section>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth" replace state={{ from: location.pathname }} />;
  }

  return children;
}
