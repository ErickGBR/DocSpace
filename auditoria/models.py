from django.db import models
from cuentas_usuario.models import Usuario

class Historial(models.Model):
    accion = models.CharField(max_length=100)
    accion_detalle = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='acciones_historial')
    recurso_tipo = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']