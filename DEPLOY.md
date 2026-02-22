# Guía de despliegue - Proyecto John (Gestor de Préstamos)

**Entorno:** Producción local que se sube al servidor  
**Última actualización:** Febrero 2026

---

## 0. Migración desde versión anterior (variables en código)

Si tenías credenciales en `settings.py`, ahora van en `.env`. Agrega a tu `.env`:

```
DB_PASSWORD=tu-password-postgresql
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
BACKUP_RECIPIENT_EMAIL=email-destino@ejemplo.com
```

**Local (DEBUG=True):** Con SQLite no necesitas `DB_*`. Sin `EMAIL_HOST_PASSWORD` se usa consola para correos.

---

## 1. Requisitos previos

- Python 3.10+
- PostgreSQL (cuando `DEBUG=False`)
- Variables de entorno configuradas

---

## 2. Configuración de variables de entorno

### Crear archivo `.env`

Copia `.env.example` a `.env` y completa los valores:

```bash
cp .env.example .env
# Editar .env con tus valores reales
```

### Variables obligatorias

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta Django | Cadena larga aleatoria |
| `DEBUG` | Modo debug | `True` (local) / `False` (servidor) |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1,midominio.com` |

### Variables para servidor (cuando `DEBUG=False`)

| Variable | Descripción |
|----------|-------------|
| `DB_NAME` | Nombre base de datos PostgreSQL |
| `DB_USER` | Usuario PostgreSQL |
| `DB_PASSWORD` | Contraseña PostgreSQL |
| `DB_HOST` | Host (ej. `localhost`) |
| `DB_PORT` | Puerto (default `5432`) |
| `EMAIL_HOST_USER` | Email para enviar (Gmail, etc.) |
| `EMAIL_HOST_PASSWORD` | App password del email |
| `BACKUP_RECIPIENT_EMAIL` | Email destino de backups |

### Variables opcionales

| Variable | Default | Descripción |
|----------|---------|-------------|
| `LANGUAGE_CODE` | `es-co` | Idioma |
| `TIME_ZONE` | `America/Bogota` | Zona horaria |

---

## 3. Pasos de despliegue en el servidor

### 3.1 Subir el proyecto

```bash
# Clonar o subir archivos al servidor
git clone <repo> /ruta/proyecto_john
cd /ruta/proyecto_john
```

### 3.2 Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
# o: venv\Scripts\activate  # Windows
```

### 3.3 Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3.4 Configurar `.env` en el servidor

```bash
# Crear .env con valores del servidor
# NUNCA commitear .env con credenciales reales
nano .env
```

Asegurar que `DEBUG=False` y las variables de BD/email estén definidas.

### 3.5 Base de datos

```bash
# PostgreSQL debe estar instalado y corriendo
# Crear base de datos y usuario si no existen

python manage.py migrate
python manage.py createsuperuser  # Si es la primera vez
```

### 3.6 Archivos estáticos

```bash
python manage.py collectstatic --noinput
```

### 3.7 Ejecutar

```bash
# Desarrollo
python manage.py runserver 0.0.0.0:8000

# Producción (con Gunicorn, por ejemplo)
gunicorn proyecto_john.wsgi:application --bind 0.0.0.0:8000
```

---

## 4. Verificación post-despliegue

- [ ] Login funciona
- [ ] Importar clientes desde Excel
- [ ] Registrar un pago
- [ ] Generar reportes
- [ ] Backups (si está configurado email)

---

## 5. Notas de seguridad

1. **Nunca** subir `.env` al repositorio (está en `.gitignore`)
2. Usar contraseñas fuertes para `SECRET_KEY` y `DB_PASSWORD`
3. En servidor, `DEBUG=False` siempre
4. Configurar `ALLOWED_HOSTS` con el dominio real
