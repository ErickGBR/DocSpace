from django.db import models
from cuentas_usuario.models import Usuario

class EspacioTrabajo(models.Model):
    title = models.CharField(max_length=255)
    bucked_path = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    miembros = models.ManyToManyField(Usuario, related_name='espacios_trabajo', blank=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='espacios_creados')

    def __str__(self):
        return self.title