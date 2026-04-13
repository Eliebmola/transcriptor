# Backend Django

## Ejecutar

```powershell
cd C:\Users\Unimagdalena\Documents\Transcriptor\backend_temp
..\.venv\Scripts\python manage.py migrate
..\.venv\Scripts\python manage.py runserver 127.0.0.1:8000
```

## Endpoints iniciales

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `GET /api/auth/me/`
- `GET /api/billing/status/`
- `POST /api/billing/checkout/`
- `POST /api/billing/webhooks/mercadopago/`
- `POST /api/transcriptions/process/`

## Flujo actual

- El usuario se registra.
- Tiene 2 intentos gratis.
- Las pruebas gratis se validan con un maximo de 45 minutos.
- El pago por uso cubre 1 audio completo por compra.
- Si no tiene suscripcion activa y agota esos intentos, puede usar creditos pagos por transcripcion.
- El plan mensual se cobra con checkout externo del proveedor.
- El webhook activa automaticamente la suscripcion mensual o acredita 1 transcripcion por pago por uso.
- Cada transcripcion devuelve un `.zip` temporal con `pdf`, `txt` y `docx`.
- Los archivos no se almacenan permanentemente.
