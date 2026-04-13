# Neon PostgreSQL 17

## Objetivo

Mover el proyecto desde SQLite local a Neon PostgreSQL 17 para:

- tener una base de datos apta para produccion,
- preparar Cloud Run,
- evitar las limitaciones de SQLite con concurrencia y webhooks.

## Que crear en Neon

1. Iniciar sesion en Neon.
2. Crear un proyecto nuevo.
3. Elegir PostgreSQL 17.
4. Crear la base de datos principal.
5. Abrir `Connect`.
6. Copiar la cadena `DATABASE_URL`.

## Formato esperado

La aplicacion espera una cadena asi:

```env
DATABASE_URL=postgresql://usuario:password@host/dbname?sslmode=require
```

## Donde ponerla

En local:

`C:\Users\Unimagdalena\Documents\Transcriptor\backend\.env`

Reemplaza:

```env
DATABASE_URL=
```

por la cadena real de Neon.

## Verificar conexion

Con la variable puesta:

```powershell
cd C:\Users\Unimagdalena\Documents\Transcriptor\backend_temp
..\.venv\Scripts\python manage.py migrate
..\.venv\Scripts\python manage.py check
```

Si todo sale bien, Django ya estara trabajando sobre PostgreSQL.

## Nota importante

Por ahora no estamos migrando datos reales desde SQLite porque el proyecto sigue en etapa de prueba.

En este punto lo mas seguro es:

1. crear PostgreSQL limpio,
2. correr migraciones,
3. crear usuarios de prueba otra vez si hace falta.
