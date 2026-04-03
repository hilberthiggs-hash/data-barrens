"""
战斗引擎 —— 纯函数实现，不依赖数据库，易于测试。

战斗流程：
1. 根据双方属性 + 装备 + 技能 构建 BattleState
2. 回合制自动战斗（最多 MAX_BATTLE_ROUNDS 回合）
3. 输出战斗日志
"""
import random
from dataclasses import dataclass, field

from server.config import MAX_BATTLE_ROUNDS, ELO_K, ELO_BASE
from server.game_data.skills import SkillDef, SKILL_MAP


@dataclass
class FighterStats:
    name: str
    max_hp: int
    hp: int
    atk: int       # 物理攻击 (基于 STR)
    speed: int     # 速度 (基于 AGI)
    spell: int     # 法术攻击 (基于 INT)
    defense: int   # 防御 (基于 VIT)
    crit_rate: float
    skills: list[SkillDef] = field(default_factory=list)
    # 状态效果
    buffs: dict[str, int] = field(default_factory=dict)  # effect -> 剩余回合数


@dataclass
class RoundResult:
    round_num: int
    attacker_action: str
    defender_action: str
    attacker_hp: int
    defender_hp: int


def build_fighter(
    name: str,
    str_val: int, agi_val: int, int_val: int, vit_val: int,
    equip_str: int = 0, equip_agi: int = 0, equip_int: int = 0, equip_vit: int = 0,
    skill_ids: list[str] | None = None,
) -> FighterStats:
    total_str = str_val + equip_str
    total_agi = agi_val + equip_agi
    total_int = int_val + equip_int
    total_vit = vit_val + equip_vit

    max_hp = 80 + total_vit * 12 + total_str * 3
    return FighterStats(
        name=name,
        max_hp=max_hp,
        hp=max_hp,
        atk=total_str * 3 + total_agi,
        speed=total_agi * 2 + total_str,
        spell=total_int * 4,
        defense=total_vit * 2 + total_str,
        crit_rate=min(0.05 + total_agi * 0.008, 0.4),
        skills=[SKILL_MAP[sid] for sid in (skill_ids or []) if sid in SKILL_MAP],
    )


def _calc_damage(attacker: FighterStats, skill: SkillDef | None, defender: FighterStats) -> tuple[int, str]:
    """计算伤害，返回 (伤害值, 描述文本)"""
    if skill is None:
        # 普通攻击
        raw = attacker.atk * 0.8
        desc = f"{attacker.name} 发动普通攻击"
    elif skill.stat in ("str", "agi"):
        raw = skill.damage_base + attacker.atk * skill.damage_scale
        desc = f"{attacker.name} 发动「{skill.name}」"
    else:  # int
        raw = skill.damage_base + attacker.spell * skill.damage_scale
        desc = f"{attacker.name} 发动「{skill.name}」"

    # 暴击
    is_crit = random.random() < attacker.crit_rate
    if is_crit:
        raw *= 1.5
        desc += "（暴击！）"

    # 防御减伤
    def_val = defender.defense
    if defender.buffs.get("def_down", 0) > 0:
        def_val = int(def_val * 0.7)
    if skill and skill.effect == "ignore_def":
        def_val = int(def_val * 0.5)

    reduction = def_val / (def_val + 100)
    damage = max(1, int(raw * (1 - reduction)))

    # 狂暴 buff
    if attacker.buffs.get("atk_up", 0) > 0:
        damage = int(damage * 1.5)

    return damage, desc


def _choose_skill(fighter: FighterStats) -> SkillDef | None:
    """AI 选择技能：有技能就随机用，没有就普通攻击"""
    usable = [s for s in fighter.skills if s.effect not in ("dodge", "block", "reflect", "heal")]
    if usable and random.random() < 0.7:
        return random.choice(usable)
    return None


def _choose_defensive_skill(fighter: FighterStats) -> SkillDef | None:
    """选择防御/反应技能"""
    defensive = [s for s in fighter.skills if s.effect in ("dodge", "block", "reflect", "heal")]
    if defensive and random.random() < 0.5:
        return random.choice(defensive)
    return None


def _apply_skill_effect(skill: SkillDef, attacker: FighterStats, defender: FighterStats, damage: int) -> tuple[int, str]:
    """处理技能特殊效果，返回 (最终伤害, 额外描述)"""
    extra = ""

    if skill.effect == "def_down":
        defender.buffs["def_down"] = 2
        extra = f" → {defender.name} 防御降低 30%（2回合）"

    elif skill.effect == "atk_up":
        attacker.buffs["atk_up"] = 3
        extra = f" → {attacker.name} 攻击提升 50%（3回合）"

    elif skill.effect == "double_hit":
        damage2 = max(1, int(damage * 0.6))
        damage = max(1, int(damage * 0.6))
        damage += damage2
        extra = f"（双击！{damage}）"

    elif skill.effect == "execute":
        if defender.hp < defender.max_hp * 0.3:
            damage *= 2
            extra = "（斩杀！伤害翻倍！）"

    elif skill.effect == "stun":
        if random.random() < 0.3:
            defender.buffs["stun"] = 1
            extra = f" → {defender.name} 被冰冻！下回合无法行动"

    return damage, extra


def _apply_defensive_effect(skill: SkillDef, defender: FighterStats, damage: int) -> tuple[int, str]:
    """处理防御技能，返回 (修改后伤害, 描述)"""
    if skill.effect == "dodge":
        if random.random() < 0.4:
            return 0, f"{defender.name} 使用「闪避」—— 完美闪避！"
        return damage, f"{defender.name} 尝试闪避 —— 未能躲开"

    elif skill.effect == "block":
        reduced = int(damage * 0.6)
        return reduced, f"{defender.name} 使用「格挡」减伤 40%"

    elif skill.effect == "reflect":
        reflect_dmg = int(damage * 0.3)
        return damage, f"{defender.name} 使用「反伤」反弹 {reflect_dmg} 伤害"

    elif skill.effect == "heal":
        heal = int(defender.max_hp * 0.15)
        defender.hp = min(defender.max_hp, defender.hp + heal)
        return damage, f"{defender.name} 使用「再生」恢复 {heal} HP"

    return damage, ""


def _tick_buffs(fighter: FighterStats):
    """回合结束时减少 buff 持续时间"""
    expired = []
    for effect, turns in fighter.buffs.items():
        fighter.buffs[effect] = turns - 1
        if fighter.buffs[effect] <= 0:
            expired.append(effect)
    for e in expired:
        del fighter.buffs[e]


def run_battle(fighter_a: FighterStats, fighter_b: FighterStats, seed: int | None = None) -> tuple[str | None, list[RoundResult]]:
    """
    执行战斗。返回 (winner_name | None, rounds)
    winner_name 为 None 表示平局。
    """
    if seed is not None:
        random.seed(seed)

    rounds: list[RoundResult] = []

    for round_num in range(1, MAX_BATTLE_ROUNDS + 1):
        # 决定出手顺序
        if fighter_a.speed >= fighter_b.speed:
            first, second = fighter_a, fighter_b
        else:
            first, second = fighter_b, fighter_a

        action_first = ""
        action_second = ""

        # ── first 攻击 second ──
        if first.buffs.get("stun", 0) > 0:
            action_first = f"{first.name} 被冰冻，无法行动！"
        else:
            skill = _choose_skill(first)
            damage, desc = _calc_damage(first, skill, second)

            if skill:
                damage, extra = _apply_skill_effect(skill, first, second, damage)
                desc += extra

            # second 防御反应
            def_skill = _choose_defensive_skill(second)
            if def_skill:
                damage, def_desc = _apply_defensive_effect(def_skill, second, damage)
                desc += f" | {def_desc}"

                # 反伤结算
                if def_skill.effect == "reflect":
                    reflect_dmg = int(damage * 0.3)
                    first.hp -= reflect_dmg

            second.hp -= damage
            action_first = f"{desc} → {second.name} -{damage} HP"

        if second.hp <= 0:
            # 统一按 fighter_a/fighter_b 顺序记录
            if first is fighter_a:
                rounds.append(RoundResult(round_num, action_first, "", fighter_a.hp, max(0, fighter_b.hp)))
            else:
                rounds.append(RoundResult(round_num, "", action_first, fighter_a.hp, max(0, fighter_b.hp)))
            return first.name, rounds

        # ── second 攻击 first ──
        if second.buffs.get("stun", 0) > 0:
            action_second = f"{second.name} 被冰冻，无法行动！"
        else:
            skill = _choose_skill(second)
            damage, desc = _calc_damage(second, skill, first)

            if skill:
                damage, extra = _apply_skill_effect(skill, second, first, damage)
                desc += extra

            def_skill = _choose_defensive_skill(first)
            if def_skill:
                damage, def_desc = _apply_defensive_effect(def_skill, first, damage)
                desc += f" | {def_desc}"

                if def_skill.effect == "reflect":
                    reflect_dmg = int(damage * 0.3)
                    second.hp -= reflect_dmg

            first.hp -= damage
            action_second = f"{desc} → {first.name} -{damage} HP"

        if first.hp <= 0:
            if first is fighter_a:
                rounds.append(RoundResult(round_num, action_first, action_second, max(0, fighter_a.hp), fighter_b.hp))
            else:
                rounds.append(RoundResult(round_num, action_second, action_first, max(0, fighter_a.hp), fighter_b.hp))
            return second.name, rounds

        # tick buffs
        _tick_buffs(first)
        _tick_buffs(second)

        # 按 fighter_a/fighter_b 顺序记录
        if first is fighter_a:
            rounds.append(RoundResult(round_num, action_first, action_second, fighter_a.hp, fighter_b.hp))
        else:
            rounds.append(RoundResult(round_num, action_second, action_first, fighter_a.hp, fighter_b.hp))

    # 平局判定：HP% 高者胜
    a_pct = fighter_a.hp / fighter_a.max_hp
    b_pct = fighter_b.hp / fighter_b.max_hp
    if a_pct > b_pct:
        return fighter_a.name, rounds
    elif b_pct > a_pct:
        return fighter_b.name, rounds
    return None, rounds


def calc_elo_change(winner_elo: float, loser_elo: float) -> tuple[float, float]:
    """返回 (winner_change, loser_change)"""
    expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    winner_change = ELO_K * (1 - expected_winner)
    loser_change = -ELO_K * expected_winner
    return round(winner_change, 1), round(loser_change, 1)


def calc_exp_reward(winner_level: int, loser_level: int) -> tuple[int, int]:
    """返回 (winner_exp, loser_exp)"""
    base = 30
    level_diff = loser_level - winner_level
    bonus = max(0, level_diff * 5)  # 以弱胜强额外经验
    winner_exp = base + bonus + 10
    loser_exp = base // 2  # 输了也有经验
    return winner_exp, loser_exp
