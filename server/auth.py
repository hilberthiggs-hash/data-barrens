"""API Token 认证"""
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session

from server.db import get_db
from server.models import Player


def get_current_player(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
) -> Player:
    """从 Authorization header 解析 token，返回当前玩家"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少认证 token，请在 Header 中添加 Authorization: Bearer <token>")

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="无效的 token 格式")

    player = db.query(Player).filter(Player.api_token == token).first()
    if not player:
        raise HTTPException(status_code=401, detail="token 无效或已过期")

    return player
