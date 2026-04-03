import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from server.db import get_db
from server.models import Player, BattleLog, Equipment, PlayerSkill, Notification
from server.schemas import ChallengeRequest, BattleLogOut, BattleRound, PlayerBrief, MessageOut
from server.services.battle_engine import build_fighter, run_battle, calc_elo_change, calc_exp_reward
from server.services.player_service import consume_stamina, consume_battle_count, add_exp, get_player
from server.auth import get_current_player
from server.config import BATTLE_STAMINA_COST, LOOT_CHANCE

router = APIRouter(prefix="/api/battle", tags=["battle"])


def _get_equipped_bonuses(player: Player) -> tuple[int, int, int, int]:
    bonuses = [0, 0, 0, 0]
    for e in player.equipments:
        if e.equipped:
            bonuses[0] += e.str_bonus
            bonuses[1] += e.agi_bonus
            bonuses[2] += e.int_bonus
            bonuses[3] += e.vit_bonus
    return tuple(bonuses)


def _get_equipped_skill_ids(player: Player) -> list[str]:
    return [ps.skill_id for ps in player.skills if ps.equipped]


def _loot_equipment(db: Session, winner: Player, loser: Player) -> str | None:
    """胜者有概率从败者背包抢一件装备，败者失去该装备。返回描述文本。"""
    import random

    if loser.is_npc:
        return None  # NPC 不掉装备

    # 败者已穿戴的装备中随机一件
    equipped = [e for e in loser.equipments if e.equipped]
    if not equipped:
        return None

    if random.random() >= LOOT_CHANCE:
        return None

    stolen = random.choice(equipped)

    from server.schemas import RARITY_NAMES
    loot_name = f"[{RARITY_NAMES[stolen.rarity]}]{stolen.name}"

    # 转移所有权
    stolen.player_id = winner.id
    stolen.equipped = False

    # 通知被抢的人
    db.add(Notification(
        player_id=loser.id,
        message=f"{winner.name} 击败了你，抢走了你身上的 {loot_name}！",
    ))
    db.commit()

    # 双方自动择优穿戴
    from server.services.equipment_service import auto_equip_best
    auto_equip_best(db, winner)
    auto_equip_best(db, loser)

    return loot_name


def _execute_battle(db: Session, attacker: Player, defender: Player, allow_loot: bool = False):
    # 构建战斗双方
    a_bonuses = _get_equipped_bonuses(attacker)
    d_bonuses = _get_equipped_bonuses(defender)

    fighter_a = build_fighter(
        attacker.name, attacker.str_, attacker.agi, attacker.int_, attacker.vit,
        *a_bonuses, _get_equipped_skill_ids(attacker),
    )
    fighter_b = build_fighter(
        defender.name, defender.str_, defender.agi, defender.int_, defender.vit,
        *d_bonuses, _get_equipped_skill_ids(defender),
    )

    winner_name, rounds = run_battle(fighter_a, fighter_b)

    # ELO 和经验
    loot_desc = None
    if winner_name == attacker.name:
        elo_w, elo_l = calc_elo_change(attacker.elo, defender.elo)
        exp_w, exp_l = calc_exp_reward(attacker.level, defender.level)
        attacker.elo += elo_w
        defender.elo = max(0, defender.elo + elo_l)
        add_exp(db, attacker, exp_w)
        add_exp(db, defender, exp_l)
        a_elo_change, d_elo_change = elo_w, elo_l
        a_exp, d_exp = exp_w, exp_l
        if allow_loot:
            loot_desc = _loot_equipment(db, attacker, defender)
    elif winner_name == defender.name:
        elo_w, elo_l = calc_elo_change(defender.elo, attacker.elo)
        exp_w, exp_l = calc_exp_reward(defender.level, attacker.level)
        defender.elo += elo_w
        attacker.elo = max(0, attacker.elo + elo_l)
        add_exp(db, defender, exp_w)
        add_exp(db, attacker, exp_l)
        a_elo_change, d_elo_change = elo_l, elo_w
        a_exp, d_exp = exp_l, exp_w
        if allow_loot:
            loot_desc = _loot_equipment(db, defender, attacker)
    else:
        a_elo_change, d_elo_change = 0, 0
        a_exp, d_exp = 15, 15
        add_exp(db, attacker, a_exp)
        add_exp(db, defender, d_exp)

    # 记录战斗日志
    winner_id = None
    if winner_name == attacker.name:
        winner_id = attacker.id
    elif winner_name == defender.name:
        winner_id = defender.id

    log = BattleLog(
        attacker_id=attacker.id,
        defender_id=defender.id,
        winner_id=winner_id,
        rounds_json=json.dumps(
            [{"round_num": r.round_num, "attacker_action": r.attacker_action,
              "defender_action": r.defender_action, "attacker_hp": r.attacker_hp,
              "defender_hp": r.defender_hp} for r in rounds],
            ensure_ascii=False,
        ),
        attacker_elo_change=a_elo_change,
        defender_elo_change=d_elo_change,
        attacker_exp_gained=a_exp,
        defender_exp_gained=d_exp,
        is_revenge=False,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log, rounds, loot_desc


def _log_to_out(db: Session, log: BattleLog, rounds: list | None = None, loot_desc: str | None = None) -> dict:
    attacker = get_player(db, log.attacker_id)
    defender = get_player(db, log.defender_id)
    winner_name = None
    if log.winner_id == log.attacker_id:
        winner_name = attacker.name
    elif log.winner_id == log.defender_id:
        winner_name = defender.name

    if rounds is None:
        rounds_data = json.loads(log.rounds_json)
    else:
        rounds_data = [
            {"round_num": r.round_num, "attacker_action": r.attacker_action,
             "defender_action": r.defender_action, "attacker_hp": r.attacker_hp,
             "defender_hp": r.defender_hp} for r in rounds
        ]

    result = BattleLogOut(
        id=log.id,
        attacker=PlayerBrief(id=attacker.id, name=attacker.name, buddy_species=attacker.buddy_species,
                             level=attacker.level, elo=attacker.elo),
        defender=PlayerBrief(id=defender.id, name=defender.name, buddy_species=defender.buddy_species,
                             level=defender.level, elo=defender.elo),
        winner_name=winner_name,
        rounds=[BattleRound(**r) for r in rounds_data],
        attacker_elo_change=log.attacker_elo_change,
        defender_elo_change=log.defender_elo_change,
        attacker_exp_gained=log.attacker_exp_gained,
        defender_exp_gained=log.defender_exp_gained,
        is_revenge=False,
        created_at=log.created_at,
    )
    out = result.model_dump(mode="json")
    out["loot"] = loot_desc
    # 附带攻击方剩余对战次数
    from server.config import DAILY_BATTLE_LIMIT
    out["battles_remaining"] = DAILY_BATTLE_LIMIT - attacker.daily_battles
    return out


@router.post("/challenge")
def api_challenge(data: ChallengeRequest, db: Session = Depends(get_db), me: Player = Depends(get_current_player)):
    if data.attacker_id != me.id:
        raise HTTPException(status_code=403, detail="只能用自己的角色发起挑战")
    if data.attacker_id == data.defender_id:
        raise HTTPException(status_code=400, detail="不能挑战自己")

    attacker = me
    defender = get_player(db, data.defender_id)
    if not defender:
        raise HTTPException(status_code=404, detail="防守方不存在")

    if defender.is_npc:
        raise HTTPException(status_code=400, detail="不能指定挑战 NPC，请用天梯匹配（/barren ladder）")

    try:
        consume_battle_count(db, attacker)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    log, rounds, loot_desc = _execute_battle(db, attacker, defender, allow_loot=True)
    return _log_to_out(db, log, rounds, loot_desc)


@router.post("/ladder")
def api_ladder(db: Session = Depends(get_db), me: Player = Depends(get_current_player)):
    """天梯匹配：自动匹配 ELO 相近的对手"""
    import random

    attacker = me

    try:
        consume_stamina(db, attacker, 2)  # 天梯消耗 2 体力，不消耗战斗次数
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 找 ELO 差距在 300 以内的所有对手（包含 NPC）
    elo_range = 300
    candidates = db.query(Player).filter(
        Player.id != attacker.id,
        Player.elo >= attacker.elo - elo_range,
        Player.elo <= attacker.elo + elo_range,
    ).all()

    if not candidates:
        candidates = db.query(Player).filter(Player.id != player_id).all()

    if not candidates:
        raise HTTPException(status_code=400, detail="荒原空无一人……没有可匹配的对手")

    # ELO 越接近权重越高，加一些随机性
    weights = [max(1, elo_range - abs(c.elo - attacker.elo)) + random.randint(0, 100) for c in candidates]
    defender = random.choices(candidates, weights=weights, k=1)[0]

    log, rounds, loot_desc = _execute_battle(db, attacker, defender)
    return _log_to_out(db, log, rounds, loot_desc)


@router.get("/log/{log_id}")
def api_get_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(BattleLog).filter(BattleLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="战斗记录不存在")
    return _log_to_out(db, log)


@router.get("/history/{player_id}", response_model=list[BattleLogOut])
def api_battle_history(player_id: int, limit: int = 10, db: Session = Depends(get_db)):
    logs = db.query(BattleLog).filter(
        (BattleLog.attacker_id == player_id) | (BattleLog.defender_id == player_id)
    ).order_by(BattleLog.created_at.desc()).limit(limit).all()
    return [_log_to_out(db, log) for log in logs]
