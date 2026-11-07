from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from .models import Documento
from app_permisos.models import UsuariosRolPermisos


def get_user_document_permission(usuario, documento):
    """Get user's permission level for a document: 'admin', 'edit', 'read', or None"""
    # Check if user is owner/creator
    if documento.usuario == usuario:
        return 'admin'

    # Check if user is gestor of the workspace
    if documento.espacio_trabajo.miembros.filter(id=usuario.id).exists():
        # Check if user is gestor role
        try:
            from cuentas_usuario.models import Rol
            rol_gestor = Rol.objects.get(nombre='gestor')
            if usuario.rol == rol_gestor:
                return 'admin'
        except:
            pass

    # Check document-specific permissions
    permiso = UsuariosRolPermisos.objects.filter(
        usuario=usuario,
        documento=documento
    ).first()

    if permiso:
        if permiso.administracion:
            return 'admin'
        elif permiso.editar:
            return 'edit'
        elif permiso.leer:
            return 'read'

    # Check workspace-level permissions
    permiso_espacio = UsuariosRolPermisos.objects.filter(
        usuario=usuario,
        espacio_trabajo=documento.espacio_trabajo
    ).first()

    if permiso_espacio:
        if permiso_espacio.administracion:
            return 'admin'
        elif permiso_espacio.editar:
            return 'edit'
        elif permiso_espacio.leer:
            return 'read'

    # Check if user is member of workspace (default read access)
    if documento.espacio_trabajo.miembros.filter(id=usuario.id).exists():
        return 'read'

    return None


class DocumentPermission(permissions.BasePermission):
    """
    Permission class for document access control.
    Supports: read, edit, admin permissions.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        permission = get_user_document_permission(request.user, obj)

        if permission is None:
            return False

        # For safe methods (GET, HEAD, OPTIONS), need at least read
        if view.action in ['list', 'retrieve', 'content', 'versions', 'compare', 'historial']:
            return permission in ['read', 'edit', 'admin']

        # For write methods (create, update, partial_update, save, restore)
        if view.action in ['create', 'update', 'partial_update', 'save', 'restore']:
            return permission in ['edit', 'admin']

        # For delete
        if view.action == 'destroy':
            return permission == 'admin'

        # For permission management
        if view.action in ['permissions', 'grant_permission', 'revoke_permission']:
            return permission == 'admin'

        return False


class CanReadDocument(permissions.BasePermission):
    """Check if user can read document"""
    def has_object_permission(self, request, view, obj):
        return get_user_document_permission(request.user, obj) in ['read', 'edit', 'admin']


class CanEditDocument(permissions.BasePermission):
    """Check if user can edit document"""
    def has_object_permission(self, request, view, obj):
        return get_user_document_permission(request.user, obj) in ['edit', 'admin']


class CanAdminDocument(permissions.BasePermission):
    """Check if user can administer document"""
    def has_object_permission(self, request, view, obj):
        return get_user_document_permission(request.user, obj) == 'admin'