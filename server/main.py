from contextlib import asynccontextmanager
from fastapi import FastAPI

from server.db import init_db, SessionLocal
from server.routers import player, battle, explore, equipment, skill, ranking
from server.services.npc_service import init_npcs
from server.game_data.lore import WELCOME_TEXT


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    init_db()
    db = SessionLocal()
    try:
        init_npcs(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="数据荒原 - Data Wasteland",
    description="异步竞技 RPG 游戏服务器",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(player.router)
app.include_router(battle.router)
app.include_router(explore.router)
app.include_router(equipment.router)
app.include_router(skill.router)
app.include_router(ranking.router)


@app.get("/")
def root():
    return {"message": "Data Wasteland Server", "welcome": WELCOME_TEXT}


@app.get("/api/skill-version")
def skill_version():
    from server.config import SKILL_VERSION, SKILL_CHANGELOG
    return {"version": SKILL_VERSION, "changelog": SKILL_CHANGELOG}


@app.get("/api/skill-content")
def skill_content():
    from fastapi.responses import PlainTextResponse
    from pathlib import Path
    skill_path = Path(__file__).resolve().parent.parent / "skill" / "SKILL.md"
    return PlainTextResponse(skill_path.read_text(encoding="utf-8"))


@app.get("/api/health")
def health():
    return {"status": "ok"}
