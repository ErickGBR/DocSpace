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