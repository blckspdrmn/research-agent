import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

import models
from auth import get_current_user
from database import get_db

CurrentUser = Annotated[models.User, Depends(get_current_user)]


async def get_owned_theme(
    theme_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_db)],
    user: CurrentUser,
) -> models.Theme:
    """無い場合も他人のものも同じ404にする（データの存在を知らせないため）"""
    theme = await db.get(models.Theme, theme_id)
    if theme is None or theme.user_id != user.id:
        raise HTTPException(404, "Theme not found")
    return theme


OwnedTheme = Annotated[models.Theme, Depends(get_owned_theme)]
