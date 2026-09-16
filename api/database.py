from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import settings

engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,  # 本番Azure PostgresSQL用の接続チェック: https://qiita.com/Ryo-0131/items/821b98a6acf3fae3bb34
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with SessionLocal() as db:
        yield db
