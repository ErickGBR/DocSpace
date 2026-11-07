from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import EspacioTrabajo
from .serializers import EspacioTrabajoSerializer
from cuentas_usuario.models import Usuario


class EspacioTrabajoViewSet(viewsets.ModelViewSet):
    serializer_class = EspacioTrabajoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EspacioTrabajo.objects.filter(miembros=self.request.user)

    def perform_create(self, serializer):
        espacio = serializer.save(creado_por=self.request.user)
        espacio.miembros.add(self.request.user)

    @action(detail=True, methods=['post'])
    def invitar_usuario(self, request, pk=None):
        espacio = self.get_object()
        user_id = request.data.get('usuario_id')
        if not user_id:
            return Response({'error': 'usuario_id requerido'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            usuario = Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        espacio.miembros.add(usuario)
        return Response({'mensaje': 'Usuario invitado correctamente'})

    @action(detail=True, methods=['post'])
    def remover_usuario(self, request, pk=None):
        espacio = self.get_object()
        user_id = request.data.get('usuario_id')
        if not user_id:
            return Response({'error': 'usuario_id requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            usuario = Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if usuario == request.user:
            return Response({'error': 'No puedes removerte a ti mismo'}, status=status.HTTP_400_BAD_REQUEST)

        espacio.miembros.remove(usuario)
        return Response({'mensaje': 'Usuario removido correctamente'})

    @action(detail=True, methods=['get'])
    def miembros(self, request, pk=None):
        espacio = self.get_object()
        miembros = espacio.miembros.all()
        from cuentas_usuario.serializers import UsuarioSerializer
        serializer = UsuarioSerializer(miembros, many=True)
        return Response(serializer.data)