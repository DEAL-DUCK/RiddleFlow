from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent
KEY_DIR = Path(__file__).parent.parent.joinpath('api_v1').joinpath('auth')
DB_PATH = BASE_DIR / "db.sqlite3"


class DbSettings(BaseModel):
    url: str = f"sqlite+aiosqlite:///{DB_PATH}"
    echo: bool = False
class AuthJWT(BaseModel):
    private_key_path: Path =  KEY_DIR / "keys" / "private_key.pem"
    public_key_path: Path =  KEY_DIR / "keys" / "public_key.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15

class Settings(BaseSettings):
    db: DbSettings = DbSettings()
    auth_jwt : AuthJWT = AuthJWT()
    # db_echo: bool = True

settings = Settings()
