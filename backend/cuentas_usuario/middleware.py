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
            return JsonResponse({'detail': 'Token requerido.'}, status=401)

        try:
            payload = decodificar(header[7:], 'access')
        except TokenError as exc:
            return JsonResponse({'detail': str(exc)}, status=401)

        if not SesionJWT.objects.filter(jti=payload['jti'],
                                        revocada=False).exists():
            return JsonResponse({'detail': 'Sesión revocada.'}, status=401)

        usuario = Usuario.objects.filter(id=payload['sub'],
                                         activo=True).first()
        if usuario is None:
            return JsonResponse({'detail': 'Usuario no válido.'}, status=401)

        request.usuario = usuario
        request.jwt_payload = payload
        return self.get_response(request)