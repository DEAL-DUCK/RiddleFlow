from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
    AsyncEngine,
)

from core.config import settings


class DatabaseHelper:
    def __init__(
        self,
        url: str,
        echo: bool = False,
        echo_pool: bool = False,
        max_overflow: int = 10,
        pool_size: int = 5,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
    ):
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            max_overflow=max_overflow,
            pool_size=pool_size,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def get_scoped_session(self):
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        return session

    async def dispose(self):
        await self.engine.dispose()

    async def session_getter(self) -> AsyncSession:
        async with self.session_factory() as session:
            yield session


db_helper = DatabaseHelper(
    url=str(settings.db.url),
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    max_overflow=settings.db.max_overflow,
    pool_size=settings.db.pool_size,
    pool_timeout=settings.db.pool_timeout,
    pool_recycle=settings.db.pool_recycle,
)
