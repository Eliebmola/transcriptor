# Despliegue recomendado

## Arquitectura

- Frontend React en Firebase Hosting.
- Backend Django en Cloud Run usando Docker.
- Base de datos en Neon Postgres.

## Neon Postgres

1. Crear un proyecto en Neon.
2. Copiar la cadena de conexion `DATABASE_URL`.
3. Guardarla en las variables del backend en Cloud Run.

## Backend en Cloud Run

### Variables necesarias

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DATABASE_URL`
- `BACKEND_PUBLIC_BASE_URL`
- `FRONTEND_BASE_URL`
- `MERCADOPAGO_ACCESS_TOKEN`
- `MERCADOPAGO_PUBLIC_KEY`
- `MERCADOPAGO_WEBHOOK_SECRET`

### Despliegue sugerido

```powershell
gcloud run deploy transcriptor-backend ^
  --source C:\Users\Unimagdalena\Documents\Transcriptor\backend_temp ^
  --region us-central1 ^
  --allow-unauthenticated
```

Si vas a desplegar con Docker directamente, usa el `Dockerfile` de `backend_temp/`.

## Frontend en Firebase Hosting

1. En `frontend/`, configurar `VITE_API_BASE_URL` apuntando al backend de Cloud Run.
2. Ejecutar build:

```powershell
cd C:\Users\Unimagdalena\Documents\Transcriptor\frontend
npm run build
```

3. Desplegar:

```powershell
firebase deploy --only hosting
```

## Regla de negocio actual

- 2 pruebas gratis.
- Limite de 45 minutos solo para pruebas gratis.
- Pago por uso: 1.5 USD por 1 audio, sin ese limite.
- Plan mensual: 6 USD.
