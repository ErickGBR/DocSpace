import os
import shutil
from datetime import datetime
from pathlib import Path
from django.conf import settings

BASE_STORAGE_PATH = getattr(settings, 'DOCSPACE_STORAGE_PATH',
    Path(settings.BASE_DIR).parent / 'docspace_storage')


def get_gestor_folder(gestor_id: int) -> Path:
    folder = BASE_STORAGE_PATH / f'gestor_{gestor_id}'
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def get_document_folder(gestor_id: int, filename: str) -> Path:
    epoch = int(datetime.now().timestamp())
    safe_name = "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_', '-')).strip()
    safe_name = safe_name.replace(' ', '_')
    folder_name = f"{safe_name}_{epoch}"

    folder = get_gestor_folder(gestor_id) / folder_name
    folder.mkdir(parents=True, exist_ok=True)

    versions_folder = folder / 'versions'
    versions_folder.mkdir(exist_ok=True)

    return folder


def get_document_root_file(document_folder: Path, filename: str) -> Path:
    return document_folder / filename


def get_version_file(document_folder: Path, filename: str, version_epoch: int = None) -> Path:
    versions_folder = document_folder / 'versions'
    name, ext = os.path.splitext(filename)
    epoch = version_epoch or int(datetime.now().timestamp())
    return versions_folder / f"{name}_{epoch}{ext}"


def get_next_version_epoch(document_folder: Path, filename: str) -> int:
    return int(datetime.now().timestamp())


def save_initial_file(gestor_id: int, filename: str, content: bytes, mime_type: str = None) -> dict:
    document_folder = get_document_folder(gestor_id, filename)
    root_file = get_document_root_file(document_folder, filename)

    root_file.write_bytes(content)

    version_epoch = int(datetime.now().timestamp())
    version_file = get_version_file(document_folder, filename, version_epoch)
    version_file.write_bytes(content)

    relative_root = root_file.relative_to(BASE_STORAGE_PATH)
    relative_version = version_file.relative_to(BASE_STORAGE_PATH)
    relative_folder = document_folder.relative_to(BASE_STORAGE_PATH)

    return {
        'storage_path': str(relative_folder),
        'documento_path': str(relative_root),
        'documento_path_version': str(relative_version),
        'version_epoch': version_epoch,
        'size': len(content),
        'mime_type': mime_type or 'application/octet-stream',
    }


def save_new_version(document_folder_rel: str, filename: str, content: bytes, version_epoch: int = None) -> dict:
    document_folder = BASE_STORAGE_PATH / document_folder_rel
    if not document_folder.exists():
        raise FileNotFoundError(f"Carpeta de documento no encontrada: {document_folder}")

    root_file = get_document_root_file(document_folder, filename)

    if version_epoch is None:
        version_epoch = get_next_version_epoch(document_folder, filename)

    version_file = get_version_file(document_folder, filename, version_epoch)
    if root_file.exists():
        shutil.copy2(root_file, version_file)

    root_file.write_bytes(content)

    relative_root = root_file.relative_to(BASE_STORAGE_PATH)
    relative_version = version_file.relative_to(BASE_STORAGE_PATH)

    return {
        'documento_path': str(relative_root),
        'documento_path_version': str(relative_version),
        'version_epoch': version_epoch,
        'size': len(content),
    }


def get_document_versions(document_folder_rel: str, filename: str) -> list:
    document_folder = BASE_STORAGE_PATH / document_folder_rel
    versions_folder = document_folder / 'versions'

    if not versions_folder.exists():
        return []

    name, ext = os.path.splitext(filename)
    versions = []

    for v_file in sorted(versions_folder.glob(f"{name}_*{ext}")):
        try:
            stem = v_file.stem
            epoch_str = stem.split('_')[-1]
            version_epoch = int(epoch_str)
            stat = v_file.stat()
            versions.append({
                'version_epoch': version_epoch,
                'version_datetime': datetime.fromtimestamp(version_epoch).isoformat(),
                'filename': v_file.name,
                'path': str(v_file.relative_to(BASE_STORAGE_PATH)),
                'size': stat.st_size,
                'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            })
        except (ValueError, IndexError):
            continue

    return sorted(versions, key=lambda x: x['version_epoch'])