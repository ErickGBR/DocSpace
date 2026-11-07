from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Historial
from .serializers import HistorialSerializer


class HistorialViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HistorialSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Historial.objects.filter(usuario=self.request.user)
        accion = self.request.query_params.get('accion')
        recurso_tipo = self.request.query_params.get('recurso_tipo')
        if accion:
            queryset = queryset.filter(accion=accion)
        if recurso_tipo:
            queryset = queryset.filter(recurso_tipo=recurso_tipo)
        return queryset