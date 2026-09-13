#!/usr/bin/env python
"""
Launcher para Sistema de Gestión de Préstamos
Inicia el servidor Django y abre el navegador automáticamente
"""
import os
import sys
import subprocess
import webbrowser
import time

def main():
    """Función principal del launcher"""
    try:
        # Cambiar a la carpeta del proyecto
        project_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_dir)
        
        print("=" * 60)
        print("🚀 Sistema de Gestión de Préstamos")
        print("=" * 60)
        print()
        print("📂 Carpeta del proyecto:", project_dir)
        print()
        
        # Verificar que manage.py existe
        if not os.path.exists('manage.py'):
            print("❌ Error: No se encontró manage.py")
            print("   Asegúrate de ejecutar esto desde la carpeta raíz del proyecto")
            input("Presiona Enter para salir...")
            return
        
        # Iniciar Django
        print("🔧 Iniciando servidor Django...")
        print("   Esto puede tomar unos segundos...")
        print()
        
        server_process = subprocess.Popen(
            [sys.executable, 'manage.py', 'runserver'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Esperar a que el servidor inicie
        time.sleep(4)
        
        # Abrir navegador
        print("🌐 Abriendo navegador...")
        webbrowser.open('http://127.0.0.1:8000/')
        
        print()
        print("=" * 60)
        print("✅ Sistema iniciado correctamente!")
        print("=" * 60)
        print()
        print("📱 URL: http://127.0.0.1:8000/")
        print()
        print("💡 Consejos:")
        print("   - La web debería abrirse automáticamente")
        print("   - Si no abre, copia la URL en tu navegador")
        print("   - Deja esta ventana abierta mientras usas el sistema")
        print("   - Para detener, cierra esta ventana")
        print()
        print("=" * 60)
        
        # Mantener el servidor activo
        server_process.wait()
        
    except KeyboardInterrupt:
        print("\n\n⛔ Sistema detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        input("Presiona Enter para salir...")

if __name__ == '__main__':
    main()
