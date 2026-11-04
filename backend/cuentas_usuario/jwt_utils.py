import uuid
from datetime import datetime, timedelta, timezone
import jwt
from django.conf import settings
from .models import SesionJWT


class TokenError(Exception):
    pass


def _ahora():
    return datetime.now(timezone.utc)


def _payload(usuario, tipo, delta):
    ahora = _ahora()
    return {
        'sub': str(usuario.id),
        'tipo': tipo,
        'iat': ahora,
        'exp': ahora + delta,
        'jti': uuid.uuid4().hex,
    }


def emitir_tokens(usuario):
    access = _payload(usuario, 'access',
                      timedelta(minutes=settings.JWT_ACCESS_MINUTES))
    refresh = _payload(usuario, 'refresh',
                       timedelta(days=settings.JWT_REFRESH_DAYS))

    SesionJWT.objects.bulk_create([
        SesionJWT(usuario=usuario, jti=access['jti'], tipo='access',
                  expira=access['exp']),
        SesionJWT(usuario=usuario, jti=refresh['jti'], tipo='refresh',
                  expira=refresh['exp']),
    ])

    return {
        'access': jwt.encode(access, settings.JWT_SECRET_KEY,
                             algorithm='HS256'),
        'refresh': jwt.encode(refresh, settings.JWT_SECRET_KEY,
                              algorithm='HS256'),
    }


def decodificar(token, tipo_esperado):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY,
                             algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise TokenError('Token expirado')
    except jwt.InvalidTokenError:
        raise TokenError('Token invalido')
    if payload.get('tipo') != tipo_esperado:
        raise TokenError('Tipo de token invalido')
    return payload