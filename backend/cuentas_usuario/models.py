from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from django.db import models

_ph = PasswordHasher()


class Usuario(models.Model):
    nombre_usuario = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255, editable=False)
    activo = models.BooleanField(default=True)
    ultimo_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    rol = models.ForeignKey(
        'Rol',
        on_delete=models.PROTECT,
        related_name='usuarios',
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.nombre_usuario

    def set_password(self, raw_password):
        self.password = _ph.hash(raw_password)

    def check_password(self, raw_password):
        if not self.password:
            return False
        try:
            return _ph.verify(self.password, raw_password)
        except (VerifyMismatchError, InvalidHashError, ValueError):
            return False

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('$argon2'):
            self.set_password(self.password)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'usuarios'


class Rol(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'usuarios_rol'


class RolPermiso(models.Model):
    tipo = models.CharField(max_length=20)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name='permisos')
    editar = models.BooleanField(default=False)
    leer = models.BooleanField(default=True)
    administracion = models.BooleanField(default=False)
    documento = models.ForeignKey(
        'documentos.Documento',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='permisos_rol',
    )
    espacio_trabajo = models.ForeignKey(
        'espacios_trabajo.EspacioTrabajo',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='permisos_rol',
    )
    usuario = models.ForeignKey(
        'cuentas_usuario.Usuario',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='permisos_rol',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'usuarios_rol_permisos'
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(tipo='admin') |
                    models.Q(tipo='documento') |
                    models.Q(tipo='espacio')
                ),
                name='rolpermiso_tipo_valido',
            ),
        ]