@echo off
REM Sistema de Gestión de Préstamos - Iniciador Rápido
REM Este archivo inicia Django y abre el navegador

echo.
echo ============================================================
echo    Sistema de Gestión de Préstamos
echo ============================================================
echo.

REM Obtener la carpeta actual
cd /d "%~dp0"

REM Verificar que manage.py existe
if not exist manage.py (
    echo Error: No se encontró manage.py
    echo Asegúrate de ejecutar esto desde la carpeta raíz
    pause
    exit /b 1
)

echo 🚀 Iniciando servidor Django...
echo.

REM Iniciar Django en otra ventana
start "Django Server - Gestión de Préstamos" python manage.py runserver

REM Esperar a que inicie
timeout /t 3 /nobreak

REM Abrir navegador
echo 🌐 Abriendo navegador...
start http://127.0.0.1:8000/

echo.
echo ============================================================
echo ✅ Sistema iniciado correctamente
echo ============================================================
echo.
echo URL: http://127.0.0.1:8000/
echo.
echo Para detener, cierra la ventana del servidor Django.
echo.
pause
