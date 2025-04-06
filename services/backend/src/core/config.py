from pathlib import Path
from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent

DB_PATH = BASE_DIR / "db.sqlite3"


class ApiPrefix(BaseModel):
    prefix: str = "/api"


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class DbSettings(BaseModel):
    url: PostgresDsn


class Settings(BaseSettings):
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DbSettings


settings = Settings()
