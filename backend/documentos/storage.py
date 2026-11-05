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