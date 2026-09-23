import asyncio
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

import models
from config import settings
from database import get_db

# Entraの公開鍵取得用
jwks_client = jwt.PyJWKClient(settings.entra_jwks_url, timeout=10)


async def get_current_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> models.User:
    # Bearer: ey... の部分を分割
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            401, "Not authenticated", headers={"WWW-Authenticate": "Bearer"}
        )
    try:
        # 公開鍵の取得: 同期HTTPなので、イベントループを止めないよう別スレッドで待つ
        key = await asyncio.to_thread(jwks_client.get_signing_key_from_jwt, token)
        payload = jwt.decode(
            token,
            key.key,  # 署名を確認
            algorithms=["RS256"],  # 想定している署名方式を指定
            audience=settings.entra_api_client_id,  # このAPIアプリ宛かを確認
            issuer=settings.entra_issuer,  # テナントを確認
            options={"require": ["exp", "iss", "aud", "sub"]},
        )
    except jwt.PyJWKClientConnectionError as exc:
        # Entraに届かないのはトークンの問題ではないので401にしない
        raise HTTPException(503, "Authentication service unavailable") from exc
    except jwt.PyJWTError as exc:
        raise HTTPException(
            401, "Invalid token", headers={"WWW-Authenticate": "Bearer"}
        ) from exc

    scopes = payload.get("scp")
    if (
        not isinstance(scopes, str)
        or settings.entra_required_scope not in scopes.split()
    ):
        raise HTTPException(403, "Required scope is missing")
    issuer = payload["iss"]
    subject = payload["sub"]
    if not isinstance(subject, str) or not subject or len(subject) > 255:
        raise HTTPException(401, "Invalid subject")

    # 初回アクセス時にユーザーを作る。
    # 並列の初回リクエストでもunique制約で1行に収束させる
    await db.execute(
        insert(models.User)
        .values(entra_issuer=issuer, entra_sub=subject)
        .on_conflict_do_nothing(constraint="uq_users_entra_identity")
    )
    await db.commit()
    user = await db.scalar(
        select(models.User).where(
            models.User.entra_issuer == issuer,
            models.User.entra_sub == subject,
        )
    )
    if user is None:
        raise HTTPException(503, "User provisioning unavailable")
    request.state.user_id = str(user.id)  # rate_limit.pyがユーザー単位で数えるため
    return user
