# Arena Game - 数据荒原 异步竞技 RPG

## 一、游戏世界观「数据荒原」(Data Wasteland)

在代码编译的尽头，存在一片被遗忘的内存荒原。散落着无主的数据碎片，而你的 Buddy —— 那个一直陪你写代码的小家伙 —— 某天意外跌入了这片荒原。

在这里，Buddy 们觉醒了战斗本能。它们在荒原中探索、成长、对抗，争夺「最强编译体」的称号。每个 Buddy 都继承了主人的某种气质，却发展出了完全不同的战斗风格。

荒原中流传着一个传说：当一个 Buddy 集齐所有流派的精髓，就能打开通往「源代码圣殿」的大门......

## 二、核心玩法

### 2.1 角色体系

注册时绑定 Buddy 外观（species/eye/hat/shiny）作为形象。
属性、技能、装备全部从零开始，不继承 Buddy 属性。

**四维属性：** STR(力量) / AGI(敏捷) / INT(智力) / VIT(体质)
**克制环：** STR > AGI > INT > VIT > STR

### 2.2 战斗系统

- 异步自动战斗，回合制，最多 10 回合
- 每回合按速度决定出手顺序 → 自动选择技能 → 结算伤害
- 平局判定：剩余 HP% 高者胜
- 战斗产出详细日志

### 2.3 成长系统

**升级：**
- 战斗获得经验（胜负都有，胜方多）
- 升级获属性点（递减：Lv1-10 +5/级，Lv11-20 +3/级，Lv21-30 +1/级）
- 上限 Lv30

**技能树：**
```
STR: 重击(Lv3) → 破甲(Lv8) → 狂暴(Lv15)
AGI: 闪避(Lv3) → 连击(Lv8) → 暗杀(Lv15)
INT: 火球(Lv3) → 冰冻(Lv8) → 湮灭(Lv15)
VIT: 格挡(Lv3) → 反伤(Lv8) → 再生(Lv15)
```
- 最多装备 3 个技能

**装备：**
- 稀有度：白/绿/蓝/紫/橙
- 槽位：武器/护甲/饰品
- 探索获取，同名同稀有度 x3 合成升一级

### 2.4 体力系统

- 每日 20 点体力（UTC+8 零点刷新）
- 消耗：战斗 1 点、探索 2 点
- 新人前 7 天双倍（40 点/天）

### 2.5 追赶与平衡

- 属性点递减
- 全局可挑战，ELO 差距调节收益
- AI NPC 冷启动
- 复仇免体力
- 月度赛季 ELO 软重置

### 2.6 排行榜

- ELO / 等级 / 赛季胜率

## 三、技术方案

### 3.1 技术栈

Python 3.10+ / FastAPI / SQLite / SQLAlchemy / pytest + httpx

### 3.2 项目结构

```
/Users/admin/arena-game/
├── server/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置
│   ├── models.py            # SQLAlchemy 模型
│   ├── schemas.py           # Pydantic schema
│   ├── db.py                # 数据库连接
│   ├── routers/
│   │   ├── player.py        # 注册、查看、分配属性
│   │   ├── battle.py        # 挑战、复仇、日志
│   │   ├── explore.py       # 探索装备
│   │   ├── equipment.py     # 装备管理、合成
│   │   ├── skill.py         # 技能管理
│   │   └── ranking.py       # 排行榜
│   ├── services/
│   │   ├── battle_engine.py # 战斗引擎（纯函数）
│   │   ├── player_service.py
│   │   ├── explore_service.py
│   │   ├── equipment_service.py
│   │   └── ranking_service.py
│   └── game_data/
│       ├── skills.py        # 技能定义
│       ├── equipment.py     # 装备模板
│       ├── npcs.py          # NPC 定义
│       └── lore.py          # 世界观叙事
├── tests/
│   ├── test_battle_engine.py
│   ├── test_player.py
│   ├── test_explore.py
│   ├── test_equipment.py
│   └── test_api.py
├── requirements.txt
└── README.md
```

### 3.3 核心数据模型

**Player:** id, name, buddy_species/eye/hat/shiny, level, exp, elo, str/agi/int/vit, unallocated_points, stamina, stamina_refreshed_at, created_at, is_npc

**Equipment:** id, player_id, slot, name, rarity, str/agi/int/vit_bonus, equipped

**BattleLog:** id, attacker_id, defender_id, winner_id, rounds_json, elo_change, exp_gained, created_at

**PlayerSkill:** id, player_id, skill_id, equipped

### 3.4 API

```
POST   /api/player/register        # 注册
GET    /api/player/{id}            # 查看角色
POST   /api/player/allocate        # 分配属性点
POST   /api/player/equip-skill     # 装备技能

POST   /api/battle/challenge       # 挑战
POST   /api/battle/revenge/{id}    # 复仇
GET    /api/battle/log/{id}        # 战斗日志
GET    /api/battle/history         # 战斗历史

POST   /api/explore                # 探索
POST   /api/equipment/merge        # 合成
POST   /api/equipment/equip        # 穿戴
POST   /api/equipment/unequip      # 卸下
GET    /api/equipment/list         # 背包

GET    /api/ranking/elo            # ELO 排行
GET    /api/ranking/level          # 等级排行
```

## 四、开发计划

### Phase 1: 核心骨架
项目初始化、数据模型、玩家注册/查看/属性分配 + 测试

### Phase 2: 战斗系统
战斗引擎、技能系统、ELO、挑战/复仇 API + 测试

### Phase 3: 探索与装备
探索、装备管理/合成、体力系统 + 测试

### Phase 4: 排行榜与 NPC
排行榜、NPC、赛季、世界观叙事 + 集成测试

### Phase 5: Claude Code Skill
skill 定义、API 封装、文本渲染
