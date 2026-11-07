from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .jwt_utils import decodificar, TokenError
from .models import SesionJWT, Usuario


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        header = request.headers.get('Authorization', '')
        if not header.startswith('Bearer '):
            return None

        token = header[7:]
        try:
            payload = decodificar(token, 'access')
        except TokenError as e:
            raise AuthenticationFailed(str(e))

        if not SesionJWT.objects.filter(jti=payload['jti'], revocada=False).exists():
            raise AuthenticationFailed('Sesión revocada.')

        try:
            usuario = Usuario.objects.get(id=payload['sub'], activo=True)
        except Usuario.DoesNotExist:
            raise AuthenticationFailed('Usuario no válido.')

        request.usuario = usuario
        request.jwt_payload = payload
        return (usuario, None)

    def authenticate_header(self, request):
        return 'Bearer'