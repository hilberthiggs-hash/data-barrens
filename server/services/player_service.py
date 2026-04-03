import datetime
from sqlalchemy.orm import Session

from server.models import Player, PlayerSkill
from server.schemas import PlayerRegister, AllocatePoints, PlayerOut, EquipmentOut, RARITY_NAMES
from server.config import (
    INITIAL_STATS, DAILY_STAMINA, NEWBIE_STAMINA, NEWBIE_DAYS,
    points_per_level, exp_to_level_up, MAX_LEVEL,
)


def register_player(db: Session, data: PlayerRegister) -> Player:
    existing = db.query(Player).filter(Player.name == data.name).first()
    if existing:
        raise ValueError(f"名字 '{data.name}' 已被占用")

    player = Player(
        name=data.name,
        buddy_species=data.buddy_species,
        buddy_eye=data.buddy_eye,
        buddy_hat=data.buddy_hat,
        buddy_shiny=data.buddy_shiny,
        **INITIAL_STATS,
    )
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


def get_player(db: Session, player_id: int) -> Player | None:
    return db.query(Player).filter(Player.id == player_id).first()


def get_player_by_name(db: Session, name: str) -> Player | None:
    return db.query(Player).filter(Player.name == name).first()


def allocate_points(db: Session, player_id: int, alloc: AllocatePoints) -> Player:
    player = get_player(db, player_id)
    if not player:
        raise ValueError("玩家不存在")

    total = alloc.str_ + alloc.agi + alloc.int_ + alloc.vit
    if total <= 0:
        raise ValueError("至少分配 1 个属性点")
    if total > player.unallocated_points:
        raise ValueError(f"属性点不足，可用 {player.unallocated_points}，请求 {total}")

    player.str_ += alloc.str_
    player.agi += alloc.agi
    player.int_ += alloc.int_
    player.vit += alloc.vit
    player.unallocated_points -= total

    db.commit()
    db.refresh(player)
    return player


def add_exp(db: Session, player: Player, exp: int) -> tuple[Player, int]:
    """增加经验值，自动升级。返回 (player, 升了几级)"""
    levels_gained = 0
    player.exp += exp

    while player.level < MAX_LEVEL:
        needed = exp_to_level_up(player.level)
        if player.exp < needed:
            break
        player.exp -= needed
        player.level += 1
        player.unallocated_points += points_per_level(player.level)
        levels_gained += 1
        _unlock_skills(db, player)

    db.commit()
    db.refresh(player)
    return player, levels_gained


def _unlock_skills(db: Session, player: Player):
    """根据等级自动解锁技能"""
    from server.game_data.skills import SKILLS

    owned_skill_ids = {ps.skill_id for ps in player.skills}
    for skill in SKILLS:
        if skill.unlock_level <= player.level and skill.id not in owned_skill_ids:
            db.add(PlayerSkill(player_id=player.id, skill_id=skill.id, equipped=False))


def refresh_stamina(db: Session, player: Player) -> Player:
    """刷新体力（UTC+8 零点重置）"""
    now = datetime.datetime.utcnow()
    utc8_now = now + datetime.timedelta(hours=8)
    utc8_last = player.stamina_refreshed_at + datetime.timedelta(hours=8)

    if utc8_now.date() > utc8_last.date():
        days_since_creation = (now - player.created_at).days
        max_stamina = NEWBIE_STAMINA if days_since_creation < NEWBIE_DAYS else DAILY_STAMINA
        player.stamina = max_stamina
        player.stamina_refreshed_at = now
        db.commit()
        db.refresh(player)

    return player


def consume_stamina(db: Session, player: Player, cost: int) -> Player:
    refresh_stamina(db, player)
    if player.stamina < cost:
        raise ValueError(f"体力不足，当前 {player.stamina}，需要 {cost}")
    player.stamina -= cost
    db.commit()
    db.refresh(player)
    return player


def to_player_out(player: Player) -> PlayerOut:
    equipped_skills = [ps.skill_id for ps in player.skills if ps.equipped]
    equipped_equip = [
        EquipmentOut(
            id=e.id,
            template_id=e.template_id,
            name=e.name,
            slot=e.slot,
            rarity=e.rarity,
            rarity_name=RARITY_NAMES[e.rarity],
            str_bonus=e.str_bonus,
            agi_bonus=e.agi_bonus,
            int_bonus=e.int_bonus,
            vit_bonus=e.vit_bonus,
            equipped=e.equipped,
        )
        for e in player.equipments if e.equipped
    ]
    return PlayerOut(
        id=player.id,
        name=player.name,
        buddy_species=player.buddy_species,
        buddy_eye=player.buddy_eye,
        buddy_hat=player.buddy_hat,
        buddy_shiny=player.buddy_shiny,
        level=player.level,
        exp=player.exp,
        exp_to_next=exp_to_level_up(player.level),
        **{"str": player.str_, "agi": player.agi, "int": player.int_, "vit": player.vit},
        unallocated_points=player.unallocated_points,
        elo=player.elo,
        stamina=player.stamina,
        is_npc=player.is_npc,
        created_at=player.created_at,
        equipped_skills=equipped_skills,
        equipped_equipment=equipped_equip,
    )
