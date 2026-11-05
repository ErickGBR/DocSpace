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