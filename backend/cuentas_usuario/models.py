from django.db import models

class Usuario(models.Model):
    nombre_usuario = models.CharField(max_length=255)
    rol = models.CharField(max_length=50, default='colaborador')
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_usuario