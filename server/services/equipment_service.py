from sqlalchemy.orm import Session

from server.models import Player, Equipment
from server.config import MERGE_REQUIRED
from server.game_data.equipment import RARITY_MULTIPLIER, TEMPLATE_MAP


def _equip_score(e: Equipment) -> int:
    """装备总属性加成，用于择优"""
    return e.str_bonus + e.agi_bonus + e.int_bonus + e.vit_bonus


def auto_equip_best(db: Session, player: Player) -> list[str]:
    """自动为每个槽位穿戴总属性最高的装备。返回变更描述列表。"""
    changes = []
    for slot in ("weapon", "armor", "accessory"):
        all_in_slot = [e for e in player.equipments if e.slot == slot]
        if not all_in_slot:
            continue

        best = max(all_in_slot, key=_equip_score)
        current = next((e for e in all_in_slot if e.equipped), None)

        if current and current.id == best.id:
            continue  # 已经是最好的

        if current:
            current.equipped = False
        best.equipped = True

        from server.schemas import RARITY_NAMES
        if current:
            changes.append(f"{slot}: [{RARITY_NAMES[current.rarity]}]{current.name} → [{RARITY_NAMES[best.rarity]}]{best.name}")
        else:
            changes.append(f"{slot}: 穿戴 [{RARITY_NAMES[best.rarity]}]{best.name}")

    if changes:
        db.commit()
    return changes


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
