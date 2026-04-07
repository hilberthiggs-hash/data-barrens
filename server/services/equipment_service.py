from itertools import product

from sqlalchemy.orm import Session

from server.models import Player, Equipment
from server.config import MERGE_REQUIRED
from server.game_data.equipment import RARITY_MULTIPLIER, TEMPLATE_MAP, get_active_set_bonuses


def _item_stats(e: Equipment) -> int:
    return e.str_bonus + e.agi_bonus + e.int_bonus + e.vit_bonus


def _combo_score(combo: dict[str, Equipment | None]) -> int:
    """计算一组装备的总属性（含套装加成）"""
    total = 0
    tids = []
    for item in combo.values():
        if item:
            total += _item_stats(item)
            tids.append(item.template_id)

    for _, sb in get_active_set_bonuses(tids):
        total += sb.str_bonus + sb.agi_bonus + sb.int_bonus + sb.vit_bonus

    return total


def auto_equip_best(db: Session, player: Player) -> list[str]:
    """自动穿戴最优装备组合（考虑套装加成）。枚举所有组合取总分最高。"""
    from server.schemas import RARITY_NAMES

    # 按槽位分组
    by_slot: dict[str, list[Equipment]] = {"weapon": [], "armor": [], "accessory": []}
    for e in player.equipments:
        if e.slot in by_slot:
            by_slot[e.slot].append(e)

    # 每个槽位的候选列表（无装备的槽位用 [None]）
    candidates = {
        slot: items if items else [None]
        for slot, items in by_slot.items()
    }

    # 枚举所有组合，找总分最高的
    best_score = -1
    best_combo: dict[str, Equipment | None] = {}
    for w, a, acc in product(candidates["weapon"], candidates["armor"], candidates["accessory"]):
        combo = {"weapon": w, "armor": a, "accessory": acc}
        score = _combo_score(combo)
        if score > best_score:
            best_score = score
            best_combo = combo

    # 应用最优组合
    changes = []
    for slot in ("weapon", "armor", "accessory"):
        best_item = best_combo.get(slot)
        current = next((e for e in by_slot[slot] if e.equipped), None)

        if best_item is None:
            continue
        if current and current.id == best_item.id:
            continue

        if current:
            current.equipped = False
        best_item.equipped = True

        if current:
            changes.append(f"{slot}: [{RARITY_NAMES[current.rarity]}]{current.name} → [{RARITY_NAMES[best_item.rarity]}]{best_item.name}")
        else:
            changes.append(f"{slot}: 穿戴 [{RARITY_NAMES[best_item.rarity]}]{best_item.name}")

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
