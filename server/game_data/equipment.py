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


# ── 武器（基础） ──
WEAPONS = [
    EquipmentTemplate("wpn_iron_sword", "铁剑", "weapon", "朴实的铁剑，力量之源", 8, 2, 0, 0, 30),
    EquipmentTemplate("wpn_shadow_dagger", "暗影匕首", "weapon", "轻盈的暗杀利器", 2, 8, 0, 0, 30),
    EquipmentTemplate("wpn_arcane_staff", "奥术法杖", "weapon", "蕴含数据碎片的法杖", 0, 0, 10, 0, 30),
    EquipmentTemplate("wpn_war_hammer", "战锤", "weapon", "沉重的锤击，力量与体质并重", 6, 0, 0, 4, 20),
    EquipmentTemplate("wpn_void_blade", "虚空之刃", "weapon", "从荒原深处挖出的神秘武器", 5, 5, 5, 0, 10),
    # ── 烈焰套 ──
    EquipmentTemplate("wpn_flame_greatsword", "烈焰巨剑", "weapon", "燃烧着荒原余烬的大剑", 10, 0, 2, 0, 15),
    # ── 暗影套 ──
    EquipmentTemplate("wpn_shadow_fangs", "暗影双牙", "weapon", "从暗影数据流中凝聚的双刃", 0, 10, 0, 2, 15),
    # ── 冰霜套 ──
    EquipmentTemplate("wpn_frost_scepter", "冰霜权杖", "weapon", "冻结一切运行进程的权杖", 0, 2, 10, 0, 15),
    # ── 守护套 ──
    EquipmentTemplate("wpn_guardian_mace", "守护圣锤", "weapon", "守护者之力凝结的战锤", 4, 0, 0, 8, 15),
    # ── 混沌套 ──
    EquipmentTemplate("wpn_chaos_edge", "混沌之锋", "weapon", "荒原深层数据扭曲而成", 4, 4, 4, 2, 8),
]

# ── 护甲（基础） ──
ARMORS = [
    EquipmentTemplate("arm_leather", "皮甲", "armor", "轻便灵活的皮制护甲", 0, 4, 0, 6, 30),
    EquipmentTemplate("arm_plate", "板甲", "armor", "厚重的金属护甲", 2, 0, 0, 10, 25),
    EquipmentTemplate("arm_robe", "法师长袍", "armor", "增幅法力的丝绸长袍", 0, 0, 8, 4, 25),
    EquipmentTemplate("arm_shadow_cloak", "暗影斗篷", "armor", "若隐若现的斗篷", 0, 8, 2, 2, 20),
    EquipmentTemplate("arm_data_shell", "数据外壳", "armor", "以荒原碎片编织的护甲", 3, 3, 3, 3, 10),
    # ── 烈焰套 ──
    EquipmentTemplate("arm_flame_cuirass", "烈焰胸甲", "armor", "灼热的锻铁护甲，力量之源", 6, 0, 0, 6, 15),
    # ── 暗影套 ──
    EquipmentTemplate("arm_shadow_vest", "暗影轻甲", "armor", "几乎无重的暗影编织", 0, 8, 0, 4, 15),
    # ── 冰霜套 ──
    EquipmentTemplate("arm_frost_mantle", "冰霜法袍", "armor", "冰晶数据编织的法师袍", 0, 0, 8, 4, 15),
    # ── 守护套 ──
    EquipmentTemplate("arm_guardian_fortress", "守护壁垒", "armor", "移动的堡垒，坚不可摧", 0, 0, 0, 14, 12),
    # ── 混沌套 ──
    EquipmentTemplate("arm_chaos_membrane", "混沌薄膜", "armor", "在四种属性间闪烁的防护层", 3, 3, 3, 4, 8),
]

# ── 饰品（基础） ──
ACCESSORIES = [
    EquipmentTemplate("acc_power_ring", "力量戒指", "accessory", "增幅力量的戒指", 6, 0, 0, 0, 30),
    EquipmentTemplate("acc_swift_boots", "疾风靴", "accessory", "脚下生风", 0, 6, 0, 0, 30),
    EquipmentTemplate("acc_wisdom_amulet", "智慧护符", "accessory", "古老的数据护符", 0, 0, 6, 0, 30),
    EquipmentTemplate("acc_vitality_belt", "活力腰带", "accessory", "坚韧不拔", 0, 0, 0, 6, 30),
    EquipmentTemplate("acc_chaos_gem", "混沌宝石", "accessory", "荒原核心凝结的宝石", 3, 3, 3, 3, 10),
    # ── 烈焰套 ──
    EquipmentTemplate("acc_flame_pendant", "烈焰坠饰", "accessory", "封印着荒原余火的挂坠", 5, 0, 2, 0, 15),
    # ── 暗影套 ──
    EquipmentTemplate("acc_shadow_earring", "暗影耳环", "accessory", "窃取数据片段的暗影饰品", 0, 5, 0, 2, 15),
    # ── 冰霜套 ──
    EquipmentTemplate("acc_frost_crystal", "冰霜水晶", "accessory", "永不融化的数据结晶", 0, 0, 5, 2, 15),
    # ── 守护套 ──
    EquipmentTemplate("acc_guardian_shield_charm", "守护盾符", "accessory", "微缩护盾凝结的符文", 0, 0, 0, 8, 15),
    # ── 混沌套 ──
    EquipmentTemplate("acc_chaos_prism", "混沌棱镜", "accessory", "折射出四色数据光芒", 2, 2, 2, 3, 8),
]

ALL_TEMPLATES = WEAPONS + ARMORS + ACCESSORIES
TEMPLATE_MAP = {t.id: t for t in ALL_TEMPLATES}

# 稀有度倍率：白0 x1, 绿1 x1.5, 蓝2 x2, 紫3 x3, 橙4 x4.5
RARITY_MULTIPLIER = [1.0, 1.5, 2.0, 3.0, 4.5]


# ── 套装系统 ──
# 模板ID前缀 → 套装名
SET_PREFIXES = {
    "flame": "烈焰套装",
    "shadow": "暗影套装",
    "frost": "冰霜套装",
    "guardian": "守护套装",
    "chaos": "混沌套装",
}

# 套装内的模板ID列表（每套 3 件：武器+护甲+饰品）
SET_MEMBERS = {
    "flame": {"wpn_flame_greatsword", "arm_flame_cuirass", "acc_flame_pendant"},
    "shadow": {"wpn_shadow_fangs", "arm_shadow_vest", "acc_shadow_earring"},
    "frost": {"wpn_frost_scepter", "arm_frost_mantle", "acc_frost_crystal"},
    "guardian": {"wpn_guardian_mace", "arm_guardian_fortress", "acc_guardian_shield_charm"},
    "chaos": {"wpn_chaos_edge", "arm_chaos_membrane", "acc_chaos_prism"},
}

@dataclass(frozen=True)
class SetBonus:
    pieces: int          # 需要装备几件
    str_bonus: int = 0
    agi_bonus: int = 0
    int_bonus: int = 0
    vit_bonus: int = 0
    description: str = ""

# 套装效果定义：2 件和 3 件的加成
SET_BONUSES = {
    "flame": [
        SetBonus(2, str_bonus=5, description="烈焰之力：力量 +5"),
        SetBonus(3, str_bonus=8, int_bonus=3, description="烈焰觉醒：力量 +8, 智力 +3, 暴击伤害 +20%"),
    ],
    "shadow": [
        SetBonus(2, agi_bonus=5, description="暗影步伐：敏捷 +5"),
        SetBonus(3, agi_bonus=8, str_bonus=3, description="暗影融合：敏捷 +8, 力量 +3, 暴击率 +10%"),
    ],
    "frost": [
        SetBonus(2, int_bonus=5, description="冰霜之智：智力 +5"),
        SetBonus(3, int_bonus=8, vit_bonus=3, description="冰霜掌控：智力 +8, 体质 +3, 法术穿透 +15%"),
    ],
    "guardian": [
        SetBonus(2, vit_bonus=5, description="守护之盾：体质 +5"),
        SetBonus(3, vit_bonus=8, str_bonus=3, description="守护壁垒：体质 +8, 力量 +3, 减伤 +10%"),
    ],
    "chaos": [
        SetBonus(2, str_bonus=3, agi_bonus=3, int_bonus=3, vit_bonus=3, description="混沌共鸣：全属性 +3"),
        SetBonus(3, str_bonus=5, agi_bonus=5, int_bonus=5, vit_bonus=5, description="混沌核心：全属性 +5, 全抗性 +10%"),
    ],
}


def get_active_set_bonuses(equipped_template_ids: list[str]) -> list[tuple[str, SetBonus]]:
    """根据已装备的模板ID列表，返回已激活的套装效果"""
    active = []
    tid_set = set(equipped_template_ids)
    for set_key, members in SET_MEMBERS.items():
        count = len(tid_set & members)
        for bonus in SET_BONUSES.get(set_key, []):
            if count >= bonus.pieces:
                active.append((set_key, bonus))
    return active
