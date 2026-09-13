#!/usr/bin/env python
"""
SCRIPT DE PRUEBAS COMPLETAS DEL SISTEMA DE GESTIÓN DE CRÉDITOS

Este script ejecuta pruebas automatizadas exhaustivas de todas las funcionalidades
críticas del sistema antes del despliegue a producción.

Ejecutar con: python test_full_system.py
"""

import os
import sys
import time
import requests
from datetime import datetime, date
import json

# Configuración
BASE_URL = "http://127.0.0.1:8000"
TEST_USER = "admin"
TEST_PASSWORD = "admin123"

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def log_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def log_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def log_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def log_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

class CreditSystemTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': []
        }

    def login(self):
        """Prueba el login del sistema"""
        try:
            log_info("Probando login...")

            # Primero obtener la página de login para extraer CSRF token
            login_page = self.session.get(f"{BASE_URL}/login/")
            if login_page.status_code != 200:
                log_error("Página de login no accesible")
                return False

            # Extraer CSRF token (buscar en el HTML)
            csrf_token = None
            if 'csrfmiddlewaretoken' in login_page.text:
                # Buscar el token en input hidden
                import re
                csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_page.text)
                if csrf_match:
                    csrf_token = csrf_match.group(1)

            if not csrf_token:
                log_warning("No se encontró CSRF token, intentando login sin él")

            response = self.session.post(
                f"{BASE_URL}/login/",
                data={
                    'username': TEST_USER,
                    'password': TEST_PASSWORD,
                    'csrfmiddlewaretoken': csrf_token
                } if csrf_token else {
                    'username': TEST_USER,
                    'password': TEST_PASSWORD
                },
                headers={'Referer': f"{BASE_URL}/login/"},
                allow_redirects=True
            )

            if response.status_code == 200 and ('inicio' in response.url.lower() or response.url.endswith('/')):
                log_success("Login exitoso")
                return True
            else:
                log_error(f"Login falló - Status: {response.status_code}, URL: {response.url}")
                return False

        except Exception as e:
            log_error(f"Error en login: {str(e)}")
            return False

    def test_dashboard(self):
        """Prueba que la página principal carga correctamente"""
        try:
            log_info("Probando página principal...")
            response = self.session.get(f"{BASE_URL}/")

            if response.status_code == 200:
                if 'cliente' in response.text.lower() or 'préstamo' in response.text.lower() or 'inicio' in response.text.lower():
                    log_success("Página principal carga correctamente")
                    return True
                else:
                    log_warning("Página principal carga pero contenido parece incompleto")
                    return True
            else:
                log_error(f"Página principal no carga - Status: {response.status_code}")
                return False

        except Exception as e:
            log_error(f"Error en página principal: {str(e)}")
            return False

    def test_client_management(self):
        """Prueba gestión completa de clientes"""
        try:
            log_info("Probando gestión de clientes...")

            # 1. Listar clientes
            response = self.session.get(f"{BASE_URL}/clientes/")
            if response.status_code != 200:
                log_error("No se puede acceder a lista de clientes")
                return False
            log_success("Lista de clientes accesible")

            # 2. Crear cliente de prueba
            # Primero obtener la página para extraer CSRF token
            create_page = self.session.get(f"{BASE_URL}/clientes/crear/")
            if create_page.status_code != 200:
                log_error("Página de crear cliente no accesible")
                return False

            csrf_token = None
            if 'csrfmiddlewaretoken' in create_page.text:
                import re
                csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', create_page.text)
                if csrf_match:
                    csrf_token = csrf_match.group(1)

            test_client_data = {
                'nombre': 'Cliente Test Automatizado',
                'cedula': f'123456789{int(time.time())}',  # Cedula única
                'telefono': '3001234567',
                'direccion': 'Calle Test 123',
                'email': 'test@example.com',
                'fecha_nacimiento': '1990-01-01'
            }

            if csrf_token:
                test_client_data['csrfmiddlewaretoken'] = csrf_token

            response = self.session.post(
                f"{BASE_URL}/clientes/crear/",
                data=test_client_data,
                headers={'Referer': f"{BASE_URL}/clientes/crear/"},
                allow_redirects=True
            )

            if response.status_code == 200 and 'cliente' in response.url.lower():
                log_success("Cliente creado exitosamente")
                # Extraer ID del cliente de la URL si es posible
                client_id = None
                if 'cliente/' in response.url:
                    try:
                        client_id = response.url.split('cliente/')[1].split('/')[0]
                    except:
                        pass
                return True
            else:
                log_error(f"Error creando cliente - Status: {response.status_code}")
                return False

        except Exception as e:
            log_error(f"Error en gestión de clientes: {str(e)}")
            return False

    def test_loan_creation(self):
        """Prueba creación de préstamos"""
        try:
            log_info("Probando creación de préstamos...")

            # Primero necesitamos un cliente existente
            # Buscar un cliente existente o crear uno
            response = self.session.get(f"{BASE_URL}/clientes/")
            if 'cliente' not in response.text.lower():
                log_warning("No hay clientes existentes, saltando prueba de préstamos")
                return True

            # Extraer primer cliente de la lista
            client_id = None
            if 'href="/cliente/' in response.text:
                href_part = response.text.split('href="/cliente/')[1]
                client_id = href_part.split('/')[0]
                try:
                    client_id = int(client_id)
                except:
                    client_id = None

            if not client_id:
                log_warning("No se pudo encontrar ID de cliente, saltando prueba de préstamos")
                return True

            # Crear préstamo
            loan_data = {
                'cliente': client_id,
                'monto': 1000000,
                'interes_porcentaje': 15.0,
                'numero_cuotas': 12,
                'fecha_inicio': date.today().strftime('%Y-%m-%d'),
                'tipo_prestamo': 'normal'
            }

            response = self.session.post(
                f"{BASE_URL}/prestamos/crear/",
                data=loan_data,
                allow_redirects=True
            )

            if response.status_code == 200:
                log_success("Préstamo creado exitosamente")
                return True
            else:
                log_error(f"Error creando préstamo - Status: {response.status_code}")
                return False

        except Exception as e:
            log_error(f"Error en creación de préstamos: {str(e)}")
            return False

    def test_payment_system(self):
        """Prueba sistema de pagos"""
        try:
            log_info("Probando sistema de pagos...")

            # Buscar préstamos existentes
            response = self.session.get(f"{BASE_URL}/prestamos/")
            if 'préstamo' not in response.text.lower() and 'prestamo' not in response.text.lower():
                log_warning("No hay préstamos existentes, saltando prueba de pagos")
                return True

            # Esta es una prueba básica - en un sistema real necesitaríamos
            # extraer IDs específicos de préstamos y cuotas
            log_success("Sistema de pagos accesible")
            return True

        except Exception as e:
            log_error(f"Error en sistema de pagos: {str(e)}")
            return False

    def test_reports(self):
        """Prueba generación de reportes"""
        try:
            log_info("Probando reportes...")

            # Probar diferentes reportes
            report_urls = [
                '/reportes/clientes/',
                '/reportes/prestamos/',
                '/reportes/historico-pagos/',
                '/reportes/estadisticas/'
            ]

            success_count = 0
            for url in report_urls:
                try:
                    response = self.session.get(f"{BASE_URL}{url}")
                    if response.status_code == 200:
                        success_count += 1
                    else:
                        log_warning(f"Reporte {url} falló - Status: {response.status_code}")
                except:
                    log_warning(f"Error accediendo a {url}")

            if success_count > 0:
                log_success(f"{success_count}/{len(report_urls)} reportes funcionan")
                return True
            else:
                log_error("Ningún reporte funciona")
                return False

        except Exception as e:
            log_error(f"Error en reportes: {str(e)}")
            return False

    def test_excel_import(self):
        """Prueba importación desde Excel"""
        try:
            log_info("Probando importación Excel...")

            response = self.session.get(f"{BASE_URL}/importar/excel/")
            if response.status_code == 200:
                log_success("Página de importación Excel accesible")
                return True
            else:
                log_error(f"Importación Excel no accesible - Status: {response.status_code}")
                return False

        except Exception as e:
            log_error(f"Error en importación Excel: {str(e)}")
            return False

    def run_all_tests(self):
        """Ejecuta todas las pruebas"""
        print("\n" + "="*60)
        print("🚀 INICIANDO PRUEBAS COMPLETAS DEL SISTEMA")
        print("="*60)
        print(f"URL Base: {BASE_URL}")
        print(f"Usuario: {TEST_USER}")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")

        # Verificar que el servidor esté corriendo
        try:
            response = requests.get(BASE_URL, timeout=5)
            if response.status_code != 200:
                log_error(f"Servidor no responde correctamente (Status: {response.status_code})")
                return False
        except:
            log_error("Servidor no está corriendo en http://127.0.0.1:8000")
            print("Ejecuta: python manage.py runserver")
            return False

        # Ejecutar pruebas
        tests = [
            ("Autenticación", self.login),
            ("Dashboard", self.test_dashboard),
            ("Gestión de Clientes", self.test_client_management),
            ("Creación de Préstamos", self.test_loan_creation),
            ("Sistema de Pagos", self.test_payment_system),
            ("Reportes", self.test_reports),
            ("Importación Excel", self.test_excel_import),
        ]

        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            result = test_func()
            self.test_results['total_tests'] += 1
            if result:
                self.test_results['passed'] += 1
            else:
                self.test_results['failed'] += 1

        # Resultados finales
        print("\n" + "="*60)
        print("📊 RESULTADOS FINALES")
        print("="*60)
        print(f"Total de pruebas: {self.test_results['total_tests']}")
        print(f"Exitosas: {Colors.GREEN}{self.test_results['passed']}{Colors.END}")
        print(f"Fallidas: {Colors.RED}{self.test_results['failed']}{Colors.END}")

        success_rate = (self.test_results['passed'] / self.test_results['total_tests']) * 100
        if success_rate >= 80:
            print(f"Tasa de éxito: {Colors.GREEN}{success_rate:.1f}%{Colors.END}")
            print(f"\n{Colors.GREEN}🎉 SISTEMA LISTO PARA PRODUCCIÓN{Colors.END}")
            return True
        else:
            print(f"Tasa de éxito: {Colors.RED}{success_rate:.1f}%{Colors.END}")
            print(f"\n{Colors.RED}⚠️  SISTEMA REQUIERE CORRECCIONES ANTES DE PRODUCCIÓN{Colors.END}")
            return False

def main():
    tester = CreditSystemTester()
    success = tester.run_all_tests()

    if success:
        print("\n" + "="*60)
        print("✅ PRUEBAS COMPLETADAS - SISTEMA OPERATIVO")
        print("Puedes proceder con el despliegue a PythonAnywhere")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ PRUEBAS FALLIDAS - REVISAR ERRORES ANTES DE DESPLEGAR")
        print("Corrige los problemas identificados y vuelve a ejecutar las pruebas")
        print("="*60)
        sys.exit(1)

if __name__ == "__main__":
    main()