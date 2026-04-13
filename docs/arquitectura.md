# Arquitectura inicial

## Decision principal

Para este producto conviene empezar con un **monolito modular** y no con microservicios.

### Por que

- El producto esta en etapa inicial.
- Hay un solo flujo de negocio fuerte: registro, limite gratis, pago, transcripcion y descarga.
- Un monolito en capas reduce complejidad operativa y costo.
- Django ya trae autenticacion, admin, ORM y buenas practicas de seguridad.

## Stack recomendado

### Backend

- Python 3.11+
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery para tareas pesadas
- Whisper o `faster-whisper` para transcripcion
- `python-docx` para Word
- `reportlab` para PDF

### Frontend

- React
- Vite
- TypeScript
- React Router
- TanStack Query

## Por que React y no Angular

Para este caso React encaja mejor porque:

- Nos deja avanzar mas rapido en un SaaS pequeno o mediano.
- Se integra muy bien con APIs REST de Django.
- Tiene menos peso estructural inicial que Angular.
- Facilita iterar dashboard, onboarding, pricing y estados de carga.

Angular seria razonable si el proyecto tuviera desde el dia uno un equipo frontend grande, reglas corporativas fuertes o una necesidad muy alta de estructura estricta.

## Modulos del backend

### `accounts`

- Registro e inicio de sesion.
- Recuperacion de contrasena.
- Verificacion de correo.
- Roles basicos: `user`, `admin`.

### `billing`

- Plan gratuito.
- Suscripcion anual.
- Estado de pago.
- Historial de transacciones.
- Webhooks del proveedor de pago.

### `transcriptions`

- Carga de audio.
- Validacion de formato y tamano.
- Cola de procesamiento.
- Generacion de `pdf`, `txt` y `docx`.
- Descarga de archivos.

## Regla de negocio inicial

- Usuario anonimo: no puede transcribir.
- Usuario registrado sin pago: 3 transcripciones gratis de por vida.
- Usuario con suscripcion activa: transcripciones ilimitadas durante 1 ano.
- Usuario con suscripcion vencida: vuelve a quedar bloqueado si ya gasto sus 3 gratis.

## Seguridad minima desde la v1

- Autenticacion con tokens seguros o JWT con refresh corto.
- Hash de contrasenas con configuracion segura de Django.
- CSRF y CORS configurados correctamente.
- Limite de subida por tipo y tamano de archivo.
- Rate limiting para login, registro y transcripcion.
- Antivirus o escaneo basico si luego aceptamos mas tipos de archivo.
- Almacenamiento privado de archivos, nunca publico por URL directa.
- Logs de auditoria para pagos y transcripciones.

## Pagos

Si quieres automatizar acceso anual, **no recomiendo depender de consignaciones manuales a una cuenta** como flujo principal.

### Problemas

- No hay confirmacion automatica confiable.
- Obliga a revision manual.
- Abre espacio a fraude o errores humanos.
- Hace mas dificil activar y renovar suscripciones.

### Recomendacion

Usar un proveedor con webhook de confirmacion de pago y dejar la consignacion manual solo como excepcion administrativa.

## Flujo tecnico

1. El usuario crea cuenta.
2. Sube un audio.
3. El backend verifica si aun tiene intentos gratis o suscripcion activa.
4. Si puede continuar, el archivo se guarda en almacenamiento privado.
5. Se crea un job de transcripcion.
6. Celery procesa el audio y genera `pdf`, `txt` y `docx`.
7. El usuario ve el estado en el dashboard y descarga resultados.

## Integracion del script actual

El script existente ya resuelve:

- Transcripcion con Whisper.
- Limpieza basica del texto.
- Exportacion a PDF.
- Exportacion a TXT.
- Exportacion a DOCX.

La adaptacion necesaria es:

- quitar la capa CLI,
- convertirlo en servicio reutilizable,
- devolver rutas y metadatos,
- capturar errores,
- ejecutarlo en background.
