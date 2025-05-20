from contextlib import asynccontextmanager

import redis
from aiobotocore.session import get_session
from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunConfig(BaseModel):
    host: str
    port: int


class DbSettings(BaseModel):
    url: PostgresDsn
    echo: bool
    echo_pool: bool
    max_overflow: int
    pool_size: int
    pool_timeout: int
    pool_recycle: int

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class AccessToken(BaseModel):
    lifetime_seconds: int
    reset_password_token_secret: str
    verification_token_secret: str


class RedisConfig(BaseModel):
    redis_host: str
    redis_port: str
    redis_db: str


class CeleryConfig(BaseModel):
    celery_main: str
    celery_broker: str
    celery_backend: str


class S3Config(BaseModel):
    access_key: str
    secret_key: str
    endpoint_url: str
    bucket_name: str
    domain_url: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig
    redis: RedisConfig
    celery: CeleryConfig
    s3: S3Config
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
    host=settings.redis.redis_host,
    port=settings.redis.redis_port,
    db=settings.redis.redis_db,
    decode_responses=True,
)

s3_client = S3Client(
    access_key=settings.s3.access_key,
    secret_key=settings.s3.secret_key,
    endpoint_url=settings.s3.endpoint_url,
    bucket_name=settings.s3.bucket_name,
)
