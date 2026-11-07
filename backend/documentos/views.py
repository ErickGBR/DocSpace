from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Documento, VersionesDocumento
from .serializers import DocumentoSerializer, VersionesDocumentoSerializer, DocumentoSaveSerializer, DocumentoPermissionSerializer
from .storage import save_initial_file, save_new_version, get_document_versions, get_file_content, delete_document
from .permissions import DocumentPermission, get_user_document_permission
from auditoria.utils import registrar_accion
from auditoria.models import Historial
from app_permisos.models import UsuariosRolPermisos
from cuentas_usuario.models import Usuario, Rol
from rest_framework.exceptions import PermissionDenied


class DocumentoViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentoSerializer
    permission_classes = [IsAuthenticated, DocumentPermission]

    def get_queryset(self):
        espacio_id = self.request.query_params.get('espacio_trabajo')
        qs = Documento.objects.filter(espacio_trabajo__miembros=self.request.user)
        if espacio_id:
            qs = qs.filter(espacio_trabajo_id=espacio_id)
        return qs

    def perform_create(self, serializer):
        documento = serializer.save(usuario=self.request.user)
        registrar_accion(
            usuario=self.request.user,
            accion='documento_crear',
            recurso_tipo='documento',
            accion_detalle=f'Documento creado: {documento.nombre_documento}',
            recurso_id=documento.id
        )

    def perform_destroy(self, instance):
        with transaction.atomic():
            registrar_accion(
                usuario=self.request.user,
                accion='documento_eliminar',
                recurso_tipo='documento',
                accion_detalle=f'Documento eliminado: {instance.nombre_documento}',
                recurso_id=instance.id
            )
            delete_document(instance.documento_path)
            instance.delete()

    @action(detail=True, methods=['post'])
    def save(self, request, pk=None):
        documento = self.get_object()
        serializer = DocumentoSaveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        content = serializer.validated_data['content']

        with transaction.atomic():
            if documento.documento_path:
                data = save_new_version(documento.documento_path, documento.nombre_documento, content.encode('utf-8'))
                documento.documento_path = data['documento_path']
                documento.documento_path_version = data['documento_path_version']
                documento.save()

                VersionesDocumento.objects.create(
                    documento=documento,
                    espacio_trabajo=documento.espacio_trabajo,
                    usuario=self.request.user,
                    accion='documento_guardar',
                    nombre_documento=documento.nombre_documento,
                    documento_path=documento.documento_path,
                    documento_path_version=data['documento_path_version']
                )
            else:
                data = save_initial_file(
                    documento.espacio_trabajo.id,
                    documento.nombre_documento,
                    content.encode('utf-8'),
                    'text/plain'
                )
                documento.documento_path = data['documento_path']
                documento.documento_path_version = data['documento_path_version']
                documento.save()

                VersionesDocumento.objects.create(
                    documento=documento,
                    espacio_trabajo=documento.espacio_trabajo,
                    usuario=self.request.user,
                    accion='documento_crear',
                    nombre_documento=documento.nombre_documento,
                    documento_path=data['documento_path'],
                    documento_path_version=data['documento_path_version']
                )

            registrar_accion(
                usuario=self.request.user,
                accion='documento_guardar',
                recurso_tipo='documento',
                accion_detalle=f'Documento guardado: {documento.nombre_documento}',
                recurso_id=documento.id
            )

        return Response({'mensaje': 'Documento guardado correctamente'})

    @action(detail=True, methods=['get'])
    def content(self, request, pk=None):
        documento = self.get_object()
        version = request.query_params.get('version')
        try:
            content = get_file_content(documento.documento_path, documento.nombre_documento, version)
            return Response({
                'content': content.decode('utf-8'),
                'version': version or 'latest'
            })
        except FileNotFoundError:
            return Response({'error': 'Archivo no encontrado'}, status=404)

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        documento = self.get_object()
        versions = get_document_versions(documento.documento_path, documento.nombre_documento)
        serializer = VersionesDocumentoSerializer(
            [v for v in versions],
            many=True
        )
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def compare(self, request, pk=None):
        documento = self.get_object()
        v1 = request.query_params.get('v1')
        v2 = request.query_params.get('v2')

        if not v1 or not v2:
            return Response({'error': 'Se requieren v1 y v2'}, status=400)

        try:
            content1 = get_file_content(documento.documento_path, documento.nombre_documento, v1).decode('utf-8')
            content2 = get_file_content(documento.documento_path, documento.nombre_documento, v2).decode('utf-8')
        except FileNotFoundError:
            return Response({'error': 'Versión no encontrada'}, status=404)

        return Response({
            'v1': {'version': v1, 'content': content1},
            'v2': {'version': v2, 'content': content2},
            'diff': self._diff_text(content1, content2)
        })

    def _diff_text(self, text1, text2):
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()
        diff = []
        i = j = 0
        while i < len(lines1) or j < len(lines2):
            if i < len(lines1) and j < len(lines2) and lines1[i] == lines2[j]:
                diff.append({'type': 'same', 'line': lines1[i]})
                i += 1
                j += 1
            elif i < len(lines1) and (j >= len(lines2) or lines1[i] != lines2[j]):
                diff.append({'type': 'removed', 'line': lines1[i]})
                i += 1
            else:
                diff.append({'type': 'added', 'line': lines2[j]})
                j += 1
        return diff

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        documento = self.get_object()
        version = request.data.get('version')
        if not version:
            return Response({'error': 'version requerida'}, status=400)

        try:
            content = get_file_content(documento.documento_path, documento.nombre_documento, version).decode('utf-8')
        except FileNotFoundError:
            return Response({'error': 'Versión no encontrada'}, status=404)

        with transaction.atomic():
            data = save_new_version(documento.documento_path, documento.nombre_documento, content.encode('utf-8'))
            documento.documento_path = data['documento_path']
            documento.documento_path_version = data['documento_path_version']
            documento.save()

            VersionesDocumento.objects.create(
                documento=documento,
                espacio_trabajo=documento.espacio_trabajo,
                usuario=self.request.user,
                accion='documento_restaurar',
                nombre_documento=documento.nombre_documento,
                documento_path=documento.documento_path,
                documento_path_version=data['documento_path_version']
            )

            from auditoria.utils import registrar_accion
            registrar_accion(
                usuario=self.request.user,
                accion='documento_restaurar',
                recurso_tipo='documento',
                accion_detalle=f'Documento restaurado a versión {version}: {documento.nombre_documento}',
                recurso_id=documento.id
            )

        return Response({'mensaje': 'Documento restaurado correctamente', 'version': version})

    @action(detail=True, methods=['get'])
    def historial(self, request, pk=None):
        documento = self.get_object()
        historial = Historial.objects.filter(recurso_tipo='documento', accion_detalle__icontains=documento.nombre_documento)
        from auditoria.serializers import HistorialSerializer
        serializer = HistorialSerializer(historial[:50], many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        """Get all permissions for this document"""
        documento = self.get_object()
        perms = UsuariosRolPermisos.objects.filter(documento=documento).select_related('usuario', 'rol')
        from app_permisos.serializers import UsuariosRolPermisosSerializer
        serializer = UsuariosRolPermisosSerializer(perms, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def grant_permission(self, request, pk=None):
        """Grant permission to user for this document"""
        documento = self.get_object()
        user_id = request.data.get('usuario_id')
        permiso_tipo = request.data.get('tipo')  # read, edit, admin
        rol_nombre = request.data.get('rol')  # optional, for role-based

        if not user_id or not permiso_tipo:
            return Response({'error': 'usuario_id y tipo requeridos'}, status=400)

        try:
            usuario = Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=404)

        # Verify user has admin permission on this document
        user_perm = get_user_document_permission(self.request.user, self.get_object())
        if user_perm != 'admin':
            raise PermissionDenied('No tienes permiso de administración sobre este documento')

        # Check if user is member of workspace
        if not self.get_object().espacio_trabajo.miembros.filter(id=usuario.id).exists():
            return Response({'error': 'Usuario no es miembro del espacio de trabajo'}, status=400)

        # Create or update permission
        rol = None
        if rol_nombre:
            try:
                rol = Rol.objects.get(nombre=rol_nombre)
            except Rol.DoesNotExist:
                return Response({'error': 'Rol no encontrado'}, status=400)

        defaults = {
            'leer': permiso_tipo in ['read', 'edit', 'admin'],
            'editar': permiso_tipo in ['edit', 'admin'],
            'administracion': permiso_tipo == 'admin',
            'tipo': 'documento',
        }

        permiso, created = UsuariosRolPermisos.objects.update_or_create(
            usuario=usuario,
            documento=self.get_object(),
            defaults=defaults
        )

        if rol:
            permiso.rol = rol
            permiso.save()

        registrar_accion(
            usuario=self.request.user,
            accion='permiso_otorgar',
            recurso_tipo='documento',
            accion_detalle=f'Permiso {permiso_tipo} otorgado a {usuario.nombre_usuario} en documento',
            recurso_id=self.get_object().id
        )

        return Response({'mensaje': 'Permiso otorgado correctamente'})

    @action(detail=True, methods=['post'])
    def revoke_permission(self, request, pk=None):
        """Revoke permission from user for this document"""
        documento = self.get_object()
        user_id = request.data.get('usuario_id')

        if not user_id:
            return Response({'error': 'usuario_id requerido'}, status=400)

        try:
            usuario = Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=404)

        # Verify user has admin permission
        user_perm = get_user_document_permission(self.request.user, self.get_object())
        if user_perm != 'admin':
            raise PermissionDenied('No tienes permiso de administración sobre este documento')

        try:
            permiso = UsuariosRolPermisos.objects.get(usuario=usuario, documento=self.get_object())
            permiso.delete()
        except UsuariosRolPermisos.DoesNotExist:
            return Response({'error': 'Permiso no encontrado'}, status=404)

        registrar_accion(
            usuario=self.request.user,
            accion='permiso_revocar',
            recurso_tipo='documento',
            accion_detalle=f'Permiso revocado a usuario {usuario.nombre_usuario}',
            recurso_id=self.get_object().id
        )

        return Response({'mensaje': 'Permiso revocado correctamente'})