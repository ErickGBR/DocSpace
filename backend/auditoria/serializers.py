from rest_framework import serializers
from .models import Historial
from cuentas_usuario.serializers import UsuarioSerializer


class HistorialSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.nombre_usuario', read_only=True)
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)

    class Meta:
        model = Historial
        fields = ['id', 'accion', 'accion_detalle', 'usuario', 'usuario_nombre', 'usuario_email', 'recurso_tipo', 'created_at']
        read_only_fields = fields