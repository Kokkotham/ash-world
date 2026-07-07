# Embers World 本地规则数据包接入说明

> 状态：数据源接入准备
> 来源：`C:\Users\林鹏\.qclaw\workspace\灰烬世界_完整开发包`
> 目标目录：`data_sources/rules/`

## 1. 目的

本目录用于保存 Embers World 的正式规则数据源，优先服务第一阶段的规则查询系统。

这些 JSON 文件来自本地完整开发包，已经过结构化整理。它们不是临时前端数据，也不是最终数据库结构，而是后续 Django importer 的权威输入来源。

当前使用顺序：

```text
data_sources/rules/*.json
↓
Django importer
↓
MySQL
↓
DRF API
↓
Vue 规则查询 UI
```

## 2. 已接入的数据文件

| 文件 | 内容 | 第一阶段用途 |
|------|------|--------------|
| `01_核心属性_结构化.json` | 四大属性、衍生公式、角色创建规则 | 规则查询；后续角色卡计算参考 |
| `02_种族_结构化.json` | 16 个种族完整结构化数据 | 规则查询；后续角色卡种族选择 |
| `03_武器专修_结构化.json` | 6 类武器专修与等级表 | 规则查询 |
| `04_武技系统_结构化.json` | 武技、连击、衔接、烬能技 | 规则查询 |
| `05_神术系统_完整_结构化.json` | 8 神系神术数据 | 神术查询 |
| `05_非奥法专修_结构化.json` | 知识、交流、艺术、生存、特殊专修 | 规则查询 |
| `06_战斗造诣_结构化.json` | 战斗造诣数据 | 规则查询 |
| `灰烬世界_奥法专修_结构化.json` | 奥法派系、模块、呈现、聚变、等级表 | 奥法规则查询；后续法术工具参考 |

## 3. 暂不接入的内容

以下文件暂时不纳入主项目数据源：

- `character_schema.json`
- `characters.json`
- `character_api_server.py`
- `spell_api_server.py`

原因：

1. 当前阶段只做规则查询系统。
2. 角色卡系统属于后续阶段。
3. standalone API 只能作为原型参考，不能直接并入 Django 正式后端。
4. 当前不处理用户系统、角色保存、战役管理或 CloudBase 迁移。

## 4. 后端现状

当前 Django backend 已有基础规则模型：

- `RuleCategory`
- `Rule`
- `GlossaryTerm`

这些模型足够支撑最小规则导入验证。

第一版 importer 应优先使用现有模型，不要过度拆表。

## 5. Importer 设计原则

建议 importer 路径：

```text
backend/apps/importer/management/commands/import_rule_sources.py
```

第一版 importer 目标：

1. 从 `data_sources/rules/` 读取 JSON。
2. 按数据文件生成 `RuleCategory`。
3. 按条目生成 `Rule`。
4. `raw_data` 保留原始 JSON 片段。
5. `content_blocks` 保存结构化正文或表格块。
6. `content` 保存可渲染的简化正文。
7. 使用稳定 slug，保证前端链接长期可用。
8. 支持重复执行，使用 slug upsert。
9. 不删除旧数据，除非未来明确加入 `--reset`。

## 6. 不允许事项

当前阶段禁止：

- 直接开发角色卡系统。
- 直接开发用户系统。
- 直接开发战役系统。
- 把 `character_api_server.py` 并入 Django。
- 把 `spell_api_server.py` 当作正式后端。
- 为复杂规则一次性设计大量关系表。
- 修改旧静态页面来消费这些数据。

## 7. 下一步任务建议

任务002：最小规则数据导入。

建议第一轮只导入：

1. `01_核心属性_结构化.json`
2. `02_种族_结构化.json`

验收目标：

- importer 可执行。
- 数据写入 MySQL。
- `/api/v1/rule-categories/` 能看到分类。
- `/api/v1/rules/` 能看到导入的规则。
- `raw_data` 和 `content_blocks` 保留原始结构。

通过后再逐步导入武器专修、武技、神术、非奥法专修、战斗造诣和奥法专修。
