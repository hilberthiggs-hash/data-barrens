"""
从 Claude Code userId 确定性生成 Buddy 外观。
算法完全复现自 claude-code/src/buddy/companion.ts。
"""
import math

SPECIES = [
    "duck", "goose", "blob", "cat", "dragon", "octopus", "owl", "penguin",
    "turtle", "snail", "ghost", "axolotl", "capybara", "cactus", "robot",
    "rabbit", "mushroom", "chonk",
]
EYES = ["·", "✦", "×", "◉", "@", "°"]
HATS = ["none", "crown", "tophat", "propeller", "halo", "wizard", "beanie", "tinyduck"]
RARITIES = ["common", "uncommon", "rare", "epic", "legendary"]
RARITY_WEIGHTS = {"common": 60, "uncommon": 25, "rare": 10, "epic": 4, "legendary": 1}
SALT = "friend-2026-401"


def _hash_string(s: str) -> int:
    """FNV-1a hash, 同 companion.ts 中的 hashString（非 Bun 分支）"""
    h = 2166136261
    for ch in s:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def _make_mulberry32(seed: int):
    """Mulberry32 PRNG，同 companion.ts"""
    a = [seed & 0xFFFFFFFF]

    def _to_int32(x):
        x = x & 0xFFFFFFFF
        return x - 0x100000000 if x >= 0x80000000 else x

    def _to_uint32(x):
        return x & 0xFFFFFFFF

    def _imul(x, y):
        return ((_to_uint32(x)) * (_to_uint32(y))) & 0xFFFFFFFF

    def rng():
        a[0] = _to_int32(a[0])
        a[0] = _to_int32(a[0] + 0x6D2B79F5)
        a_u = _to_uint32(a[0])
        t = _imul(a_u ^ (a_u >> 15), (1 | a_u) & 0xFFFFFFFF)
        t = _to_uint32(t)
        t = _to_uint32((t + _imul(t ^ (t >> 7), (61 | t) & 0xFFFFFFFF)) & 0xFFFFFFFF) ^ t
        t = _to_uint32(t)
        return _to_uint32(t ^ (t >> 14)) / 4294967296

    return rng


def _pick(rng, arr):
    return arr[math.floor(rng() * len(arr))]


def _roll_rarity(rng):
    total = sum(RARITY_WEIGHTS.values())
    roll = rng() * total
    for r in RARITIES:
        roll -= RARITY_WEIGHTS[r]
        if roll < 0:
            return r
    return "common"


def resolve_buddy(user_id: str) -> dict:
    """
    从 userId 确定性生成 Buddy 外观。
    返回 {"species": ..., "eye": ..., "hat": ..., "shiny": ...}
    """
    seed = _hash_string(user_id + SALT)
    rng = _make_mulberry32(seed)

    rarity = _roll_rarity(rng)
    species = _pick(rng, SPECIES)
    eye = _pick(rng, EYES)
    hat = "none" if rarity == "common" else _pick(rng, HATS)
    shiny = rng() < 0.01

    return {
        "species": species,
        "eye": eye,
        "hat": hat,
        "shiny": shiny,
    }
