from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.db import get_db
from server.models import Player
from server.schemas import RankingEntry, PlayerBrief

router = APIRouter(prefix="/api/ranking", tags=["ranking"])


@router.get("/elo", response_model=list[RankingEntry])
def api_elo_ranking(limit: int = 20, db: Session = Depends(get_db)):
    players = db.query(Player).filter(Player.is_npc == False).order_by(Player.elo.desc()).limit(limit).all()
    return [
        RankingEntry(
            rank=i + 1,
            player=PlayerBrief(
                id=p.id, name=p.name, buddy_species=p.buddy_species,
                level=p.level, elo=p.elo,
            ),
        )
        for i, p in enumerate(players)
    ]


@router.get("/level", response_model=list[RankingEntry])
def api_level_ranking(limit: int = 20, db: Session = Depends(get_db)):
    players = db.query(Player).filter(Player.is_npc == False).order_by(Player.level.desc(), Player.exp.desc()).limit(limit).all()
    return [
        RankingEntry(
            rank=i + 1,
            player=PlayerBrief(
                id=p.id, name=p.name, buddy_species=p.buddy_species,
                level=p.level, elo=p.elo,
            ),
        )
        for i, p in enumerate(players)
    ]
