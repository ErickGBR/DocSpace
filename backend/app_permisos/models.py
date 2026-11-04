from django.db import models
from cuentas_usuario.models import Usuario
from espacios_trabajo.models import EspacioTrabajo
from documentos.models import Documento

class UsuariosRol(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='roles')
    nombre = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.usuario.nombre_usuario}"

class UsuariosRolPermisos(models.Model):
    rol = models.ForeignKey(UsuariosRol, on_delete=models.CASCADE, related_name='permisos')
    editar = models.BooleanField(default=False)
    leer = models.BooleanField(default=True)
    administracion = models.BooleanField(default=False)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE, null=True, blank=True, related_name='permisos')
    espacio_trabajo = models.ForeignKey(EspacioTrabajo, on_delete=models.CASCADE, null=True, blank=True, related_name='permisos')
    created_at = models.DateTimeField(auto_now_add=True)