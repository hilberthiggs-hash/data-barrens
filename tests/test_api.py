"""集成测试 —— 完整游戏流程"""
import json


def _register(client, name="hero", species="duck"):
    resp = client.post("/api/player/register", json={
        "name": name, "buddy_species": species,
    })
    assert resp.status_code == 200
    return resp.json()


def test_full_battle_flow(client):
    """注册 → 挑战 NPC → 查看日志"""
    player = _register(client, "warrior")
    pid = player["id"]

    # 挑战训练假人
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

    # 查看战斗日志
    resp = client.get(f"/api/battle/log/{battle['id']}")
    assert resp.status_code == 200

    # 查看战斗历史
    resp = client.get(f"/api/battle/history/{pid}")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_explore_and_equip(client):
    """探索 → 获得装备 → 穿戴"""
    player = _register(client, "explorer")
    pid = player["id"]

    resp = client.post(f"/api/explore/{pid}")
    assert resp.status_code == 200
    explore_result = resp.json()
    assert "narrative" in explore_result
    assert explore_result["equipment"]["name"]

    equip_id = explore_result["equipment"]["id"]

    # 穿戴
    resp = client.post(f"/api/equipment/equip?player_id={pid}&equipment_id={equip_id}")
    assert resp.status_code == 200
    assert resp.json()["equipped"] is True

    # 查看背包
    resp = client.get(f"/api/equipment/{pid}/list")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

    # 卸下
    resp = client.post(f"/api/equipment/unequip?player_id={pid}&equipment_id={equip_id}")
    assert resp.status_code == 200
    assert resp.json()["equipped"] is False


def test_ranking(client):
    """排行榜"""
    _register(client, "rank1")
    _register(client, "rank2")

    resp = client.get("/api/ranking/elo")
    assert resp.status_code == 200
    data = resp.json()
    # NPC + 2 个玩家
    assert len(data) >= 2

    resp = client.get("/api/ranking/level")
    assert resp.status_code == 200


def test_cannot_fight_self(client):
    player = _register(client, "solo")
    pid = player["id"]
    resp = client.post("/api/battle/challenge", json={
        "attacker_id": pid, "defender_id": pid,
    })
    assert resp.status_code == 400


def test_revenge(client):
    """复仇流程"""
    p1 = _register(client, "attacker1")
    p2 = _register(client, "defender1")

    # p1 挑战 p2
    resp = client.post("/api/battle/challenge", json={
        "attacker_id": p1["id"], "defender_id": p2["id"],
    })
    battle = resp.json()
    battle_id = battle["id"]

    # p2 复仇（无论胜负都可以复仇，只要 p2 是被挑战方且输了）
    # 如果 p2 赢了，复仇应该返回错误
    if battle["winner_name"] == p2["name"]:
        resp = client.post(f"/api/battle/revenge/{battle_id}?player_id={p2['id']}")
        assert resp.status_code == 400
    else:
        resp = client.post(f"/api/battle/revenge/{battle_id}?player_id={p2['id']}")
        assert resp.status_code == 200
        assert resp.json()["is_revenge"] is True


def test_skill_list_and_equip(client):
    """技能列表（新玩家无技能）"""
    player = _register(client, "skilltest")
    pid = player["id"]

    resp = client.get(f"/api/skill/{pid}/list")
    assert resp.status_code == 200
    # Lv1 玩家没有解锁任何技能
    assert resp.json() == []
