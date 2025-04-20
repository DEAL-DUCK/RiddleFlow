import uuid
from pathlib import Path

from fastapi import UploadFile

UPLOADS_DIR = "static/covers"
Path(UPLOADS_DIR).mkdir(parents=True, exist_ok=True)


async def save_cover(file: UploadFile) -> str:
    # Проверка типа файла
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise ValueError("Only JPEG/PNG images allowed")

    # Генерация имени файла
    file_ext = file.filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = f"{UPLOADS_DIR}/{filename}"

    # Сохранение
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return filename