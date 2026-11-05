from rest_framework import generics
from .models import Historial
from .serializers import HistorialSerializer


class HistorialListView(generics.ListAPIView):
    queryset = Historial.objects.all()
    serializer_class = HistorialSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        accion = self.request.query_params.get('accion')
        if accion:
            qs = qs.filter(accion=accion)
        usuario = self.request.query_params.get('usuario')
        if usuario:
            qs = qs.filter(usuario_id=usuario)
        recurso_tipo = self.request.query_params.get('recurso_tipo')
        if recurso_tipo:
            qs = qs.filter(recurso_tipo=recurso_tipo)
        limit = self.request.query_params.get('limit')
        if limit:
            try:
                qs = qs[:int(limit)]
            except ValueError:
                pass
        return qs


class HistorialDetailView(generics.RetrieveAPIView):
    queryset = Historial.objects.all()
    serializer_class = HistorialSerializer