from dataclasses import dataclass


@dataclass(frozen=True)
class SkillDef:
    id: str
    name: str
    description: str
    stat: str        # 主属性：str/agi/int/vit
    unlock_level: int
    damage_base: int
    damage_scale: float   # 伤害 = damage_base + stat_value * damage_scale
    effect: str | None = None  # 特殊效果标识


# STR 系
HEAVY_STRIKE = SkillDef("heavy_strike", "重击", "全力一击，造成高额物理伤害", "str", 3, 15, 1.5)
ARMOR_BREAK = SkillDef("armor_break", "破甲", "撕裂防御，降低目标 30% 防御持续 2 回合", "str", 8, 10, 1.2, "def_down")
BERSERK = SkillDef("berserk", "狂暴", "燃烧生命，攻击力提升 50% 持续 3 回合", "str", 15, 5, 0.8, "atk_up")

# AGI 系
DODGE = SkillDef("dodge", "闪避", "灵巧身法，本回合 40% 概率闪避攻击", "agi", 3, 0, 0.0, "dodge")
COMBO = SkillDef("combo", "连击", "高速双击，每次伤害较低但命中两次", "agi", 8, 8, 1.0, "double_hit")
ASSASSINATE = SkillDef("assassinate", "暗杀", "致命打击，对 HP<30% 的目标伤害翻倍", "agi", 15, 20, 1.8, "execute")

# INT 系
FIREBALL = SkillDef("fireball", "火球", "凝聚火焰球，造成法术伤害", "int", 3, 18, 1.6)
FREEZE = SkillDef("freeze", "冰冻", "冻结目标，30% 概率使目标下回合无法行动", "int", 8, 12, 1.3, "stun")
ANNIHILATE = SkillDef("annihilate", "湮灭", "释放毁灭能量，无视 50% 防御", "int", 15, 25, 2.0, "ignore_def")

# VIT 系
BLOCK = SkillDef("block", "格挡", "硬抗伤害，本回合减伤 40%", "vit", 3, 0, 0.0, "block")
THORNS = SkillDef("thorns", "反伤", "荆棘之躯，反弹受到伤害的 30%", "vit", 8, 0, 0.0, "reflect")
REGENERATE = SkillDef("regenerate", "再生", "生命恢复，回复 15% 最大 HP", "vit", 15, 0, 0.0, "heal")


SKILLS = [
    HEAVY_STRIKE, ARMOR_BREAK, BERSERK,
    DODGE, COMBO, ASSASSINATE,
    FIREBALL, FREEZE, ANNIHILATE,
    BLOCK, THORNS, REGENERATE,
]

SKILL_MAP = {s.id: s for s in SKILLS}
