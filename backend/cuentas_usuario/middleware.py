from django.http import JsonResponse

from .jwt_utils import TokenError, decodificar
from .models import SesionJWT, Usuario

RUTAS_LIBRES = {
    '/api/auth/register/',
    '/api/auth/login/',
    '/api/auth/refresh/',
}


class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.usuario = None

        if not request.path_info.startswith('/api/'):
            return self.get_response(request)
        ruta = request.path_info.rstrip('/') + '/'
        if ruta in RUTAS_LIBRES:
            request.path_info = ruta
            return self.get_response(request)

        header = request.headers.get('Authorization', '')
        if not header.startswith('Bearer '):
            return self.get_response(request)

        try:
            payload = decodificar(header[7:], 'access')
        except TokenError:
            return self.get_response(request)

        if not SesionJWT.objects.filter(jti=payload['jti'],
                                        revocada=False).exists():
            return self.get_response(request)

        usuario = Usuario.objects.filter(id=payload['sub'],
                                         activo=True).first()
        if usuario is None:
            return self.get_response(request)

        request.usuario = usuario
        request.jwt_payload = payload
        return self.get_response(request)