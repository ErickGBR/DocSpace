from rest_framework import serializers
from .models import EspacioTrabajo
from cuentas_usuario.serializers import UsuarioSerializer
from cuentas_usuario.models import Usuario


class EspacioTrabajoSerializer(serializers.ModelSerializer):
    miembros = UsuarioSerializer(many=True, read_only=True)
    miembros_ids = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='miembros'
    )
    creado_por = UsuarioSerializer(read_only=True)

    class Meta:
        model = EspacioTrabajo
        fields = ['id', 'title', 'bucked_path', 'status', 'created_at', 'miembros', 'miembros_ids', 'creado_por']
        read_only_fields = ['id', 'created_at', 'creado_por']

    def create(self, validated_data):
        miembros = validated_data.pop('miembros', [])
        espacio = EspacioTrabajo.objects.create(**validated_data)
        if miembros:
            espacio.miembros.set(miembros)
        return espacio

    def update(self, instance, validated_data):
        miembros = validated_data.pop('miembros', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if miembros is not None:
            instance.miembros.set(miembros)
        return instance