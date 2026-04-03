import random
from sqlalchemy.orm import Session

from server.models import Player, Equipment
from server.game_data.equipment import ALL_TEMPLATES, RARITY_MULTIPLIER, EquipmentTemplate


# 稀有度掉落概率
RARITY_WEIGHTS = [50, 25, 15, 8, 2]  # 白/绿/蓝/紫/橙


def explore(db: Session, player: Player) -> Equipment:
    """执行一次探索，返回获得的装备"""
    # 按权重随机选择模板
    templates = ALL_TEMPLATES
    weights = [t.drop_weight for t in templates]
    template: EquipmentTemplate = random.choices(templates, weights=weights, k=1)[0]

    # 随机稀有度
    rarity: int = random.choices(range(5), weights=RARITY_WEIGHTS, k=1)[0]
    multiplier = RARITY_MULTIPLIER[rarity]

    equip = Equipment(
        player_id=player.id,
        template_id=template.id,
        name=template.name,
        slot=template.slot,
        rarity=rarity,
        str_bonus=int(template.str_bonus * multiplier),
        agi_bonus=int(template.agi_bonus * multiplier),
        int_bonus=int(template.int_bonus * multiplier),
        vit_bonus=int(template.vit_bonus * multiplier),
        equipped=False,
    )
    db.add(equip)
    db.commit()
    db.refresh(equip)
    return equip
