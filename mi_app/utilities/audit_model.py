"""
CRÍTICA #6: SYSTEM AUDIT LOG
Model para registrar TODOS los cambios en el sistema
¿QUIÉN hizo QUÉ, CUÁNDO, y ANTES/DESPUÉS?
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class AuditLog(models.Model):
    """
    Registro de auditoría completo de todas las operaciones en el sistema.
    
    Campos:
    - usuario: Quién realizó la acción
    - accion: CREATE, UPDATE, DELETE, RESTORE
    - modelo: Qué modelo fue afectado (Prestamo, Cuota, Pago, Client, etc)
    - objeto_id: ID del objeto afectado
    - cambios: JSON con before/after de los campos modificados
    - timestamp: Cuándo se realizó (auto_now_add)
    - ip_address: De dónde vino la solicitud
    - descripcion: Descripción legible de la acción
    """
    
    ACCIONES = [
        ('CREATE', 'Crear'),
        ('UPDATE', 'Actualizar'),
        ('DELETE', 'Eliminar'),
        ('RESTORE', 'Restaurar'),
    ]
    
    MODELOS = [
        ('Cliente', 'Cliente'),
        ('Prestamo', 'Préstamo'),
        ('Cuota', 'Cuota'),
        ('Pago', 'Pago'),
        ('ListaNegra', 'Lista Negra'),
        ('Configuracion', 'Configuración'),
        ('User', 'Usuario'),
    ]
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        db_index=True,
        help_text="Usuario que realizó la acción"
    )
    
    accion = models.CharField(
        max_length=20,
        choices=ACCIONES,
        db_index=True,
        help_text="Tipo de acción realizada"
    )
    
    modelo = models.CharField(
        max_length=50,
        choices=MODELOS,
        db_index=True,
        help_text="Modelo/tabla afectada"
    )
    
    objeto_id = models.IntegerField(
        help_text="ID del objeto afectado"
    )
    
    objeto_representacion = models.CharField(
        max_length=255,
        blank=True,
        help_text="Representación legible del objeto (ej: Prestamo #123)"
    )
    
    cambios = models.JSONField(
        null=True,
        blank=True,
        help_text="JSON con cambios: {'campo': ['antes', 'después']}"
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Fecha y hora de la acción"
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP de origen de la solicitud"
    )
    
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción legible en formato texto"
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"
        indexes = [
            models.Index(fields=['usuario', '-timestamp']),
            models.Index(fields=['modelo', '-timestamp']),
            models.Index(fields=['accion', '-timestamp']),
            models.Index(fields=['objeto_id', 'modelo']),
        ]
    
    def __str__(self):
        return f"{self.get_accion_display()} {self.objeto_representacion} por {self.usuario.username if self.usuario else 'Sistema'} ({self.timestamp.strftime('%d/%m/%Y %H:%M')})"
    
    def get_cambios_legibles(self):
        """Retorna los cambios en formato legible"""
        if not self.cambios:
            return "Sin cambios registrados"
        
        cambios_texto = []
        for campo, [antes, despues] in self.cambios.items():
            cambios_texto.append(f"{campo}: '{antes}' → '{despues}'")
        
        return "; ".join(cambios_texto)
    
    @property
    def resumen(self):
        """Resumen de la auditoría"""
        return f"{self.get_accion_display()}: {self.objeto_representacion} - {self.get_cambios_legibles()}"
