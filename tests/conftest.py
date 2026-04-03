import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi import FastAPI
from fastapi.testclient import TestClient

from server.db import Base, get_db
import server.models  # 确保模型注册到 Base.metadata
from server.routers import player, battle, explore, equipment, skill, ranking
from server.services.npc_service import init_npcs


def create_test_app() -> FastAPI:
    """创建无 lifespan 的测试 app"""
    test_app = FastAPI()
    test_app.include_router(player.router)
    test_app.include_router(battle.router)
    test_app.include_router(explore.router)
    test_app.include_router(equipment.router)
    test_app.include_router(skill.router)
    test_app.include_router(ranking.router)

    @test_app.get("/api/health")
    def health():
        return {"status": "ok"}

    return test_app


@pytest.fixture()
def db_session():
    """每个测试使用独立的内存数据库"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    """FastAPI 测试客户端，注入测试数据库"""
    test_app = create_test_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    test_app.dependency_overrides[get_db] = override_get_db
    init_npcs(db_session)

    with TestClient(test_app) as c:
        yield c

    test_app.dependency_overrides.clear()
