from pathlib import Path
from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
import redis


class ApiPrefix(BaseModel):
    prefix: str = "/api"


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class DbSettings(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    max_overflow: int = 10
    pool_size: int = 50
    pool_timeout: int = 30
    pool_recycle: int = 3600

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class AccessToken(BaseModel):
    lifetime_seconds: int = 3600000  # ПОМЕНЯТЬ ПРИ СОЗДАНИИ REFRESH JWT
    reset_password_token_secret: str
    verification_token_secret: str


class RedisConfig:
    REDIS_HOST = "redis_cache"
    REDIS_PORT = 6379
    REDIS_DB = 0


class CeleryConfig:
    CELERY_MAIN = "tasks"
    CELERY_BROKER = "redis://redis_celery:6379/0"
    CELERY_BACKEND = "redis://redis_celery:6379/0"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env.local"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    redis: RedisConfig = RedisConfig()
    celery: CeleryConfig = CeleryConfig()
    db: DbSettings
    access_token: AccessToken


settings = Settings()

redis_client = redis.StrictRedis(
    host=settings.redis.REDIS_HOST,
    port=settings.redis.REDIS_PORT,
    db=settings.redis.REDIS_DB,
    decode_responses=True,
)
