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


# ── STR 系 ──
HEAVY_STRIKE = SkillDef("heavy_strike", "重击", "全力一击，造成高额物理伤害", "str", 3, 15, 1.5)
GROUND_SLAM = SkillDef("ground_slam", "震地", "重锤大地，震荡波及周围数据", "str", 5, 12, 1.3, "aoe")
ARMOR_BREAK = SkillDef("armor_break", "破甲", "撕裂防御，降低目标 30% 防御持续 2 回合", "str", 8, 10, 1.2, "def_down")
WAR_CRY = SkillDef("war_cry", "战吼", "激励自身，攻击力提升 30% 并回复少量 HP", "str", 10, 8, 1.0, "atk_up")
BERSERK = SkillDef("berserk", "狂暴", "燃烧生命，攻击力提升 50% 持续 3 回合", "str", 15, 5, 0.8, "atk_up")
JUDGMENT = SkillDef("judgment", "末日审判", "凝聚全部力量的毁灭一击", "str", 20, 30, 2.2)

# ── AGI 系 ──
DODGE = SkillDef("dodge", "闪避", "灵巧身法，本回合 40% 概率闪避攻击", "agi", 3, 0, 0.0, "dodge")
POISON_BLADE = SkillDef("poison_blade", "毒刃", "淬毒攻击，目标持续失血 2 回合", "agi", 5, 10, 1.2, "dot")
COMBO = SkillDef("combo", "连击", "高速双击，每次伤害较低但命中两次", "agi", 8, 8, 1.0, "double_hit")
SHADOW_CLONE = SkillDef("shadow_clone", "影分身", "分身迷惑，50% 闪避并反击", "agi", 10, 5, 0.8, "dodge")
ASSASSINATE = SkillDef("assassinate", "暗杀", "致命打击，对 HP<30% 的目标伤害翻倍", "agi", 15, 20, 1.8, "execute")
FATAL_RHYTHM = SkillDef("fatal_rhythm", "致命节奏", "三连斩，每击递增伤害", "agi", 20, 10, 1.5, "triple_hit")

# ── INT 系 ──
FIREBALL = SkillDef("fireball", "火球", "凝聚火焰球，造成法术伤害", "int", 3, 18, 1.6)
CHAIN_LIGHTNING = SkillDef("chain_lightning", "闪电链", "弹射闪电，附带 20% 眩晕", "int", 5, 14, 1.4, "stun")
FREEZE = SkillDef("freeze", "冰冻", "冻结目标，30% 概率使目标下回合无法行动", "int", 8, 12, 1.3, "stun")
VOID_SHIELD = SkillDef("void_shield", "虚空护盾", "编织数据屏障，吸收伤害", "int", 10, 0, 0.0, "block")
ANNIHILATE = SkillDef("annihilate", "湮灭", "释放毁灭能量，无视 50% 防御", "int", 15, 25, 2.0, "ignore_def")
TIME_STOP = SkillDef("time_stop", "时间停止", "冻结时间线，目标必定无法行动", "int", 20, 15, 1.8, "stun")

# ── VIT 系 ──
BLOCK = SkillDef("block", "格挡", "硬抗伤害，本回合减伤 40%", "vit", 3, 0, 0.0, "block")
IRON_WALL = SkillDef("iron_wall", "铁壁", "铜墙铁壁，本回合减伤 60%", "vit", 5, 0, 0.0, "block")
THORNS = SkillDef("thorns", "反伤", "荆棘之躯，反弹受到伤害的 30%", "vit", 8, 0, 0.0, "reflect")
LIFE_DRAIN = SkillDef("life_drain", "生命汲取", "吸取目标生命力，造成伤害并回复等量 HP", "vit", 10, 10, 1.2, "lifesteal")
REGENERATE = SkillDef("regenerate", "再生", "生命恢复，回复 15% 最大 HP", "vit", 15, 0, 0.0, "heal")
IMMORTAL = SkillDef("immortal", "不灭之躯", "激活荒原核心数据，回复 30% HP 并减伤", "vit", 20, 0, 0.0, "heal")


SKILLS = [
    # STR
    HEAVY_STRIKE, GROUND_SLAM, ARMOR_BREAK, WAR_CRY, BERSERK, JUDGMENT,
    # AGI
    DODGE, POISON_BLADE, COMBO, SHADOW_CLONE, ASSASSINATE, FATAL_RHYTHM,
    # INT
    FIREBALL, CHAIN_LIGHTNING, FREEZE, VOID_SHIELD, ANNIHILATE, TIME_STOP,
    # VIT
    BLOCK, IRON_WALL, THORNS, LIFE_DRAIN, REGENERATE, IMMORTAL,
]

SKILL_MAP = {s.id: s for s in SKILLS}
