import random
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.db import get_db
from server.models import Player
from server.schemas import EquipmentOut, RARITY_NAMES
from server.services.player_service import get_player, consume_stamina
from server.services.explore_service import explore
from server.game_data.lore import EXPLORE_TEXTS
from server.config import EXPLORE_STAMINA_COST

router = APIRouter(prefix="/api/explore", tags=["explore"])


class ExploreResult(BaseModel):
    narrative: str
    equipment: EquipmentOut


@router.post("/{player_id}", response_model=ExploreResult)
def api_explore(player_id: int, db: Session = Depends(get_db)):
    player = get_player(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="玩家不存在")

    consume_stamina(db, player, EXPLORE_STAMINA_COST)
    equip = explore(db, player)

    narrative = random.choice(EXPLORE_TEXTS)
    rarity_name = RARITY_NAMES[equip.rarity]
    narrative += f"\n发现了 [{rarity_name}] {equip.name}！"

    return ExploreResult(
        narrative=narrative,
        equipment=EquipmentOut(
            id=equip.id,
            template_id=equip.template_id,
            name=equip.name,
            slot=equip.slot,
            rarity=equip.rarity,
            rarity_name=rarity_name,
            str_bonus=equip.str_bonus,
            agi_bonus=equip.agi_bonus,
            int_bonus=equip.int_bonus,
            vit_bonus=equip.vit_bonus,
            equipped=equip.equipped,
        ),
    )
