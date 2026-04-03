from sqlalchemy.orm import Session

from server.models import Player, Equipment
from server.config import MERGE_REQUIRED
from server.game_data.equipment import RARITY_MULTIPLIER, TEMPLATE_MAP


def equip_item(db: Session, player: Player, equipment_id: int) -> Equipment:
    equip = db.query(Equipment).filter(
        Equipment.id == equipment_id,
        Equipment.player_id == player.id,
    ).first()
    if not equip:
        raise ValueError("装备不存在")
    if equip.equipped:
        raise ValueError("已经装备了")

    # 卸下同槽位已装备的
    current = db.query(Equipment).filter(
        Equipment.player_id == player.id,
        Equipment.slot == equip.slot,
        Equipment.equipped == True,
    ).first()
    if current:
        current.equipped = False

    equip.equipped = True
    db.commit()
    db.refresh(equip)
    return equip


def unequip_item(db: Session, player: Player, equipment_id: int) -> Equipment:
    equip = db.query(Equipment).filter(
        Equipment.id == equipment_id,
        Equipment.player_id == player.id,
    ).first()
    if not equip:
        raise ValueError("装备不存在")
    if not equip.equipped:
        raise ValueError("这件装备没有穿戴")

    equip.equipped = False
    db.commit()
    db.refresh(equip)
    return equip


def merge_equipment(db: Session, player: Player, template_id: str, rarity: int) -> Equipment:
    """合成：3 个同名同稀有度 → 1 个高一级稀有度"""
    if rarity >= 4:
        raise ValueError("橙色装备已是最高品质，无法合成")

    candidates = db.query(Equipment).filter(
        Equipment.player_id == player.id,
        Equipment.template_id == template_id,
        Equipment.rarity == rarity,
        Equipment.equipped == False,
    ).all()

    if len(candidates) < MERGE_REQUIRED:
        raise ValueError(f"需要 {MERGE_REQUIRED} 个同名同稀有度未装备的装备，当前只有 {len(candidates)} 个")

    template = TEMPLATE_MAP.get(template_id)
    if not template:
        raise ValueError("装备模板不存在")

    # 消耗材料
    for c in candidates[:MERGE_REQUIRED]:
        db.delete(c)

    # 生成高一级
    new_rarity = rarity + 1
    multiplier = RARITY_MULTIPLIER[new_rarity]
    new_equip = Equipment(
        player_id=player.id,
        template_id=template_id,
        name=template.name,
        slot=template.slot,
        rarity=new_rarity,
        str_bonus=int(template.str_bonus * multiplier),
        agi_bonus=int(template.agi_bonus * multiplier),
        int_bonus=int(template.int_bonus * multiplier),
        vit_bonus=int(template.vit_bonus * multiplier),
        equipped=False,
    )
    db.add(new_equip)
    db.commit()
    db.refresh(new_equip)
    return new_equip
