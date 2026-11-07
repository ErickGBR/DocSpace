from rest_framework import serializers
from .models import Usuario
from django.contrib.auth.hashers import make_password


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre_usuario', 'email', 'rol', 'activo', 'ultimo_login', 'created_at']
        read_only_fields = ['id', 'activo', 'ultimo_login', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre_usuario', 'email', 'password', 'rol', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'rol': {'required': False}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)