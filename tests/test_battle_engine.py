"""战斗引擎单元测试 —— 纯函数，不依赖数据库"""
from server.services.battle_engine import build_fighter, run_battle, calc_elo_change, calc_exp_reward


def test_build_fighter_basic():
    f = build_fighter("test", 10, 10, 10, 10)
    assert f.name == "test"
    assert f.max_hp > 0
    assert f.atk > 0
    assert f.speed > 0
    assert f.hp == f.max_hp


def test_build_fighter_with_equip_bonus():
    f1 = build_fighter("base", 10, 10, 10, 10)
    f2 = build_fighter("buffed", 10, 10, 10, 10, equip_str=5, equip_vit=5)
    assert f2.atk > f1.atk
    assert f2.max_hp > f1.max_hp


def test_battle_produces_result():
    a = build_fighter("Alice", 15, 10, 5, 10)
    b = build_fighter("Bob", 5, 10, 15, 10)
    winner, rounds = run_battle(a, b, seed=42)
    assert len(rounds) > 0
    assert len(rounds) <= 10
    assert all(r.round_num > 0 for r in rounds)


def test_battle_deterministic_with_seed():
    a1 = build_fighter("A", 15, 10, 5, 10)
    b1 = build_fighter("B", 5, 10, 15, 10)
    w1, r1 = run_battle(a1, b1, seed=123)

    a2 = build_fighter("A", 15, 10, 5, 10)
    b2 = build_fighter("B", 5, 10, 15, 10)
    w2, r2 = run_battle(a2, b2, seed=123)

    assert w1 == w2
    assert len(r1) == len(r2)


def test_battle_with_skills():
    a = build_fighter("Warrior", 20, 8, 5, 10, skill_ids=["heavy_strike", "armor_break"])
    b = build_fighter("Mage", 5, 8, 20, 10, skill_ids=["fireball", "freeze"])
    winner, rounds = run_battle(a, b, seed=99)
    assert winner is not None or len(rounds) == 10


def test_elo_change_symmetric():
    w_change, l_change = calc_elo_change(1000, 1000)
    assert w_change > 0
    assert l_change < 0
    assert abs(w_change + l_change) < 0.5  # 基本对称


def test_elo_underdog_gets_more():
    # 弱者赢了应该获得更多 ELO
    w1, _ = calc_elo_change(800, 1200)   # 弱者赢强者
    w2, _ = calc_elo_change(1200, 800)   # 强者赢弱者
    assert w1 > w2


def test_exp_reward():
    w_exp, l_exp = calc_exp_reward(10, 10)
    assert w_exp > l_exp > 0


def test_exp_bonus_for_underdog():
    w1, _ = calc_exp_reward(5, 15)   # 以弱胜强
    w2, _ = calc_exp_reward(15, 5)   # 以强胜弱
    assert w1 > w2


def test_one_shot_kill():
    """强者 vs 极弱，应该很快结束"""
    a = build_fighter("Giant", 50, 30, 30, 30, skill_ids=["berserk", "heavy_strike"])
    b = build_fighter("Weakling", 1, 1, 1, 1)
    winner, rounds = run_battle(a, b, seed=42)
    assert winner == "Giant"
    assert len(rounds) <= 3
