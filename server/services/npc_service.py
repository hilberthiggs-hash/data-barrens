from sqlalchemy.orm import Session

from server.models import Player, PlayerSkill
from server.game_data.npcs import NPC_DEFS


def init_npcs(db: Session):
    """初始化 NPC 角色（幂等）"""
    for npc_def in NPC_DEFS:
        existing = db.query(Player).filter(Player.name == npc_def["name"]).first()
        if existing:
            continue

        npc = Player(
            name=npc_def["name"],
            buddy_species=npc_def["buddy_species"],
            buddy_eye="·",
            buddy_hat="none",
            buddy_shiny=False,
            level=npc_def["level"],
            str_=npc_def["str"],
            agi=npc_def["agi"],
            int_=npc_def["int"],
            vit=npc_def["vit"],
            elo=npc_def["elo"],
            is_npc=True,
            stamina=999,
        )
        db.add(npc)
        db.flush()

        for skill_id in npc_def["skills"]:
            db.add(PlayerSkill(player_id=npc.id, skill_id=skill_id, equipped=True))

    db.commit()
