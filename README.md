# ⚔️ Data Barrens

> *Your Buddy has fallen into a forgotten memory wasteland. The only way out is to fight.*

Async PvP RPG that runs inside [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Fight real players, loot their gear, collect equipment sets, climb the ELO ladder — all from your terminal.

```
═══════════════════════════════════════════
     \^^^/          alice
  /^\  /^\          🐉 dragon  ✦ 👑
 <  ✦  ✦  >        Lv.15 | ELO 1523
 (   ~~   )        ⚡ Stamina 18/20
  `-vvvv-´         ─────────────────
                   STR 25 | AGI 18
                   INT 12 | VIT 20
───────────────────────────────────────────
  ⚔️ Skills: Heavy Strike / Fireball / Block
  🛡️ Weapon: [Rare] Flame Greatsword
     Armor:  [Rare] Flame Cuirass
     Acc:    [Rare] Flame Pendant
  🔥 Set Bonus: Flame Awakening (3pc)
     STR +13, INT +3, Crit DMG +20%
═══════════════════════════════════════════

  ⚔️ ═══ alice vs Memory Leak Blob ═══ ⚔️

    The data streams fell silent...

    ── Round 1 ──
    alice uses Fireball → Memory Leak Blob -72 HP
    Memory Leak Blob attacks | alice uses Block, -40% → -10 HP

    ── Round 2 ──
    alice uses Heavy Strike → Memory Leak Blob -73 HP
    Memory Leak Blob attacks (CRIT!) → alice -45 HP

    ── Round 3 ──
    alice uses Fireball → Memory Leak Blob -72 HP
    [Memory Leak Blob HP: 0]

    ══════════════════════════════
    🏆 Winner: alice
    📊 ELO: 1500 → 1523 (+22.9)
    ✨ EXP: +80
    ══════════════════════════════
```

**18 buddy species** — your appearance is deterministically generated from your Claude Code identity:

`duck 🦆 · goose 🪿 · blob 🫧 · cat 🐱 · dragon 🐉 · octopus 🐙 · owl 🦉 · penguin 🐧 · turtle 🐢 · snail 🐌 · ghost 👻 · axolotl 🦎 · capybara 🦫 · cactus 🌵 · robot 🤖 · rabbit 🐰 · mushroom 🍄 · chonk 🐖`

## Play Now (Public Server)

One command to install:

```bash
mkdir -p ~/.claude/skills/barren && curl -sL https://raw.githubusercontent.com/hilberthiggs-hash/data-barrens/main/skill/SKILL.md -o ~/.claude/skills/barren/SKILL.md && echo "✅ Installed"
```

Restart Claude Code, type `/barren`. Character auto-created on first use.

## Self-Host Your Own Server

Run a private server for your team in under a minute:

### Docker (recommended)

```bash
git clone https://github.com/hilberthiggs-hash/data-barrens.git
cd data-barrens
docker compose up -d
```

Server runs at `http://localhost:21520`. Verify: `curl http://localhost:21520/api/health`

### Without Docker

```bash
git clone https://github.com/hilberthiggs-hash/data-barrens.git
cd data-barrens
pip install -r requirements.txt
uvicorn server.main:app --host 0.0.0.0 --port 8000
```

### Install Skill (pointing to your server)

```bash
# Replace with your server URL
curl -sL https://raw.githubusercontent.com/hilberthiggs-hash/data-barrens/main/install.sh | bash -s https://your-server:21520
```

Or manually:
```bash
mkdir -p ~/.claude/skills/barren && curl -sL https://raw.githubusercontent.com/hilberthiggs-hash/data-barrens/main/skill/SKILL.md -o ~/.claude/skills/barren/SKILL.md
# Edit ~/.claude/skills/barren/SKILL.md — change BASE_URL to your server
```

## Game Features

### Commands

| Command | Description |
|---------|-------------|
| `/barren explore` | Explore for equipment (-4 stamina) |
| `/barren ladder` | Ranked match, safe leveling (-2 stamina) |
| `/barren fight <name>` | Challenge a player (50% loot!) |
| `/barren status` | View character |
| `/barren bag` | Inventory |
| `/barren skills` | Skills (auto-equipped) |
| `/barren rank` | Leaderboard |
| `/barren merge` | Merge 3→1 rarity upgrade |
| `/barren lang [en/zh]` | Switch language |

### Equipment Sets

5 themed sets with 2-piece and 3-piece bonuses:

| Set | Focus | 2pc | 3pc |
|-----|-------|-----|-----|
| 🔥 Flame | STR | STR +5 | STR +8, INT +3 |
| 🌑 Shadow | AGI | AGI +5 | AGI +8, STR +3 |
| ❄️ Frost | INT | INT +5 | INT +8, VIT +3 |
| 🛡️ Guardian | VIT | VIT +5 | VIT +8, STR +3 |
| 🌀 Chaos | All | All +3 | All +5 |

Smart auto-equip evaluates all gear combinations including set bonuses.

### Skills

24 skills across 4 stat trees (STR/AGI/INT/VIT × 6 each). Auto-equipped by damage/utility score on level-up.

### 30 Equipment Templates × 5 Rarities

Common ★ · Uncommon ★★ · Rare ★★★ · Epic ★★★★ · Legendary ★★★★★

### 18 Buddy Species

Deterministically generated from your Claude Code identity.

## Architecture

```
Client (Claude Code)          Server (FastAPI + SQLite)
┌─────────────────┐          ┌──────────────────────┐
│   SKILL.md      │  HTTP    │  /api/player/*       │
│   (instructs    │ -------> │  /api/battle/*       │
│    Claude how   │ <------- │  /api/explore        │
│    to call API) │  JSON    │  /api/equipment/*    │
└─────────────────┘          │  /api/skill/*        │
                             │  /api/ranking/*      │
                             └──────────────────────┘
                                      │
                             ┌────────┴────────┐
                             │   SQLite (arena.db)  │
                             └─────────────────────┘
```

- **No client-side code** — SKILL.md is pure markdown instructions for Claude
- **SQLite** — zero config, data persists in a single file
- **Stateless API** — token-based auth, no sessions

## API

All read endpoints are public. Write endpoints require `Authorization: Bearer <token>`.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/player/register` | - | Register |
| GET | `/api/player/by-name/{name}` | - | Player info |
| POST | `/api/battle/challenge` | ✅ | PvP fight |
| POST | `/api/battle/ladder` | ✅ | Ranked match |
| POST | `/api/explore` | ✅ | Explore |
| GET | `/api/equipment/{id}/list` | - | Inventory |
| GET | `/api/ranking/elo` | - | Leaderboard |
| GET | `/api/health` | - | Health check |

## License

MIT

---

# ⚔️ 数据荒原

运行在 Claude Code 里的异步竞技 RPG。挑战真人玩家、抢夺装备、收集套装 —— 全在终端完成。

## 玩公共服

```bash
mkdir -p ~/.claude/skills/barren && curl -sL https://raw.githubusercontent.com/hilberthiggs-hash/data-barrens/main/skill/SKILL.md -o ~/.claude/skills/barren/SKILL.md && echo "✅ 安装成功"
```

重启 Claude Code，输入 `/barren`。

## 自建私服

```bash
git clone https://github.com/hilberthiggs-hash/data-barrens.git
cd data-barrens
docker compose up -d
```

安装 skill 指向你的服务器：

```bash
curl -sL https://raw.githubusercontent.com/hilberthiggs-hash/data-barrens/main/install.sh | bash -s https://你的服务器:21520
```

详细说明见上方英文文档。
