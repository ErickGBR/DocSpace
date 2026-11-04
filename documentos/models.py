from django.db import models
from espacios_trabajo.models import EspacioTrabajo
from cuentas_usuario.models import Usuario

class Documento(models.Model):
    espacio_trabajo = models.ForeignKey(EspacioTrabajo, on_delete=models.CASCADE, related_name='documentos')
    nombre_documento = models.CharField(max_length=255)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='documentos_creados')
    status = models.CharField(max_length=50, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_documento

class VersionesDocumento(models.Model):
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE, related_name='versiones')
    espacio_trabajo = models.ForeignKey(EspacioTrabajo, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=100)
    nombre_documento = models.CharField(max_length=255)
    documento_path = models.CharField(max_length=255, blank=True, null=True)
    documento_path_version = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']