# Embers World — 数据库设计

> **文档级别**: 架构设计
> **最后更新**: 2026-07-04
> **数据库**: MySQL 8.0+

---

## 1. 设计哲学

**数据库保存的是实体 (Entity)，不是网页。**

所有页面都是数据库渲染的结果。不要写死 HTML。

### 核心实体

| 实体 | 说明 | 对应当前 JSON |
|------|------|---------------|
| Rule | 游戏规则条目 | professions.json, story-rules.json |
| Lore | 世界观条目 | races.json, regions.json |
| Character | 玩家角色卡 | CloudBase characters 集合 |
| User | 用户账号 | CloudBase users 集合 |
| Tag | 标签 | links.json 中的 type |
| Version | 版本记录 | chapters.json 中的 version_status |
| Media | 媒体文件（图片） | — |
| Category | 分类 | chapters.json 中的章节结构 |
| Relation | 关联关系 | links.json |

---

## 2. ER 图 (Mermaid)

```mermaid
erDiagram
    User ||--o{ Character : owns
    User ||--o{ Session : participates
    Character ||--o{ CharacterLog : has
    Character ||--{ Rule : references

    Rule ||--o{ RuleTag : has
    Tag ||--o{ RuleTag : tagged_by
    Rule ||--o{ Relation : source
    Rule ||--o{ Relation : target
    Category ||--o{ Rule : categorizes
    Category ||--o{ Lore : categorizes
    Lore ||--o{ Relation : source
    Lore ||--o{ Relation : target
    Lore ||--o{ Lore : parent_of

    Glossary ||--o{ Relation : source
    Glossary ||--o{ Relation : target

    User {
        int id PK
        string username UK
        string email UK
        string phone
        string display_name
        string bio
        string avatar_url
        string gender
        datetime created_at
        datetime updated_at
    }

    Character {
        int id PK
        int user_id FK
        string name
        string race_id
        string profession_id
        int level
        json attributes
        json skills
        json equipment
        json background
        datetime created_at
        datetime updated_at
        boolean is_deleted
    }

    Rule {
        int id PK
        string title
        string slug UK
        text summary
        text content
        string category_id FK
        string chapter_ref
        int version_number
        string status
        datetime created_at
        datetime updated_at
    }

    Lore {
        int id PK
        string title
        string slug UK
        text summary
        text content
        string lore_type
        int parent_id FK
        string region
        datetime created_at
        datetime updated_at
    }

    Glossary {
        int id PK
        string term
        string key UK
        string category
        text definition
        text aliases
        datetime created_at
    }

    Tag {
        int id PK
        string name UK
        string color
    }

    Category {
        int id PK
        string name
        string slug UK
        int parent_id FK
        int sort_order
    }

    Relation {
        int id PK
        string source_type
        int source_id
        string relation_type
        string target_type
        int target_id
    }

    RuleTag {
        int rule_id FK
        int tag_id FK
    }

    CharacterLog {
        int id PK
        int character_id FK
        text content
        int session_number
        datetime created_at
    }

    Session {
        int id PK
        int user_id FK
        string title
        string role
        datetime created_at
    }

    Version {
        int id PK
        string entity_type
        int entity_id
        int version_number
        json snapshot
        string changed_by
        datetime created_at
    }
```

---

## 3. 表结构详细设计

### 3.1 users (用户)

```sql
CREATE TABLE users (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(25) UNIQUE NOT NULL,    -- CloudBase 规则: ^[a-z][0-9a-z_]{5,24}$
    email       VARCHAR(255) UNIQUE,
    phone       VARCHAR(20) UNIQUE,
    password    VARCHAR(255),                    -- Django PBKDF2 哈希
    display_name VARCHAR(50) DEFAULT '旅人',
    bio         TEXT,
    avatar_url  VARCHAR(500),
    gender      VARCHAR(10) DEFAULT '',          -- 男/女/其他
    is_active   BOOLEAN DEFAULT TRUE,
    is_staff    BOOLEAN DEFAULT FALSE,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 3.2 characters (角色卡)

```sql
CREATE TABLE characters (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id       BIGINT NOT NULL,
    name          VARCHAR(100) NOT NULL,
    race_id       VARCHAR(50),          -- 关联 races 表的 slug
    profession_id VARCHAR(50),          -- 关联 professions 表的 slug
    level         INT DEFAULT 1,
    attributes    JSON,                 -- {strength, agility, intellect, spirit}
    skills        JSON,                 -- 技能列表
    equipment     JSON,                 -- 装备列表
    background    TEXT,                 -- 背景故事
    is_deleted    BOOLEAN DEFAULT FALSE,
    deleted_at    DATETIME,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user (user_id),
    INDEX idx_deleted (is_deleted)
);
```

### 3.3 rules (规则)

```sql
CREATE TABLE rules (
    id             BIGINT AUTO_INCREMENT PRIMARY KEY,
    title          VARCHAR(200) NOT NULL,
    slug           VARCHAR(200) UNIQUE NOT NULL,
    summary        TEXT,
    content        LONGTEXT,             -- 富文本/Markdown
    category_id    BIGINT,
    chapter_ref    VARCHAR(20),          -- 如 "3.2.1"
    rule_type      VARCHAR(50),          -- profession/divine_art/story_rule
    level_table    JSON,                 -- 等级表数据
    version_number INT DEFAULT 1,
    status         VARCHAR(20) DEFAULT 'draft',  -- draft/pending/published
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    INDEX idx_type (rule_type),
    INDEX idx_status (status),
    FULLTEXT INDEX ft_content (title, summary, content)
);
```

### 3.4 lore (世界观)

```sql
CREATE TABLE lore (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(200) NOT NULL,
    slug        VARCHAR(200) UNIQUE NOT NULL,
    summary     TEXT,
    content     LONGTEXT,
    lore_type   VARCHAR(50),            -- race/deity/region/faction/event
    parent_id   BIGINT,                  -- 父条目 (如种族分支)
    region      VARCHAR(100),
    sort_order  INT DEFAULT 0,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES lore(id),
    INDEX idx_type (lore_type),
    FULLTEXT INDEX ft_lore (title, summary, content)
);
```

### 3.5 glossary (术语表)

```sql
CREATE TABLE glossary (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    term        VARCHAR(100) NOT NULL,
    `key`       VARCHAR(100) UNIQUE NOT NULL,
    category    VARCHAR(50),
    definition  TEXT NOT NULL,
    aliases     JSON,                   -- 别名数组
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    FULLTEXT INDEX ft_term (term, definition)
);
```

### 3.6 categories (分类)

```sql
CREATE TABLE categories (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    slug        VARCHAR(100) UNIQUE NOT NULL,
    parent_id   BIGINT,
    sort_order  INT DEFAULT 0,
    FOREIGN KEY (parent_id) REFERENCES categories(id)
);
```

### 3.7 tags (标签)

```sql
CREATE TABLE tags (
    id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    name    VARCHAR(50) UNIQUE NOT NULL,
    color   VARCHAR(7) DEFAULT '#c9a84c'
);

CREATE TABLE rule_tags (
    rule_id BIGINT NOT NULL,
    tag_id  BIGINT NOT NULL,
    PRIMARY KEY (rule_id, tag_id),
    FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);
```

### 3.8 relations (关联关系)

```sql
CREATE TABLE relations (
    id             BIGINT AUTO_INCREMENT PRIMARY KEY,
    source_type    VARCHAR(50) NOT NULL,   -- rule/lore/glossary
    source_id      BIGINT NOT NULL,
    relation_type  VARCHAR(50),             -- related/parent/child/references
    target_type    VARCHAR(50) NOT NULL,
    target_id      BIGINT NOT NULL,
    INDEX idx_source (source_type, source_id),
    INDEX idx_target (target_type, target_id)
);
```

### 3.9 sessions (游戏记录)

```sql
CREATE TABLE sessions (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id     BIGINT NOT NULL,
    title       VARCHAR(200),
    role        VARCHAR(50),              -- GM/Player
    notes       TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 3.10 character_logs (角色日志)

```sql
CREATE TABLE character_logs (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    character_id    BIGINT NOT NULL,
    session_number  INT,
    content         TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);
```

### 3.11 versions (版本快照)

```sql
CREATE TABLE versions (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    entity_type     VARCHAR(50) NOT NULL,   -- rule/lore/character
    entity_id       BIGINT NOT NULL,
    version_number  INT NOT NULL,
    snapshot        JSON NOT NULL,           -- 完整快照
    change_summary  TEXT,
    changed_by      BIGINT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (changed_by) REFERENCES users(id),
    INDEX idx_entity (entity_type, entity_id)
);
```

---

## 4. 数据迁移计划

### 当前 JSON → MySQL 映射

| JSON 文件 | 目标表 | 迁移脚本 |
|-----------|--------|----------|
| `races.json` (ancient/spirit_mixed/nature_psionic/human_branches) | `lore` (lore_type='race') | `migrate_races.py` |
| `races.json` (players) | `lore` (lore_type='player_race') | 同上 |
| `professions.json` | `rules` (rule_type='profession') | `migrate_professions.py` |
| `divine-arts.json` | `rules` (rule_type='divine_art') | `migrate_divine_arts.py` |
| `story-rules.json` | `rules` (rule_type='story_rule') | `migrate_story_rules.py` |
| `glossary.json` | `glossary` | `migrate_glossary.py` |
| `chapters.json` | `categories` | `migrate_chapters.py` |
| `links.json` | `relations` | `migrate_links.py` |
| CloudBase `users` | `users` | `migrate_users.py` |
| CloudBase `characters` | `characters` | `migrate_characters.py` |
| CloudBase `sessions` | `sessions` | `migrate_sessions.py` |

### 迁移原则

1. **不丢失数据** — 保留原始 JSON 文件作为备份
2. **保留关联** — links.json 中的关联关系必须正确映射
3. **可回滚** — 每个迁移脚本都有对应的回滚脚本
4. **分批执行** — 先迁移规则/世界观/术语，再迁移用户数据
