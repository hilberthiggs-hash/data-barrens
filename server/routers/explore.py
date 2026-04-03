import random
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.db import get_db
from server.models import Player
from server.schemas import EquipmentOut, RARITY_NAMES
from server.services.player_service import consume_stamina
from server.services.explore_service import explore
from server.auth import get_current_player
from server.game_data.lore import EXPLORE_TEXTS
from server.config import EXPLORE_STAMINA_COST

router = APIRouter(prefix="/api/explore", tags=["explore"])


class ExploreResult(BaseModel):
    narrative: str
    equipment: EquipmentOut
    stamina_remaining: int


@router.post("", response_model=ExploreResult)
def api_explore(db: Session = Depends(get_db), me: Player = Depends(get_current_player)):
    consume_stamina(db, me, EXPLORE_STAMINA_COST)
    equip = explore(db, me)

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
        stamina_remaining=me.stamina,
    )
