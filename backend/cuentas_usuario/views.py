from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import LoginSerializer, RegisterSerializer, UsuarioSerializer
from .models import Usuario
from .jwt_utils import emitir_tokens, decodificar, TokenError


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response({'detail': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

        if not usuario.check_password(password):
            return Response({'detail': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

        if not usuario.activo:
            return Response({'detail': 'Usuario inactivo'}, status=status.HTTP_403_FORBIDDEN)

        tokens = emitir_tokens(usuario)
        return Response({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'usuario': UsuarioSerializer(usuario).data
        })


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()
        tokens = emitir_tokens(usuario)
        return Response({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'usuario': UsuarioSerializer(usuario).data
        }, status=status.HTTP_201_CREATED)


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return Response({'detail': 'Refresh token requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = decodificar(refresh, 'refresh')
        except TokenError as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        from .models import SesionJWT
        if not SesionJWT.objects.filter(jti=payload['jti'], revocada=False).exists():
            return Response({'detail': 'Sesión revocada'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            usuario = Usuario.objects.get(id=payload['sub'], activo=True)
        except Usuario.DoesNotExist:
            return Response({'detail': 'Usuario no válido'}, status=status.HTTP_401_UNAUTHORIZED)

        from .models import SesionJWT
        SesionJWT.objects.filter(jti=payload['jti']).update(revocada=True)

        tokens = emitir_tokens(usuario)
        return Response({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'usuario': UsuarioSerializer(usuario).data
        })


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh = request.data.get('refresh')
        if refresh:
            try:
                payload = decodificar(refresh, 'refresh')
                from .models import SesionJWT
                SesionJWT.objects.filter(jti=payload['jti']).update(revocada=True)
            except TokenError:
                pass
        return Response({'detail': 'Sesión cerrada'})