"""玩家系统测试 —— 通过 API 测试"""


def test_register_player(client):
    resp = client.post("/api/player/register", json={
        "name": "testplayer",
        "buddy_species": "duck",
        "buddy_eye": "✦",
        "buddy_hat": "crown",
        "buddy_shiny": True,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "testplayer"
    assert data["buddy_species"] == "duck"
    assert data["buddy_shiny"] is True
    assert data["level"] == 1
    assert data["elo"] == 1000.0
    assert data["str"] == 5
    assert data["agi"] == 5


def test_register_duplicate_name(client):
    client.post("/api/player/register", json={"name": "dup"})
    resp = client.post("/api/player/register", json={"name": "dup"})
    assert resp.status_code == 400
    assert "已被占用" in resp.json()["detail"]


def test_get_player(client):
    resp = client.post("/api/player/register", json={"name": "getme"})
    pid = resp.json()["id"]
    resp = client.get(f"/api/player/{pid}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "getme"


def test_get_player_by_name(client):
    client.post("/api/player/register", json={"name": "findme"})
    resp = client.get("/api/player/by-name/findme")
    assert resp.status_code == 200
    assert resp.json()["name"] == "findme"


def test_get_player_not_found(client):
    resp = client.get("/api/player/9999")
    assert resp.status_code == 404


def test_allocate_points(client):
    # 先创建一个有属性点的玩家（通过直接修改数据库）
    resp = client.post("/api/player/register", json={"name": "alloctest"})
    pid = resp.json()["id"]

    # 新玩家没有未分配属性点，应该失败
    resp = client.post(f"/api/player/{pid}/allocate", json={"str": 1})
    assert resp.status_code == 400


def test_npcs_exist(client):
    """NPC 应该在初始化时创建"""
    resp = client.get("/api/player/by-name/训练假人")
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_npc"] is True
    assert data["buddy_species"] == "robot"


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
