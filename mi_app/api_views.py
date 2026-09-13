"""
API Views para endpoints dinámicos del sistema
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Cliente

@login_required
@require_http_methods(["GET"])
def api_clientes_search(request):
    """
    API endpoint para búsqueda de clientes
    
    GET /api/clientes/search/?q=texto
    
    Query parameters:
    - q: Texto de búsqueda (mínimo 2 caracteres)
    - limit: Máximo de resultados (default: 20)
    
    Response:
    {
        "success": true/false,
        "query": "texto buscado",
        "results": [
            {
                "id": 1,
                "nombre": "Juan Pérez",
                "cedula": "1234567890",
                "telefono": "555-1234",
                "estado": "ACTIVO"
            },
            ...
        ],
        "count": 5,
        "error": "Mensaje de error si aplica"
    }
    """
    
    try:
        q = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 20))
        
        # Validación: mínimo 2 caracteres
        if len(q) < 2:
            return JsonResponse({
                'success': False,
                'error': 'Mínimo 2 caracteres para buscar',
                'results': [],
                'count': 0
            })
        
        # Validación: máximo 100 caracteres
        if len(q) > 100:
            q = q[:100]
        
        # Buscar en nombre, cédula o teléfono
        clientes = Cliente.objects.filter(
            Q(nombre__icontains=q) | 
            Q(cedula__icontains=q) |
            Q(celular__icontains=q)
        ).values('id', 'nombre', 'cedula', 'celular', 'estado')[:limit]
        
        # Convertir a lista
        resultados = list(clientes)
        
        return JsonResponse({
            'success': True,
            'query': q,
            'results': resultados,
            'count': len(resultados)
        })
    
    except ValueError:
        return JsonResponse({
            'success': False,
            'error': 'Parámetro inválido',
            'results': []
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}',
            'results': []
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_prestamos_search(request):
    """
    API endpoint para búsqueda de préstamos
    
    GET /api/prestamos/search/?q=texto
    
    Busca por número de préstamo o nombre de cliente
    """
    
    try:
        from .models import Prestamo
        
        q = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 20))
        
        if len(q) < 2:
            return JsonResponse({
                'success': False,
                'error': 'Mínimo 2 caracteres',
                'results': []
            })
        
        # Buscar préstamos por cliente o por monto
        prestamos = Prestamo.objects.filter(
            Q(cliente__nombre__icontains=q) |
            Q(id__icontains=q)
        ).select_related('cliente').values(
            'id', 'cliente__nombre', 'monto', 'estado'
        )[:limit]
        
        resultados = list(prestamos)
        
        return JsonResponse({
            'success': True,
            'query': q,
            'results': resultados,
            'count': len(resultados)
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'results': []
        }, status=500)
