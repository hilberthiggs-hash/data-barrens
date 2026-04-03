from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from server.db import get_db
from server.models import Notification
from server.schemas import PlayerRegister, AllocatePoints, PlayerOut, MessageOut
from server.auth import get_current_player
from server.services.player_service import (
    register_player, get_player, get_player_by_name, get_player_by_email,
    allocate_points, refresh_stamina, to_player_out,
)

router = APIRouter(prefix="/api/player", tags=["player"])


@router.post("/register")
def api_register(data: PlayerRegister, db: Session = Depends(get_db)):
    try:
        player = register_player(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    out = to_player_out(player).model_dump(mode="json", by_alias=True)
    out["api_token"] = player.api_token  # 仅注册时返回 token
    return out


@router.get("/{player_id}", response_model=PlayerOut)
def api_get_player(player_id: int, db: Session = Depends(get_db)):
    player = get_player(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="玩家不存在")
    refresh_stamina(db, player)
    return to_player_out(player)


@router.get("/by-name/{name}", response_model=PlayerOut)
def api_get_player_by_name(name: str, db: Session = Depends(get_db)):
    player = get_player_by_name(db, name)
    if not player:
        raise HTTPException(status_code=404, detail="玩家不存在")
    refresh_stamina(db, player)
    return to_player_out(player)


@router.get("/by-email/{email:path}", response_model=PlayerOut)
def api_get_player_by_email(email: str, db: Session = Depends(get_db)):
    player = get_player_by_email(db, email)
    if not player:
        raise HTTPException(status_code=404, detail="该邮箱未注册角色")
    refresh_stamina(db, player)
    return to_player_out(player)


@router.get("/resolve-buddy/{user_id}")
def api_resolve_buddy(user_id: str):
    from server.services.buddy_resolver import resolve_buddy
    return resolve_buddy(user_id)


@router.post("/{player_id}/allocate", response_model=PlayerOut)
def api_allocate_points(player_id: int, data: AllocatePoints, db: Session = Depends(get_db)):
    try:
        player = allocate_points(db, player_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return to_player_out(player)


@router.get("/notifications/unread")
def api_get_notifications(db: Session = Depends(get_db), me: Player = Depends(get_current_player)):
    """获取未读通知并标记已读"""
    notifs = db.query(Notification).filter(
        Notification.player_id == me.id,
        Notification.read == False,
    ).order_by(Notification.created_at.desc()).all()

    messages = [n.message for n in notifs]

    # 标记已读
    for n in notifs:
        n.read = True
    db.commit()

    return {"notifications": messages}
