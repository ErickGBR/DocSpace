from rest_framework import serializers
from .models import Documento, VersionesDocumento
from espacios_trabajo.models import EspacioTrabajo
from cuentas_usuario.models import Usuario
from cuentas_usuario.serializers import UsuarioSerializer


class DocumentoSerializer(serializers.ModelSerializer):
    creado_por = UsuarioSerializer(read_only=True)
    espacio_trabajo_nombre = serializers.CharField(source='espacio_trabajo.title', read_only=True)

    class Meta:
        model = Documento
        fields = ['id', 'nombre_documento', 'espacio_trabajo', 'espacio_trabajo_nombre', 'creado_por', 'status', 'created_at']
        read_only_fields = ['id', 'creado_por', 'created_at']


class VersionesDocumentoSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.nombre_usuario', read_only=True)

    class Meta:
        model = VersionesDocumento
        fields = ['id', 'documento', 'accion', 'nombre_documento', 'documento_path', 'documento_path_version', 'usuario', 'usuario_nombre', 'status', 'created_at']
        read_only_fields = ['id', 'created_at', 'usuario']


class DocumentoSaveSerializer(serializers.Serializer):
    content = serializers.CharField()


class DocumentoPermissionSerializer(serializers.Serializer):
    usuario = serializers.IntegerField()
    rol = serializers.CharField(required=False, allow_null=True)
    leer = serializers.BooleanField()
    editar = serializers.BooleanField()
    administracion = serializers.BooleanField()
    tipo = serializers.CharField()