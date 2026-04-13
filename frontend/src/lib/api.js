export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function fetchJson(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await response.json() : null;

  if (!response.ok) {
    throw new Error(payload?.detail || payload?.error || "Ocurrio un error en la solicitud.");
  }

  return payload;
}

export async function fetchWithToken(path, token, options = {}) {
  return fetchJson(path, {
    ...options,
    headers: {
      ...(options.headers || {}),
      Authorization: `Token ${token}`,
    },
  });
}
