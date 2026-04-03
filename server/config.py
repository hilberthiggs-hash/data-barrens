import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.environ.get("ARENA_DB_PATH", str(BASE_DIR / "arena.db"))
DATABASE_URL = f"sqlite:///{DB_PATH}"

# 游戏常量
MAX_LEVEL = 30
DAILY_STAMINA = 20
NEWBIE_STAMINA = 40
NEWBIE_DAYS = 7
BATTLE_STAMINA_COST = 0  # 对战不消耗体力，改用每日次数限制
DAILY_BATTLE_LIMIT = 3  # 每日对战次数上限
LOOT_CHANCE = 0.3  # 胜者从败者背包抢装备的概率
EXPLORE_STAMINA_COST = 4
MAX_EQUIPPED_SKILLS = 3
MAX_BATTLE_ROUNDS = 10
MERGE_REQUIRED = 3  # 合成所需同名同稀有度装备数

# 每级属性点（递减）
def points_per_level(level: int) -> int:
    if level <= 10:
        return 5
    elif level <= 20:
        return 3
    else:
        return 1

# 升级所需经验
def exp_to_level_up(level: int) -> int:
    return 50 + level * 30

# ELO 常量
ELO_BASE = 1000
ELO_K = 32

# 初始属性
INITIAL_STATS = {"str_": 5, "agi": 5, "int_": 5, "vit": 5}
