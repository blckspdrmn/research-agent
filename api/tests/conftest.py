import httpx
import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import models
from auth import get_current_user
from config import settings
from database import get_db
from main import app

TEST_DB_URL = settings.test_database_url

if TEST_DB_URL is None:
    raise RuntimeError("TEST_DATABASE_URLが未設定です。api/.envを確認してください")

# 異なるDBの操作を防ぐ
if not TEST_DB_URL.endswith("_test"):
    raise RuntimeError(f"テスト用DBではありません: {TEST_DB_URL}")


@pytest.fixture
async def db():
    engine = create_async_engine(TEST_DB_URL)

    # 毎テストまっさらな状態から始める
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)
        await conn.run_sync(models.Base.metadata.create_all)

    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        # 所有チェックのテスト用。JWTの検証自体はここでは扱わない
        user = models.User(entra_issuer="https://test.example", entra_sub="test-user")
        session.add(user)
        await session.commit()

        app.dependency_overrides[get_db] = lambda: session
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            yield session
        finally:
            app.dependency_overrides.clear()

    await engine.dispose()


@pytest.fixture
async def client(db):  # dbを引数に取ることで、先にDBの準備が走る
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
