from auditoria.models import Historial
from cuentas_usuario.models import Usuario


def registrar_accion(
    usuario: Usuario,
    accion: str,
    recurso_tipo: str = None,
    accion_detalle: str = None,
    recurso_id: int = None,
):
    if not usuario:
        return None

    detalle = accion_detalle or f"{accion.capitalize()} de {recurso_tipo or 'recurso'}"
    if recurso_id:
        detalle += f" (ID: {recurso_id})"

    return Historial.objects.create(
        accion=accion,
        accion_detalle=detalle,
        usuario=usuario,
        recurso_tipo=recurso_tipo,
    )


class AccionesHistorial:
    DOC_CREATE = 'documento_crear'
    DOC_UPLOAD = 'documento_subir'
    DOC_SAVE = 'documento_guardar'
    DOC_UPDATE = 'documento_actualizar'
    DOC_DELETE = 'documento_eliminar'
    DOC_DOWNLOAD = 'documento_descargar'
    DOC_VIEW = 'documento_ver'

    VERSION_CREATE = 'version_crear'
    VERSION_RESTORE = 'version_restaurar'
    VERSION_LIST = 'version_listar'

    ESPACIO_CREATE = 'espacio_crear'
    ESPACIO_UPDATE = 'espacio_actualizar'
    ESPACIO_DELETE = 'espacio_eliminar'

    USER_LOGIN = 'usuario_login'
    USER_LOGOUT = 'usuario_logout'
    USER_REGISTER = 'usuario_registrar'

    PERMISO_ASIGNAR = 'permiso_asignar'
    PERMISO_QUITAR = 'permiso_quitar'