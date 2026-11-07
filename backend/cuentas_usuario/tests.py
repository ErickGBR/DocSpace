from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Usuario, Rol


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.rol_gestor, _ = Rol.objects.get_or_create(nombre='gestor')
        self.rol_colaborador, _ = Rol.objects.get_or_create(nombre='colaborador')

    def create_user(self, nombre_usuario, email, password, rol=None):
        return Usuario.create_user(nombre_usuario, email, password, rol)

    def test_register_usuario(self):
        data = {
            'nombre_usuario': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'rol': 'gestor'
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['usuario']['email'], 'test@example.com')

    def test_register_duplicate_email(self):
        self.create_user('user1', 'test@example.com', 'password123')
        data = {
            'nombre_usuario': 'user2',
            'email': 'test@example.com',
            'password': 'password123',
            'rol': 'gestor'
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        email_error = response.data['email']
        if isinstance(email_error, list):
            self.assertEqual(str(email_error[0]), 'Este correo ya está registrado.')
        else:
            self.assertEqual(str(email_error), 'Este correo ya está registrado.')

    def test_login(self):
        self.create_user('testuser', 'test@example.com', 'password123')
        data = {'email': 'test@example.com', 'password': 'password123'}
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_password(self):
        self.create_user('testuser', 'test@example.com', 'password123')
        data = {'email': 'test@example.com', 'password': 'wrong'}
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        usuario = self.create_user('testuser', 'test@example.com', 'password123')
        from cuentas_usuario.jwt_utils import emitir_tokens
        tokens = emitir_tokens(usuario)
        response = self.client.post('/api/auth/refresh/', {'refresh': tokens['refresh']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_logout(self):
        usuario = self.create_user('testuser', 'test@example.com', 'password123')
        from cuentas_usuario.jwt_utils import emitir_tokens
        tokens = emitir_tokens(usuario)
        response = self.client.post('/api/auth/logout/', {'refresh': tokens['refresh']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)