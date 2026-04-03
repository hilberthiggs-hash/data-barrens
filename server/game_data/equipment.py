from dataclasses import dataclass


@dataclass(frozen=True)
class EquipmentTemplate:
    id: str
    name: str
    slot: str       # weapon / armor / accessory
    description: str
    str_bonus: int
    agi_bonus: int
    int_bonus: int
    vit_bonus: int
    drop_weight: int  # 掉落权重，越高越容易掉


# ── 武器 ──
WEAPONS = [
    EquipmentTemplate("wpn_iron_sword", "铁剑", "weapon", "朴实的铁剑，力量之源", 8, 2, 0, 0, 30),
    EquipmentTemplate("wpn_shadow_dagger", "暗影匕首", "weapon", "轻盈的暗杀利器", 2, 8, 0, 0, 30),
    EquipmentTemplate("wpn_arcane_staff", "奥术法杖", "weapon", "蕴含数据碎片的法杖", 0, 0, 10, 0, 30),
    EquipmentTemplate("wpn_war_hammer", "战锤", "weapon", "沉重的锤击，力量与体质并重", 6, 0, 0, 4, 20),
    EquipmentTemplate("wpn_void_blade", "虚空之刃", "weapon", "从荒原深处挖出的神秘武器", 5, 5, 5, 0, 10),
]

# ── 护甲 ──
ARMORS = [
    EquipmentTemplate("arm_leather", "皮甲", "armor", "轻便灵活的皮制护甲", 0, 4, 0, 6, 30),
    EquipmentTemplate("arm_plate", "板甲", "armor", "厚重的金属护甲", 2, 0, 0, 10, 25),
    EquipmentTemplate("arm_robe", "法师长袍", "armor", "增幅法力的丝绸长袍", 0, 0, 8, 4, 25),
    EquipmentTemplate("arm_shadow_cloak", "暗影斗篷", "armor", "若隐若现的斗篷", 0, 8, 2, 2, 20),
    EquipmentTemplate("arm_data_shell", "数据外壳", "armor", "以荒原碎片编织的护甲", 3, 3, 3, 3, 10),
]

# ── 饰品 ──
ACCESSORIES = [
    EquipmentTemplate("acc_power_ring", "力量戒指", "accessory", "增幅力量的戒指", 6, 0, 0, 0, 30),
    EquipmentTemplate("acc_swift_boots", "疾风靴", "accessory", "脚下生风", 0, 6, 0, 0, 30),
    EquipmentTemplate("acc_wisdom_amulet", "智慧护符", "accessory", "古老的数据护符", 0, 0, 6, 0, 30),
    EquipmentTemplate("acc_vitality_belt", "活力腰带", "accessory", "坚韧不拔", 0, 0, 0, 6, 30),
    EquipmentTemplate("acc_chaos_gem", "混沌宝石", "accessory", "荒原核心凝结的宝石", 3, 3, 3, 3, 10),
]

ALL_TEMPLATES = WEAPONS + ARMORS + ACCESSORIES
TEMPLATE_MAP = {t.id: t for t in ALL_TEMPLATES}

# 稀有度倍率：白0 x1, 绿1 x1.5, 蓝2 x2, 紫3 x3, 橙4 x4.5
RARITY_MULTIPLIER = [1.0, 1.5, 2.0, 3.0, 4.5]
