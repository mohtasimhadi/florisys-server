import os
import shutil
from pathlib import Path
from uuid import uuid4

ALLOWED_EXT = {".tif", ".tiff"}

def ensure_ext(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXT:
        raise ValueError("Unsupported file type")
    return ext

def new_filename(original: str) -> tuple[str, str]:
    ext = ensure_ext(original)
    file_id = uuid4().hex
    name = Path(original).stem
    return file_id, f"{file_id}{ext}", name

def save_upload(dst_dir: str, upload_file) -> tuple[str, str, str]:
    file_id, filename, name = new_filename(upload_file.filename)
    dst = Path(dst_dir) / filename
    with dst.open("wb") as out:
        shutil.copyfileobj(upload_file.file, out)
    return file_id, filename, name

def delete_file(dst_dir: str, filename: str) -> None:
    p = Path(dst_dir) / filename
    if p.exists():
        p.unlink()
