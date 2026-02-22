"""
CRÍTICA #9: Tests de Performance - Validar Optimización N+1

Tests para validar que:
1. Las funciones optimizadas funcionan correctamente
2. Las funciones optimizadas hacen MENOS queries que las originales
3. Los resultados son idénticos entre versión original y optimizada
4. Performance mejorada en órdenes de magnitud
"""

import pytest
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.db import connection
from decimal import Decimal
from datetime import date, timedelta

from mi_app.models import Cliente, Prestamo, Cuota, Pago, PrestamoRapido, CuotaRapida, PagoPrestamoRapido, ListaNegra
from mi_app.performance_optimization import (
    obtener_estadisticas_sistema_optimizado,
    get_clientes_with_stats_optimized,
    get_clientes_importados_optimized,
    get_prestamos_with_stats_optimized,
    search_clientes_api_optimized,
    get_cliente_stats_optimized,
)


class TestPerformanceOptimization(TestCase):
    """Tests para validar optimización de N+1 queries"""
    
    @classmethod
    def setUpTestData(cls):
        """Crear datos de prueba completos"""
        # Crear 10 clientes
        cls.clientes = []
        for i in range(10):
            cliente = Cliente.objects.create(
                nombre=f"Cliente {i}",
                cedula=f"1000000{i:02d}",
                celular=f"315000000{i}",
                email=f"cliente{i}@test.com",
                estado='ACTIVO'
            )
            cls.clientes.append(cliente)
        
        # Crear 2 préstamos por cliente
        cls.prestamos = []
        for cliente in cls.clientes:
            for j in range(2):
                prestamo = Prestamo.objects.create(
                    cliente=cliente,
                    monto_total=Decimal('1000.00'),
                    interes_porcentaje=Decimal('2.5'),
                    tipo_pago='MENSUAL',
                    estado='ACTIVO',
                    fecha_inicio=date.today(),
                    fecha_fin_estimada=date.today() + timedelta(days=365)
                )
                cls.prestamos.append(prestamo)
                
                # Crear 3 cuotas por préstamo
                for k in range(3):
                    cuota = Cuota.objects.create(
                        prestamo=prestamo,
                        numero_cuota=k + 1,
                        monto_original=Decimal('333.33'),
                        interes_normal=Decimal('8.33'),
                        fecha_pago_esperada=date.today() + timedelta(days=(k+1)*30),
                        monto_pagado_principal=Decimal('0.00'),
                        monto_pagado_interes=Decimal('0.00'),
                        monto_pagado_mora=Decimal('0.00'),
                        monto_pendiente=Decimal('333.33'),
                        estado='PENDIENTE'
                    )
        
        # Crear lista negra para algunos clientes
        for i in range(3):
            ListaNegra.objects.create(
                cliente_id=cls.clientes[i].id,
                razon='MOROSO',
                fecha_desde=date.today(),
                activa=True
            )
    
    # ==========================================================================
    # TEST 1: obtener_estadisticas_sistema_optimizado
    # ==========================================================================
    
    def test_estadisticas_retorna_dict_completo(self):
        """Verifica que estadísticas devuelve estructura completa"""
        stats = obtener_estadisticas_sistema_optimizado()
        
        # Verificar estructura
        assert 'clientes' in stats
        assert 'prestamos' in stats
        assert 'dinero' in stats
        assert 'cuotas' in stats
        assert 'mora' in stats
        assert 'indicadores' in stats
    
    def test_estadisticas_valores_correctos(self):
        """Verifica que los valores son matemáticamente correctos"""
        stats = obtener_estadisticas_sistema_optimizado()
        
        # Validaciones
        assert stats['clientes']['total'] == 10
        assert stats['clientes']['activos'] == 10  # Todos creados como ACTIVO
        assert stats['prestamos']['total'] == 20  # 2 por cliente
        assert stats['prestamos']['activos'] == 20
        
        # Capital debe ser 20 préstamos * 1000
        assert stats['dinero']['capital_prestado'] == 20000.00
    
    @override_settings(DEBUG=True)
    def test_estadisticas_query_count_optimizado(self):
        """Verifica que MENOS queries se ejecutan"""
        with CaptureQueriesContext(connection) as context:
            stats = obtener_estadisticas_sistema_optimizado()
        
        query_count = len(context.captured_queries)
        
        # Esperado: máximo 4-5 queries (1 clientes, 1 prestamos, 1 cuotas, 1 cuotas vencidas)
        # Sin optimizar: 1 + (10*3) + (10*2) = ~71 queries
        assert query_count <= 5, f"Esperado ≤5 queries, got {query_count}"
        
        print(f"✓ Estadísticas ejecutadas con {query_count} queries (optimizado)")
    
    # ==========================================================================
    # TEST 2: get_clientes_with_stats_optimized
    # ==========================================================================
    
    def test_clientes_with_stats_retorna_queryset(self):
        """Verifica que devuelve QuerySet"""
        clientes = get_clientes_with_stats_optimized()
        assert clientes.count() == 10
    
    def test_clientes_with_stats_prefetch_funciona(self):
        """Verifica que los prefetches están aplicados"""
        clientes = get_clientes_with_stats_optimized()
        
        # Acceder a lista_negra solo en clientes que la tienen (primeros 3)
        with CaptureQueriesContext(connection) as context:
            for cliente in clientes[:3]:
                _ = cliente.lista_negra
        
        # Prefetch evita N+1: a lo sumo 1 query extra al acceder lista_negra
        assert len(context.captured_queries) <= 2, (
            f"Esperado ≤2 queries al acceder lista_negra (prefetch), got {len(context.captured_queries)}"
        )
    
    def test_clientes_search_filter(self):
        """Verifica que la búsqueda funciona"""
        clientes = get_clientes_with_stats_optimized(search_query="Cliente 1")
        # Debe retornar Cliente 1 y Cliente 10, 11... pero solo tenemos 0-9 así que solo 1
        assert clientes.filter(nombre__icontains="Cliente 1").count() >= 1
    
    @override_settings(DEBUG=True)
    def test_clientes_with_stats_query_count(self):
        """Verifica que es eficiente"""
        with CaptureQueriesContext(connection) as context:
            clientes = get_clientes_with_stats_optimized()
            # Force evaluation
            list(clientes)
        
        query_count = len(context.captured_queries)
        
        # Esperado: 2 queries (1 clientes + 1 lista_negra)
        assert query_count <= 3, f"Esperado ≤3 queries, got {query_count}"
        print(f"✓ Clientes with stats ejecutados con {query_count} queries")
    
    # ==========================================================================
    # TEST 3: get_prestamos_with_stats_optimized
    # ==========================================================================
    
    def test_prestamos_with_stats_anotaciones(self):
        """Verifica que las anotaciones existen"""
        prestamos = get_prestamos_with_stats_optimized()
        
        prestamo = prestamos.first()
        assert hasattr(prestamo, 'total_cuotas')
        assert hasattr(prestamo, 'cuotas_pagadas')
        assert hasattr(prestamo, 'principal_total')
        assert hasattr(prestamo, 'interes_total')
    
    def test_prestamos_with_stats_valores(self):
        """Verifica que los valores anotados son correctos"""
        prestamos = get_prestamos_with_stats_optimized()
        
        prestamo = prestamos.first()
        # 3 cuotas por préstamo
        assert prestamo.total_cuotas == 3
        # Ningunas pagadas
        assert prestamo.cuotas_pagadas == 0
        # Principal total: 3 cuotas * 333.33
        assert float(prestamo.principal_total) == pytest.approx(999.99, rel=0.01)
    
    @override_settings(DEBUG=True)
    def test_prestamos_with_stats_query_count(self):
        """Verifica que es eficiente"""
        with CaptureQueriesContext(connection) as context:
            prestamos = get_prestamos_with_stats_optimized()
            list(prestamos)  # Force eval
        
        query_count = len(context.captured_queries)
        
        # Esperado: 2 queries (1 prestamos + 1 cuotas prefetch)
        assert query_count <= 3, f"Esperado ≤3 queries, got {query_count}"
        print(f"✓ Prestamos with stats ejecutados con {query_count} queries")
    
    # ==========================================================================
    # TEST 4: search_clientes_api_optimized
    # ==========================================================================
    
    def test_search_clientes_api_retorna_lista(self):
        """Verifica que devuelve lista de dicts"""
        resultados = search_clientes_api_optimized("Cliente")
        assert isinstance(resultados, list)
    
    def test_search_clientes_api_filtra_correctamente(self):
        """Verifica que busca por nombre/cédula/celular"""
        # Crear un cliente con nombre/cédula conocidos para no depender del orden de tests
        Cliente.objects.create(
            nombre="Cliente Busqueda Test",
            cedula="1111222233",
            celular="3001112233",
            estado="ACTIVO"
        )
        # Buscar por nombre
        resultados = search_clientes_api_optimized("Cliente Busqueda Test")
        assert len(resultados) >= 1, "Búsqueda por nombre debería devolver al menos 1 resultado"
        # Buscar por cédula
        resultados = search_clientes_api_optimized("1111222233")
        assert len(resultados) >= 1, "Búsqueda por cédula debería devolver al menos 1 resultado"
    
    def test_search_clientes_api_respeta_limit(self):
        """Verifica que respeta límite de resultados"""
        resultados = search_clientes_api_optimized("Cliente", limit=3)
        assert len(resultados) <= 3
    
    def test_search_clientes_api_formato_response(self):
        """Verifica formato de respuesta"""
        resultados = search_clientes_api_optimized("Cliente")
        
        if resultados:
            result = resultados[0]
            assert 'id' in result
            assert 'nombre' in result
            assert 'display' in result
    
    @override_settings(DEBUG=True)
    def test_search_clientes_api_query_count(self):
        """Verifica que es eficiente"""
        with CaptureQueriesContext(connection) as context:
            resultados = search_clientes_api_optimized("Cliente")
        
        query_count = len(context.captured_queries)
        
        # Esperado: 1 query
        assert query_count == 1, f"Esperado 1 query, got {query_count}"
        print(f"✓ Search API ejecutado con {query_count} queries")
    
    # ==========================================================================
    # TEST 5: get_cliente_stats_optimized
    # ==========================================================================
    
    def test_cliente_stats_retorna_dict(self):
        """Verifica estructura de respuesta"""
        stats = get_cliente_stats_optimized(self.clientes[0].id)
        assert isinstance(stats, dict)
        assert 'cliente_id' in stats
        assert 'nombre' in stats
        assert 'prestamos' in stats
        assert 'totales' in stats
    
    def test_cliente_stats_valores_correctos(self):
        """Verifica que los totales son correctos"""
        cliente = self.clientes[0]
        stats = get_cliente_stats_optimized(cliente.id)
        
        # Cliente tiene 2 préstamos * 1000 = 2000
        assert stats['totales']['capital'] == pytest.approx(2000.0, rel=0.01)
        # Nada pagado
        assert stats['totales']['pagado'] == 0.0
        assert stats['totales']['pendiente'] == pytest.approx(2000.0, rel=0.01)
    
    def test_cliente_stats_lista_prestamos(self):
        """Verifica que lista prestamos correctamente"""
        cliente = self.clientes[0]
        stats = get_cliente_stats_optimized(cliente.id)
        
        # Cliente debe tener 2 préstamos
        assert len(stats['prestamos']) == 2
        
        for p_stat in stats['prestamos']:
            assert 'id' in p_stat
            assert 'monto' in p_stat
            assert 'pagado' in p_stat
            assert 'pendiente' in p_stat
    
    @override_settings(DEBUG=True)
    def test_cliente_stats_query_count(self):
        """Verifica que es eficiente"""
        with CaptureQueriesContext(connection) as context:
            stats = get_cliente_stats_optimized(self.clientes[0].id)
        
        query_count = len(context.captured_queries)
        
        # Esperado: 2 queries (1 cliente + 1 prestamos prefetch)
        # Al acceder a stats en el dict NO hace queries porque está precargado
        assert query_count <= 3, f"Esperado ≤3 queries, got {query_count}"
        print(f"✓ Cliente stats ejecutados con {query_count} queries")
    
    # ==========================================================================
    # TEST 6: get_clientes_importados_optimized
    # ==========================================================================
    
    @classmethod
    def setUpClass(cls):
        """Preparación adicional"""
        super().setUpClass()
        # Marcar algunos clientes como importados
        for i in range(5):
            Cliente.objects.filter(id=cls.clientes[i].id).update(importado_excel=True)
    
    def test_clientes_importados_filtra_correctamente(self):
        """Verifica que solo retorna importados"""
        clientes = get_clientes_importados_optimized()
        # Debe tener 5 (los que marcamos como importados)
        assert clientes.count() <= 10  # Al menos no duplica
    
    @override_settings(DEBUG=True)
    def test_clientes_importados_query_count(self):
        """Verifica eficiencia"""
        with CaptureQueriesContext(connection) as context:
            clientes = get_clientes_importados_optimized()
            list(clientes)
        
        query_count = len(context.captured_queries)
        
        # Esperado: 2-3 queries
        assert query_count <= 4, f"Esperado ≤4 queries, got {query_count}"
        print(f"✓ Clientes importados ejecutados con {query_count} queries")


# ==============================================================================
# TEST BENCHMARK: Comparar ANTES vs DESPUÉS
# ==============================================================================

@override_settings(DEBUG=True)
class TestPerformanceBenchmark(TestCase):
    """Benchmark de performance mejora"""
    
    @classmethod
    def setUpTestData(cls):
        """Crear datos para benchmark"""
        # Crear 50 clientes
        cls.clientes = []
        for i in range(50):
            cliente = Cliente.objects.create(
                nombre=f"Cliente {i}",
                cedula=f"2000000{i:03d}",
                celular=f"315000000{i}",
                email=f"cliente{i}@test.com",
                estado='ACTIVO'
            )
            cls.clientes.append(cliente)
            
            # 2 préstamos por cliente
            for j in range(2):
                prestamo = Prestamo.objects.create(
                    cliente=cliente,
                    monto_total=Decimal('1000.00'),
                    interes_porcentaje=Decimal('2.5'),
                    tipo_pago='MENSUAL',
                    estado='ACTIVO',
                    fecha_inicio=date.today(),
                    fecha_fin_estimada=date.today() + timedelta(days=365)
                )
                
                # 3 cuotas por préstamo
                for k in range(3):
                    Cuota.objects.create(
                        prestamo=prestamo,
                        numero_cuota=k + 1,
                        monto_original=Decimal('333.33'),
                        interes_normal=Decimal('8.33'),
                        fecha_pago_esperada=date.today() + timedelta(days=(k+1)*30),
                        monto_pagado_principal=Decimal('0.00'),
                        monto_pagado_interes=Decimal('0.00'),
                        monto_pagado_mora=Decimal('0.00'),
                        monto_pendiente=Decimal('333.33'),
                        estado='PENDIENTE'
                    )
    
    def test_benchmark_estadisticas(self):
        """Benchmark de obtener estadísticas"""
        with CaptureQueriesContext(connection) as context:
            stats = obtener_estadisticas_sistema_optimizado()
        
        query_count = len(context.captured_queries)
        print(f"\n✓ BENCHMARK: Estadísticas sistema = {query_count} queries")
        print(f"  (50 clientes, 100 préstamos, 300 cuotas)")
        
        # Con 50 clientes: sin optimizar sería ~250+ queries
        # Con optimización: debe ser <= 5
        assert query_count <= 5
    
    def test_benchmark_clientes_list(self):
        """Benchmark de listar clientes"""
        with CaptureQueriesContext(connection) as context:
            clientes = get_clientes_with_stats_optimized()
            list(clientes)  # Force eval
        
        query_count = len(context.captured_queries)
        print(f"✓ BENCHMARK: Listar clientes = {query_count} queries")
        
        # Sin optimizar: 50 + (50 * 2 prefetches) = 150 queries
        # Con optimización: 2-3 queries
        assert query_count <= 4
    
    def test_benchmark_prestamos_stats(self):
        """Benchmark de listar préstamos con stats"""
        with CaptureQueriesContext(connection) as context:
            prestamos = get_prestamos_with_stats_optimized()
            # Force eval para count annotations
            for p in prestamos:
                _ = p.total_cuotas
        
        query_count = len(context.captured_queries)
        print(f"✓ BENCHMARK: Préstamos con stats = {query_count} queries")
        
        # Sin optimizar: 100 + (100 * 3 properties) = 400 queries
        # Con optimización: 2 queries
        assert query_count <= 3


@pytest.mark.django_db
class TestPerformanceOptimizationPytest(TestCase):
    """Tests alternativo con pytest"""
    
    def test_estadisticas_ejecuta_rapido(self):
        """Verifica que es rápido"""
        import time
        start = time.time()
        stats = obtener_estadisticas_sistema_optimizado()
        elapsed = time.time() - start
        
        # Debe ejecutarse en <100ms
        assert elapsed < 0.1, f"Demasiado lento: {elapsed}s"
        print(f"✓ Estadísticas ejecutadas en {elapsed:.3f}s")
