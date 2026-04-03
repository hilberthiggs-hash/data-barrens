from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.db import get_db
from server.models import Player, Equipment
from server.schemas import EquipmentOut, MessageOut, RARITY_NAMES
from server.services.player_service import get_player
from server.services.equipment_service import equip_item, unequip_item, merge_equipment
from server.auth import get_current_player

router = APIRouter(prefix="/api/equipment", tags=["equipment"])


def _equip_to_out(e: Equipment) -> EquipmentOut:
    return EquipmentOut(
        id=e.id, template_id=e.template_id, name=e.name, slot=e.slot,
        rarity=e.rarity, rarity_name=RARITY_NAMES[e.rarity],
        str_bonus=e.str_bonus, agi_bonus=e.agi_bonus,
        int_bonus=e.int_bonus, vit_bonus=e.vit_bonus,
        equipped=e.equipped,
    )


# 读接口：公开
@router.get("/{player_id}/list", response_model=list[EquipmentOut])
def api_list_equipment(player_id: int, db: Session = Depends(get_db)):
    player = get_player(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="玩家不存在")
    return [_equip_to_out(e) for e in player.equipments]


# 写接口：需认证
@router.post("/equip", response_model=EquipmentOut)
def api_equip(equipment_id: int, db: Session = Depends(get_db), me: Player = Depends(get_current_player)):
    try:
        equip = equip_item(db, me, equipment_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _equip_to_out(equip)


@router.post("/unequip", response_model=EquipmentOut)
def api_unequip(equipment_id: int, db: Session = Depends(get_db), me: Player = Depends(get_current_player)):
    try:
        equip = unequip_item(db, me, equipment_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _equip_to_out(equip)


class MergeRequest(BaseModel):
    template_id: str
    rarity: int


@router.post("/merge", response_model=EquipmentOut)
def api_merge(data: MergeRequest, db: Session = Depends(get_db), me: Player = Depends(get_current_player)):
    try:
        equip = merge_equipment(db, me, data.template_id, data.rarity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _equip_to_out(equip)
