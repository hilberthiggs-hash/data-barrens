"""集成测试 —— 完整游戏流程"""


def _register(client, name="hero", species="duck"):
    resp = client.post("/api/player/register", json={
        "email": f"{name}@test.com", "name": name, "buddy_species": species,
    })
    assert resp.status_code == 200
    return resp.json()


def test_full_battle_flow(client):
    """注册 → 挑战 NPC → 查看日志"""
    player = _register(client, "warrior")
    pid = player["id"]

    npc = client.get("/api/player/by-name/训练假人").json()

    resp = client.post("/api/battle/challenge", json={
        "attacker_id": pid,
        "defender_id": npc["id"],
    })
    assert resp.status_code == 200
    battle = resp.json()
    assert len(battle["rounds"]) > 0
    assert battle["attacker"]["name"] == "warrior"
    assert battle["defender"]["name"] == "训练假人"
    assert "battles_remaining" in battle
    assert "loot" in battle

    # 查看战斗日志
    resp = client.get(f"/api/battle/log/{battle['id']}")
    assert resp.status_code == 200

    # 查看战斗历史
    resp = client.get(f"/api/battle/history/{pid}")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_ladder(client):
    """天梯匹配"""
    player = _register(client, "laddertest")
    pid = player["id"]

    resp = client.post(f"/api/battle/ladder/{pid}")
    assert resp.status_code == 200
    battle = resp.json()
    assert len(battle["rounds"]) > 0
    assert "battles_remaining" in battle


def test_battle_daily_limit(client):
    """对战次数限制"""
    player = _register(client, "limittest")
    pid = player["id"]
    npc = client.get("/api/player/by-name/训练假人").json()

    # 打 3 次
    for _ in range(3):
        resp = client.post("/api/battle/challenge", json={
            "attacker_id": pid, "defender_id": npc["id"],
        })
        assert resp.status_code == 200

    # 第 4 次应该失败
    resp = client.post("/api/battle/challenge", json={
        "attacker_id": pid, "defender_id": npc["id"],
    })
    assert resp.status_code == 400
    assert "对战次数" in resp.json()["detail"]


def test_explore_and_equip(client):
    """探索 → 获得装备 → 穿戴"""
    player = _register(client, "explorer")
    pid = player["id"]

    resp = client.post(f"/api/explore/{pid}")
    assert resp.status_code == 200
    explore_result = resp.json()
    assert "narrative" in explore_result

    equip_id = explore_result["equipment"]["id"]

    resp = client.post(f"/api/equipment/equip?player_id={pid}&equipment_id={equip_id}")
    assert resp.status_code == 200
    assert resp.json()["equipped"] is True

    resp = client.get(f"/api/equipment/{pid}/list")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

    resp = client.post(f"/api/equipment/unequip?player_id={pid}&equipment_id={equip_id}")
    assert resp.status_code == 200
    assert resp.json()["equipped"] is False


def test_ranking(client):
    _register(client, "rank1")
    _register(client, "rank2")

    resp = client.get("/api/ranking/elo")
    assert resp.status_code == 200
    assert len(resp.json()) >= 2

    resp = client.get("/api/ranking/level")
    assert resp.status_code == 200


def test_cannot_fight_self(client):
    player = _register(client, "solo")
    pid = player["id"]
    resp = client.post("/api/battle/challenge", json={
        "attacker_id": pid, "defender_id": pid,
    })
    assert resp.status_code == 400


def test_skill_list(client):
    player = _register(client, "skilltest")
    pid = player["id"]
    resp = client.get(f"/api/skill/{pid}/list")
    assert resp.status_code == 200
    assert resp.json() == []
