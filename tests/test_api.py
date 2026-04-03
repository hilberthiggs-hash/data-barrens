"""集成测试 —— 完整游戏流程（含认证）"""


def _register(client, name="hero", species="duck"):
    resp = client.post("/api/player/register", json={
        "email": f"{name}@test.com", "name": name, "buddy_species": species,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "api_token" in data
    return data


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_full_battle_flow(client):
    """注册 → 天梯匹配 → 查看日志"""
    player = _register(client, "warrior")
    pid = player["id"]
    token = player["api_token"]

    resp = client.post("/api/battle/ladder", headers=_auth(token))
    assert resp.status_code == 200
    battle = resp.json()
    assert len(battle["rounds"]) > 0
    assert battle["attacker"]["name"] == "warrior"
    assert "battles_remaining" in battle
    assert "loot" in battle

    resp = client.get(f"/api/battle/log/{battle['id']}")
    assert resp.status_code == 200

    resp = client.get(f"/api/battle/history/{pid}")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_pvp_with_loot(client):
    """玩家对战有装备掉落"""
    p1 = _register(client, "fighter1")
    p2 = _register(client, "fighter2")

    resp = client.post("/api/battle/challenge",
        headers=_auth(p1["api_token"]),
        json={"attacker_id": p1["id"], "defender_id": p2["id"]},
    )
    assert resp.status_code == 200
    assert "loot" in resp.json()


def test_cannot_challenge_npc(client):
    player = _register(client, "npcfighter")
    npc = client.get("/api/player/by-name/训练假人").json()
    resp = client.post("/api/battle/challenge",
        headers=_auth(player["api_token"]),
        json={"attacker_id": player["id"], "defender_id": npc["id"]},
    )
    assert resp.status_code == 400


def test_ladder(client):
    player = _register(client, "laddertest")
    resp = client.post("/api/battle/ladder", headers=_auth(player["api_token"]))
    assert resp.status_code == 200
    assert len(resp.json()["rounds"]) > 0


def test_battle_daily_limit(client):
    player = _register(client, "limittest")
    token = player["api_token"]

    for _ in range(3):
        resp = client.post("/api/battle/ladder", headers=_auth(token))
        assert resp.status_code == 200

    resp = client.post("/api/battle/ladder", headers=_auth(token))
    assert resp.status_code == 400
    assert "对战次数" in resp.json()["detail"]


def test_explore_auto_equip(client):
    """探索后自动择优穿戴"""
    player = _register(client, "explorer")
    pid = player["id"]
    token = player["api_token"]

    resp = client.post("/api/explore", headers=_auth(token))
    assert resp.status_code == 200
    assert "stamina_remaining" in resp.json()
    assert "auto_equip" in resp.json()

    # 第一件装备应该自动穿戴
    resp = client.get(f"/api/equipment/{pid}/list")
    assert resp.status_code == 200
    equips = resp.json()
    assert len(equips) >= 1
    assert any(e["equipped"] for e in equips)


def test_ranking(client):
    _register(client, "rank1")
    _register(client, "rank2")
    resp = client.get("/api/ranking/elo")
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


def test_cannot_fight_self(client):
    player = _register(client, "solo")
    resp = client.post("/api/battle/challenge",
        headers=_auth(player["api_token"]),
        json={"attacker_id": player["id"], "defender_id": player["id"]},
    )
    assert resp.status_code == 400


def test_auth_required(client):
    """写接口没 token 应返回 401"""
    resp = client.post("/api/explore")
    assert resp.status_code == 401

    resp = client.post("/api/battle/ladder")
    assert resp.status_code == 401


def test_wrong_token(client):
    resp = client.post("/api/explore", headers={"Authorization": "Bearer wrong_token"})
    assert resp.status_code == 401


def test_skill_list(client):
    player = _register(client, "skilltest")
    resp = client.get(f"/api/skill/{player['id']}/list")
    assert resp.status_code == 200
    assert resp.json() == []
