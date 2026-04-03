from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.db import get_db
from server.models import Player, PlayerSkill
from server.config import MAX_EQUIPPED_SKILLS
from server.game_data.skills import SKILL_MAP
from server.schemas import MessageOut

router = APIRouter(prefix="/api/skill", tags=["skill"])


class EquipSkillRequest(BaseModel):
    player_id: int
    skill_id: str
    equip: bool = True  # True=装备, False=卸下


class SkillOut(BaseModel):
    skill_id: str
    name: str
    description: str
    stat: str
    unlock_level: int
    equipped: bool


@router.get("/{player_id}/list", response_model=list[SkillOut])
def api_list_skills(player_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="玩家不存在")

    result = []
    for ps in player.skills:
        skill_def = SKILL_MAP.get(ps.skill_id)
        if skill_def:
            result.append(SkillOut(
                skill_id=ps.skill_id,
                name=skill_def.name,
                description=skill_def.description,
                stat=skill_def.stat,
                unlock_level=skill_def.unlock_level,
                equipped=ps.equipped,
            ))
    return result


@router.post("/equip", response_model=MessageOut)
def api_equip_skill(data: EquipSkillRequest, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == data.player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="玩家不存在")

    ps = db.query(PlayerSkill).filter(
        PlayerSkill.player_id == data.player_id,
        PlayerSkill.skill_id == data.skill_id,
    ).first()
    if not ps:
        raise HTTPException(status_code=400, detail="你还没有解锁这个技能")

    skill_def = SKILL_MAP.get(data.skill_id)
    skill_name = skill_def.name if skill_def else data.skill_id

    if data.equip:
        if ps.equipped:
            return MessageOut(message=f"「{skill_name}」已经装备了")
        equipped_count = db.query(PlayerSkill).filter(
            PlayerSkill.player_id == data.player_id,
            PlayerSkill.equipped == True,
        ).count()
        if equipped_count >= MAX_EQUIPPED_SKILLS:
            raise HTTPException(status_code=400, detail=f"最多装备 {MAX_EQUIPPED_SKILLS} 个技能")
        ps.equipped = True
        db.commit()
        return MessageOut(message=f"已装备「{skill_name}」")
    else:
        ps.equipped = False
        db.commit()
        return MessageOut(message=f"已卸下「{skill_name}」")
