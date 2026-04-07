# ⚔️ Data Barrens

Async PvP RPG that runs inside [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Fight real players, loot gear, collect equipment sets — all from your terminal.

```
⚔️ ═══ alice vs Memory Leak Blob ═══ ⚔️

  ── Round 1 ──
  alice uses Fireball → Memory Leak Blob -72 HP
  Memory Leak Blob attacks | alice uses Block, -40% → alice -10 HP

  ── Round 2 ──
  alice uses Heavy Strike → Memory Leak Blob -73 HP
  ...

  🏆 Winner: alice | ELO +22.9 | EXP +80
```

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

Server runs at `http://localhost:8000`. Verify: `curl http://localhost:8000/api/health`

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
curl -sL https://raw.githubusercontent.com/hilberthiggs-hash/data-barrens/main/install.sh | bash -s https://your-server:8000
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
curl -sL https://raw.githubusercontent.com/hilberthiggs-hash/data-barrens/main/install.sh | bash -s https://你的服务器:8000
```

详细说明见上方英文文档。
