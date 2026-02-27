# 🚀 Guía de Trabajo: Desarrollo Local vs Producción PythonAnywhere

---

## 🎯 CONTEXTO DEL PROYECTO (IMPORTANTE PARA REANUDAR CONVERSACIONES)

### 📌 **Identificación del Proyecto**
- **Nombre**: Sistema de Gestión de Créditos
- **Propietario**: Juan Carlos (Juancho)
- **Tipo**: Aplicación web Django para gestión financiera
- **GitHub**: https://github.com/juan2007As/Gestion-de-Creditos
- **Producción**: PythonAnywhere (`Gestion-de-Creditos`)

### 🛠️ **Stack Tecnológico**
- **Backend**: Django (Python)
- **Base de Datos**: SQLite (local) / PostgreSQL (producción)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Hosting**: PythonAnywhere
- **Control de Versiones**: Git

### 🎯 **Funcionalidad Principal**
Sistema completo para gestión de créditos que incluye:
- Gestión de clientes y préstamos
- Cálculo de cuotas e intereses
- Sistema de pagos y amortización
- Reportes financieros
- Lista negra de clientes
- Importación desde Excel
- Auditoría completa del sistema

### 👤 **Información del Desarrollador**
- **Usuario**: Juan Carlos
- **Ubicación**: Colombia
- **Proyecto**: Portafolio profesional
- **Contacto**: Desarrollo local en Windows

### 📅 **Estado Actual**
- **Última actualización**: $(date)
- **Versión**: Producción activa
- **Estado**: En desarrollo continuo
- **Flujo**: Local → Git → PythonAnywhere

### ⚠️ **Notas Importantes para Continuidad**
- **Entorno local**: `c:\Users\Juancho\Desktop\Proyectos para portafolio\proyecto_john_produccion`
- **Entorno producción**: PythonAnywhere bash: `(mi-env) ~/Gestion-de-Creditos (main)$`
- **Base de datos**: Se limpia frecuentemente para pruebas
- **Scripts importantes**: `limpiar_db.py`, `generar_plantilla.py`
- **Archivos clave**: `manage.py`, `requirements.txt`, `Plantilla_Maestra_Creditos.xlsx`

---

## 📋 Información General

Este proyecto tiene **DOS ambientes**:

- **🔧 Local**: Desarrollo y pruebas (`c:\Users\Juancho\Desktop\Proyectos para portafolio\proyecto_john_produccion`)
- **🌐 Producción**: PythonAnywhere (`Gestion-de-Creditos`)

### Flujo de Trabajo
1. **Desarrollar/Probar** localmente
2. **Subir cambios** al Git
3. **Importar en PythonAnywhere** para probar en producción

---

## 🖥️ Desarrollo Local (Windows)

### Configuración Inicial
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Variables de Entorno (.env)
Crear archivo `.env` en la raíz del proyecto:
```env
DEBUG=True
SECRET_KEY=django-insecure-test-key-for-development-only-123456789
ALLOWED_HOSTS=localhost,127.0.0.1,testserver
```

### Comandos Django Básicos
```bash
# Ejecutar servidor de desarrollo
python manage.py runserver

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Shell interactivo
python manage.py shell

# Limpiar base de datos (borra datos, mantiene estructura)
python manage.py flush
```

### Scripts de Limpieza de BD
```bash
# Script completo (pregunta confirmación)
python limpiar_db.py

# Script específico de BD
python scripts/limpiar_bd.py

# Script de restauración desde backup vacío
python scripts/restaurar_bd_vacia.py
```

---

## 🌐 Producción PythonAnywhere

### Acceso a Consola
1. Ir a https://www.pythonanywhere.com/
2. Iniciar sesión
3. Pestaña **"Consoles"**
4. Abrir **"Bash console"**

### Navegación y Activación
```bash
# Ir al directorio del proyecto
cd ~/Gestion-de-Creditos

# Activar entorno virtual
source ~/.virtualenvs/tu_entorno_virtual/bin/activate

# Verificar entorno activo
which python
```

### Comandos de Git (Sincronización)
```bash
# Ver estado del repositorio
git status

# Descargar cambios desde GitHub
git pull origin main

# Ver commits recientes
git log --oneline -5

# Ver diferencias con origin
git diff origin/main
```

### Gestión de Base de Datos
```bash
# Backup antes de cambios
cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d_%H%M%S)

# Limpiar base de datos
python limpiar_db.py

# Aplicar migraciones después de pull
python manage.py migrate

# Recargar aplicación web
# Ir a Web tab -> Reload
```

### Monitoreo y Logs
```bash
# Ver logs de error
tail -f /var/log/pythonanywhere/error.log

# Ver logs de acceso
tail -f /var/log/pythonanywhere/access.log

# Ver procesos corriendo
ps aux | grep python

# Ver uso de disco
du -h --max-depth=1
```

### Comandos Útiles de Sistema
```bash
# Ver directorio actual
pwd

# Listar archivos
ls -la

# Ver tamaño de directorios
du -sh *

# Ver procesos Python
ps aux | grep python

# Matar proceso si es necesario
kill -9 PID_DEL_PROCESO
```

---

## 🔄 Sincronización Git

### Desde Local a PythonAnywhere
```bash
# Local - después de cambios
git add .
git commit -m "Descripción del cambio"
git push origin main

# PythonAnywhere - descargar cambios
cd ~/Gestion-de-Creditos
git pull origin main
python manage.py migrate  # Si hay nuevas migraciones
# Reiniciar web app desde Web tab
```

### Verificar Sincronización
```bash
# Ver si hay diferencias
git status
git diff origin/main

# Ver último commit
git log --oneline -1
```

---

## ⚠️ Checklist Antes de Cambios en Producción

- [ ] **Backup de BD**: `cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d_%H%M%S)`
- [ ] **Ver estado del repo**: `git status`
- [ ] **Pull de cambios**: `git pull origin main`
- [ ] **Aplicar migraciones**: `python manage.py migrate`
- [ ] **Verificar que funciona**: Probar funcionalidad crítica
- [ ] **Reload web app**: Desde pestaña Web en PythonAnywhere

---

## 🆘 Solución de Problemas Comunes

### Error: SECRET_KEY no encontrada
```bash
# Verificar variables de entorno
echo $SECRET_KEY

# O crear archivo .env temporal
echo "SECRET_KEY=django-insecure-temp-key" > .env
```

### Error: Modulo Django no encontrado
```bash
# Verificar entorno virtual activo
which python

# Reactivar si es necesario
source ~/.virtualenvs/tu_entorno/bin/activate
```

### Error: Base de datos locked
```bash
# Matar procesos que usen la BD
ps aux | grep sqlite
kill -9 PID_DEL_PROCESO

# O simplemente esperar y reintentar
```

### Error: Puerto ocupado (local)
```bash
# Matar proceso en puerto 8000
netstat -tulpn | grep :8000
kill -9 PID_DEL_PROCESO
```

---

## 📞 Contactos y Recursos

- **PythonAnywhere**: https://www.pythonanywhere.com/
- **Documentación Django**: https://docs.djangoproject.com/
- **Git**: https://git-scm.com/doc

---
*Última actualización: $(date)*