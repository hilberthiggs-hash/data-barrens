import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from server.db import get_db
from server.models import Player, BattleLog, Equipment, PlayerSkill
from server.schemas import ChallengeRequest, BattleLogOut, BattleRound, PlayerBrief, MessageOut
from server.services.battle_engine import build_fighter, run_battle, calc_elo_change, calc_exp_reward
from server.services.player_service import consume_stamina, add_exp, get_player
from server.config import BATTLE_STAMINA_COST

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


def _execute_battle(db: Session, attacker: Player, defender: Player, is_revenge: bool = False):
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
    if winner_name == attacker.name:
        elo_w, elo_l = calc_elo_change(attacker.elo, defender.elo)
        exp_w, exp_l = calc_exp_reward(attacker.level, defender.level)
        attacker.elo += elo_w
        defender.elo = max(0, defender.elo + elo_l)
        add_exp(db, attacker, exp_w)
        add_exp(db, defender, exp_l)
        a_elo_change, d_elo_change = elo_w, elo_l
        a_exp, d_exp = exp_w, exp_l
    elif winner_name == defender.name:
        elo_w, elo_l = calc_elo_change(defender.elo, attacker.elo)
        exp_w, exp_l = calc_exp_reward(defender.level, attacker.level)
        defender.elo += elo_w
        attacker.elo = max(0, attacker.elo + elo_l)
        add_exp(db, defender, exp_w)
        add_exp(db, attacker, exp_l)
        a_elo_change, d_elo_change = elo_l, elo_w
        a_exp, d_exp = exp_l, exp_w
    else:
        # 平局
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
        is_revenge=is_revenge,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log, rounds


def _log_to_out(db: Session, log: BattleLog, rounds: list | None = None) -> BattleLogOut:
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

    return BattleLogOut(
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
        is_revenge=log.is_revenge,
        created_at=log.created_at,
    )


@router.post("/challenge", response_model=BattleLogOut)
def api_challenge(data: ChallengeRequest, db: Session = Depends(get_db)):
    if data.attacker_id == data.defender_id:
        raise HTTPException(status_code=400, detail="不能挑战自己")

    attacker = get_player(db, data.attacker_id)
    defender = get_player(db, data.defender_id)
    if not attacker:
        raise HTTPException(status_code=404, detail="攻击方不存在")
    if not defender:
        raise HTTPException(status_code=404, detail="防守方不存在")

    consume_stamina(db, attacker, BATTLE_STAMINA_COST)
    log, rounds = _execute_battle(db, attacker, defender)
    return _log_to_out(db, log, rounds)


@router.post("/ladder/{player_id}", response_model=BattleLogOut)
def api_ladder(player_id: int, db: Session = Depends(get_db)):
    """天梯匹配：自动匹配 ELO 相近的对手"""
    import random

    attacker = get_player(db, player_id)
    if not attacker:
        raise HTTPException(status_code=404, detail="玩家不存在")

    consume_stamina(db, attacker, BATTLE_STAMINA_COST)

    # 找 ELO 差距在 300 以内的所有对手（包含 NPC）
    elo_range = 300
    candidates = db.query(Player).filter(
        Player.id != player_id,
        Player.elo >= attacker.elo - elo_range,
        Player.elo <= attacker.elo + elo_range,
    ).all()

    # 如果范围内没人，放宽到所有人
    if not candidates:
        candidates = db.query(Player).filter(Player.id != player_id).all()

    if not candidates:
        raise HTTPException(status_code=400, detail="荒原空无一人……没有可匹配的对手")

    # ELO 越接近权重越高
    weights = [max(1, elo_range - abs(c.elo - attacker.elo)) for c in candidates]
    defender = random.choices(candidates, weights=weights, k=1)[0]

    log, rounds = _execute_battle(db, attacker, defender)
    return _log_to_out(db, log, rounds)


@router.post("/revenge/{battle_id}", response_model=BattleLogOut)
def api_revenge(battle_id: int, player_id: int, db: Session = Depends(get_db)):
    original = db.query(BattleLog).filter(BattleLog.id == battle_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="战斗记录不存在")
    if original.defender_id != player_id:
        raise HTTPException(status_code=400, detail="只有被挑战方才能复仇")
    if original.winner_id == player_id:
        raise HTTPException(status_code=400, detail="你赢了这场战斗，不需要复仇")

    attacker = get_player(db, player_id)
    defender = get_player(db, original.attacker_id)
    if not attacker or not defender:
        raise HTTPException(status_code=404, detail="玩家不存在")

    # 复仇不消耗体力
    log, rounds = _execute_battle(db, attacker, defender, is_revenge=True)
    return _log_to_out(db, log, rounds)


@router.get("/log/{log_id}", response_model=BattleLogOut)
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
