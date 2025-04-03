from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent
KEY_DIR = Path(__file__).parent.parent.parent.parent.parent
DB_PATH = BASE_DIR / "db.sqlite3"


class DbSettings(BaseModel):
    url: str = f"sqlite+aiosqlite:///{DB_PATH}"
    echo: bool = False

JWT_CONFIG = {
    "ALGORITHM": "RS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
    "REFRESH_TOKEN_EXPIRE_DAYS": 7
}
class Settings(BaseSettings):
    db: DbSettings = DbSettings()

    # db_echo: bool = True

settings = Settings()
