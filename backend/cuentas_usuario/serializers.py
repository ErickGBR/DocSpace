from rest_framework import serializers
from .models import Usuario, Rol
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre_usuario', 'email', 'rol', 'activo', 'ultimo_login', 'created_at']
        read_only_fields = ['id', 'activo', 'ultimo_login', 'created_at']


class RegisterSerializer(serializers.Serializer):
    nombre_usuario = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    rol = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    def create(self, validated_data):
        password = validated_data.pop('password')
        rol_nombre = validated_data.pop('rol', None)
        try:
            usuario = Usuario.objects.create(**validated_data)
        except IntegrityError as e:
            error_str = str(e)
            if 'email_key' in error_str.lower():
                raise serializers.ValidationError({'email': 'Este correo ya está registrado.'})
            raise serializers.ValidationError({'detail': 'Error al crear usuario.'})
        if rol_nombre:
            try:
                rol = Rol.objects.get(nombre=rol_nombre)
                usuario.rol = rol
            except Rol.DoesNotExist:
                pass
        usuario.set_password(password)
        usuario.save()
        return usuario


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)