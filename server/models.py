import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.db import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str | None] = mapped_column(String(128), unique=True, nullable=True)  # 唯一身份标识
    api_token: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)  # API 认证 token
    name: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)

    # Buddy 外观（仅形象，不继承属性）
    buddy_species: Mapped[str] = mapped_column(String(32), default="blob")
    buddy_eye: Mapped[str] = mapped_column(String(8), default="·")
    buddy_hat: Mapped[str] = mapped_column(String(16), default="none")
    buddy_shiny: Mapped[bool] = mapped_column(Boolean, default=False)

    # 等级与经验
    level: Mapped[int] = mapped_column(Integer, default=1)
    exp: Mapped[int] = mapped_column(Integer, default=0)

    # 四维属性
    str_: Mapped[int] = mapped_column("str_", Integer, default=5)
    agi: Mapped[int] = mapped_column(Integer, default=5)
    int_: Mapped[int] = mapped_column("int_", Integer, default=5)
    vit: Mapped[int] = mapped_column(Integer, default=5)
    unallocated_points: Mapped[int] = mapped_column(Integer, default=0)

    # ELO
    elo: Mapped[float] = mapped_column(Float, default=1000.0)

    # 体力
    stamina: Mapped[int] = mapped_column(Integer, default=20)
    stamina_refreshed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    # 每日对战次数
    daily_battles: Mapped[int] = mapped_column(Integer, default=0)
    battles_refreshed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    # 元信息
    is_npc: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    # 关联
    equipments: Mapped[list["Equipment"]] = relationship(back_populates="player", cascade="all, delete-orphan")
    skills: Mapped[list["PlayerSkill"]] = relationship(back_populates="player", cascade="all, delete-orphan")


class Equipment(Base):
    __tablename__ = "equipments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False)
    template_id: Mapped[str] = mapped_column(String(64), nullable=False)  # 装备模板ID
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    slot: Mapped[str] = mapped_column(String(16), nullable=False)  # weapon/armor/accessory
    rarity: Mapped[int] = mapped_column(Integer, default=0)  # 0白 1绿 2蓝 3紫 4橙

    str_bonus: Mapped[int] = mapped_column(Integer, default=0)
    agi_bonus: Mapped[int] = mapped_column(Integer, default=0)
    int_bonus: Mapped[int] = mapped_column(Integer, default=0)
    vit_bonus: Mapped[int] = mapped_column(Integer, default=0)

    equipped: Mapped[bool] = mapped_column(Boolean, default=False)

    player: Mapped["Player"] = relationship(back_populates="equipments")


class PlayerSkill(Base):
    __tablename__ = "player_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False)
    skill_id: Mapped[str] = mapped_column(String(32), nullable=False)
    equipped: Mapped[bool] = mapped_column(Boolean, default=False)

    player: Mapped["Player"] = relationship(back_populates="skills")


class BattleLog(Base):
    __tablename__ = "battle_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    attacker_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False)
    defender_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False)
    winner_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("players.id"), nullable=True)

    rounds_json: Mapped[str] = mapped_column(Text, default="[]")

    attacker_elo_change: Mapped[float] = mapped_column(Float, default=0.0)
    defender_elo_change: Mapped[float] = mapped_column(Float, default=0.0)
    attacker_exp_gained: Mapped[int] = mapped_column(Integer, default=0)
    defender_exp_gained: Mapped[int] = mapped_column(Integer, default=0)

    is_revenge: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )
