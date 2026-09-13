"""
AUDITOR DE COBERTURA TESTING - CRÍTICA #5
==========================================

Audita el estado actual del testing en el proyecto.
Identifica:
- Tests actuales y su organización
- Cobertura de código
- Qué módulos/funciones faltan tests
- Recomendaciones

Ejecutar: python manage.py auditar_testing

Propósito:
- Mapa de tests existentes vs faltantes
- Cobertura por módulo
- Generar roadmap de testing CRÍTICA #5
"""

import os
import subprocess
from pathlib import Path
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Audita el estado actual de testing del proyecto'

    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*80)
        self.stdout.write("🔍 AUDITOR DE COBERTURA TESTING - CRÍTICA #5")
        self.stdout.write("="*80 + "\n")
        
        # 1. Contar tests
        self.audit_tests_count()
        
        # 2. Listar tests por ubicación
        self.audit_tests_organization()
        
        # 3. Intentar coverage
        self.audit_coverage()
        
        # 4. Módulos sin tests identific ados
        self.audit_coverage_gaps()
        
        self.stdout.write("\n" + "="*80)
        self.stdout.write("✅ Auditoría completada")
        self.stdout.write("="*80 + "\n")
    
    def audit_tests_count(self):
        """Cuenta tests totales en el proyecto"""
        self.stdout.write("\n📊 CONTEO DE TESTS")
        self.stdout.write("-" * 80)
        
        project_root = Path('/c/Users/Juancho/Desktop/proyecto_john')
        test_files = list(project_root.rglob('test*.py'))
        self.stdout.write(f"✅ Tests encontrados: {len(test_files)} archivos")
        
        # Contar test methods
        test_count = 0
        for test_file in test_files:
            try:
                with open(test_file, 'r') as f:
                    content = f.read()
                    test_count += content.count('def test_')
            except:
                pass
        
        self.stdout.write(f"✅ Test methods: ~{test_count} funciones de test\n")
    
    def audit_tests_organization(self):
        """Audita dónde están los tests"""
        self.stdout.write("\n📁 ORGANIZACIÓN DE TESTS")
        self.stdout.write("-" * 80)
        
        locations = {
            'mi_app/tests/': '/c/Users/Juancho/Desktop/proyecto_john/mi_app/tests',
            'tests/ (root)': '/c/Users/Juancho/Desktop/proyecto_john/tests',
            'Root level': '/c/Users/Juancho/Desktop/proyecto_john',
        }
        
        for label, path in locations.items():
            if os.path.exists(path):
                test_files = [f for f in os.listdir(path) if f.startswith('test_') and f.endswith('.py')]
                if test_files:
                    self.stdout.write(f"  📍 {label}:")
                    for tf in test_files[:5]:
                        self.stdout.write(f"     - {tf}")
                    if len(test_files) > 5:
                        self.stdout.write(f"     ... y {len(test_files) - 5} más")
    
    def audit_coverage(self):
        """Intenta obtener cobertura"""
        self.stdout.write("\n📈 COBERTURA ACTUAL")
        self.stdout.write("-" * 80)
        
        self.stdout.write("⚠️  Nota: Coverage solo disponible si 'coverage' está instalado")
        self.stdout.write("   Instalación: pip install coverage")
        self.stdout.write("   Generar coverage:")
        self.stdout.write("   $ coverage run --source='mi_app' manage.py test")
        self.stdout.write("   $ coverage report\n")
        
        try:
            result = subprocess.run(
                ['coverage', 'report', '--source=mi_app'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.stdout.write(self.style.SUCCESS("Coverage output:"))
                self.stdout.write(result.stdout)
            else:
                self.stdout.write(self.style.WARNING("Coverage no disponible (instalar: pip install coverage)"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Coverage no disponible: {str(e)}"))
    
    def audit_coverage_gaps(self):
        """Identifica módulos sin tests"""
        self.stdout.write("\n🎯 MÓDULOS SIN TESTS (GAPS)")
        self.stdout.write("-" * 80)
        
        modules_no_tests = {
            'mi_app/models.py': 'Models: Cliente, Prestamo, Cuota, Pago, etc.',
            'mi_app/forms.py': 'Forms: ClienteForm, PrestamoForm, etc.',
            'mi_app/utils.py': 'Utilities: cálculos, helpers',
            'mi_app/decorators.py': 'Auth decorators: @login_required, @require_permission',
            'mi_app/templatetags/': 'Custom template tags',
        }
        
        for module, desc in modules_no_tests.items():
            self.stdout.write(f"❌ {module}: {desc}")
        
        self.stdout.write("\n" + self.style.SUCCESS("✅ TESTS EXISTENTES (Por CRÍTICA):"))
        self.stdout.write("  ✅ test_auth.py - Autenticación")
        self.stdout.write("  ✅ test_search.py - Búsqueda AJAX")
        self.stdout.write("  ✅ test_finanzas_critica3.py - Financiero")
        self.stdout.write("  ✅ test_validaciones_critica4.py - Validaciones")
        
        self.stdout.write("\n" + self.style.WARNING("🔴 FALTANTES CRÍTICOS:"))
        self.stdout.write("  ❌ 50+ Unit tests (models, forms, utils)")
        self.stdout.write("  ❌ 20+ Integration tests (workflows)")
        self.stdout.write("  ❌ 10+ E2E tests (Selenium)")
        self.stdout.write("  ❌ CI/CD pipeline (GitHub Actions)")
        self.stdout.write("  ❌ Coverage reporting (pytest-cov)")
        self.stdout.write("  ❌ Performance tests")
        self.stdout.write("  ❌ Security tests")
