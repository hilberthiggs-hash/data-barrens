from pydantic import BaseModel, Field
from datetime import datetime


# ── Player ──

class PlayerRegister(BaseModel):
    name: str = Field(min_length=1, max_length=32)
    buddy_species: str = "blob"
    buddy_eye: str = "·"
    buddy_hat: str = "none"
    buddy_shiny: bool = False


class AllocatePoints(BaseModel):
    str_: int = Field(default=0, alias="str", ge=0)
    agi: int = Field(default=0, ge=0)
    int_: int = Field(default=0, alias="int", ge=0)
    vit: int = Field(default=0, ge=0)

    model_config = {"populate_by_name": True}


class PlayerOut(BaseModel):
    id: int
    name: str
    buddy_species: str
    buddy_eye: str
    buddy_hat: str
    buddy_shiny: bool
    level: int
    exp: int
    exp_to_next: int
    str_: int = Field(alias="str", serialization_alias="str")
    agi: int
    int_: int = Field(alias="int", serialization_alias="int")
    vit: int
    unallocated_points: int
    elo: float
    stamina: int
    is_npc: bool
    created_at: datetime
    equipped_skills: list[str]
    equipped_equipment: list["EquipmentOut"]

    model_config = {"from_attributes": True, "populate_by_name": True}


# ── Equipment ──

RARITY_NAMES = ["白", "绿", "蓝", "紫", "橙"]


class EquipmentOut(BaseModel):
    id: int
    template_id: str
    name: str
    slot: str
    rarity: int
    rarity_name: str
    str_bonus: int
    agi_bonus: int
    int_bonus: int
    vit_bonus: int
    equipped: bool

    model_config = {"from_attributes": True}


# ── Battle ──

class ChallengeRequest(BaseModel):
    attacker_id: int
    defender_id: int


class BattleRound(BaseModel):
    round_num: int
    attacker_action: str
    defender_action: str
    attacker_hp: int
    defender_hp: int


class BattleLogOut(BaseModel):
    id: int
    attacker: "PlayerBrief"
    defender: "PlayerBrief"
    winner_name: str | None
    rounds: list[BattleRound]
    attacker_elo_change: float
    defender_elo_change: float
    attacker_exp_gained: int
    defender_exp_gained: int
    is_revenge: bool
    created_at: datetime


class PlayerBrief(BaseModel):
    id: int
    name: str
    buddy_species: str
    level: int
    elo: float


# ── Ranking ──

class RankingEntry(BaseModel):
    rank: int
    player: PlayerBrief


# ── Common ──

class MessageOut(BaseModel):
    message: str
