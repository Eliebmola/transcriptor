# Transcriptor SaaS

Implementacion base de una plataforma de transcripcion con:

- Backend en Django + Django REST Framework con autenticacion por token.
- Frontend en React.
- Limite de 2 intentos gratis por usuario.
- Plan mensual para transcripciones ilimitadas.
- Pago por uso de 1 transcripcion.
- Exportacion a PDF, TXT y DOCX en un ZIP temporal.

## Estado actual

- El backend ejecutable esta en `backend_temp/`.
- El frontend React esta en `frontend/`.
- La transcripcion ya funciona end-to-end.
- Los archivos se devuelven para descarga inmediata y no se almacenan permanentemente.
- El contador de intentos gratis ya se descuenta correctamente.
- El frontend ahora esta dividido en varias paginas: inicio, acceso, dashboard, transcripcion y plan.
- El backend ya incluye billing con ordenes, webhook y checkout para Mercado Pago.
- Las pruebas gratis tienen limite de 45 minutos por audio.
- El pago por uso cubre 1 audio completo por 1.5 USD.
- El plan mensual cuesta 6 USD.

## Ejecutar backend

```powershell
cd C:\Users\Unimagdalena\Documents\Transcriptor\backend_temp
..\.venv\Scripts\python manage.py migrate
..\.venv\Scripts\python manage.py runserver 127.0.0.1:8000
```

## Ejecutar frontend

```powershell
cd C:\Users\Unimagdalena\Documents\Transcriptor\frontend
npm install
npm run dev
```

## Configuracion de pagos

Variables nuevas en `backend/.env` o `backend/.env.example`:

- `MERCADOPAGO_ACCESS_TOKEN`
- `MERCADOPAGO_PUBLIC_KEY`
- `MERCADOPAGO_WEBHOOK_SECRET`
- `PAID_PLAN_PRICE`
- `PER_USE_PRICE`
- `PER_USE_PRICE_USD`
- `BILLING_CURRENCY`
- `BACKEND_PUBLIC_BASE_URL`
- `FRONTEND_BASE_URL`

Si quieres orientar el checkout hacia PSE, puedes ajustar:

- `MERCADOPAGO_EXCLUDED_PAYMENT_TYPES`
- `MERCADOPAGO_EXCLUDED_PAYMENT_METHODS`
- `MERCADOPAGO_INSTALLMENTS=1`

## Flujo actual

1. El usuario se registra o inicia sesion.
2. El frontend consulta intentos gratis restantes y estado del plan.
3. El usuario puede ir a la pagina del plan y abrir el checkout.
4. El webhook del proveedor actualiza la orden y activa el plan anual o entrega 1 credito por uso.
5. El usuario sube un audio.
6. El backend transcribe y genera PDF, DOCX y TXT.
7. El sistema entrega un ZIP para descarga inmediata.
8. Si el usuario no tiene suscripcion, se consume primero un credito pago y luego un intento gratis.

## Despliegue recomendado

- Frontend: Firebase Hosting
- Backend: Cloud Run con Docker
- Base de datos: Neon Postgres

Guia base: [deployment.md](C:\Users\Unimagdalena\Documents\Transcriptor\docs\deployment.md)

## Guias utiles

- Ejecucion local: [local-run.md](C:\Users\Unimagdalena\Documents\Transcriptor\docs\local-run.md)
- Neon PostgreSQL 17: [neon-postgres-setup.md](C:\Users\Unimagdalena\Documents\Transcriptor\docs\neon-postgres-setup.md)

## Script existente reutilizado

La base funcional actual esta en:

`C:\Users\Unimagdalena\Documents\Enfriamiento Simulado\transcribe_to_pdf.py`

Su logica fue tomada como referencia para crear un servicio reutilizable dentro del backend:

- `backend_temp/transcriptions/services.py`

## IA adicional recomendada

- Deteccion automatica de idioma.
- Correccion y limpieza inteligente del texto.
- Resumen del contenido.
- Titulo sugerido del archivo.
- Identificacion de hablantes.
- Extraccion de puntos clave o tareas.

## Siguiente iteracion natural

1. Integrar pasarela de pagos con webhook.
2. Mover transcripciones pesadas a cola de tareas.
3. Migrar de SQLite a PostgreSQL.
4. Consolidar `backend_temp/` como `backend/` final.
