from contextlib import asynccontextmanager

from aiobotocore.session import get_session
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


class S3Config(BaseModel):
    access_key: str = "7a55abe43bf44246938f347062ea1a5f"
    secret_key: str = "904deb287fc7447a86f103c89ed2a462"
    endpoint_url: str = "https://s3.ru-7.storage.selcloud.ru"
    bucket_name: str = "riddle-flow-public-bucket"
    domain_url: str = "https://8111c3e1-45b1-4f66-a978-cc168f520971.selstorage.ru"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.template", ".env.local"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    redis: RedisConfig = RedisConfig()
    celery: CeleryConfig = CeleryConfig()
    s3: S3Config = S3Config()
    db: DbSettings
    access_token: AccessToken


class S3Client:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        endpoint_url: str,
        bucket_name: str,
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(
        self,
        file_path: str,
    ):
        object_name = file_path.split("/")[-1]
        async with self.get_client() as client:
            with open(file_path, "rb") as file:
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=object_name,
                    Body=file,
                )


settings = Settings()

redis_client = redis.StrictRedis(
    host=settings.redis.REDIS_HOST,
    port=settings.redis.REDIS_PORT,
    db=settings.redis.REDIS_DB,
    decode_responses=True,
)

s3_client = S3Client(
    access_key=settings.s3.access_key,
    secret_key=settings.s3.secret_key,
    endpoint_url=settings.s3.endpoint_url,
    bucket_name=settings.s3.bucket_name,
)
