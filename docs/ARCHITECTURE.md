# Embers World Architecture

## System Identity

Embers World is no longer a static HTML site. The project is now a RuleBook Platform.

The core asset is rule data. The core system is the RuleBook Engine.

## Top-Level Flow

```text
                data_sources
                     |
                     v
          RuleBook Import Pipeline
                     |
                     v
              Django Data Models
                     |
        +------------+------------+
        |            |            |
        v            v            v
    RuleBook API  Search API  Glossary API
        |            |            |
        +------------+------------+
                     |
                     v
               Vue RuleBook
                     |
        +------------+------------+
        |            |            |
        v            v            v
 Character Engine  Lore Engine  AI Engine
```

## Project Layers

```text
Alpha
  Project Skeleton
  Rule Importer
  Vue Validation
  RuleBook Architecture

RuleBook Engine
  RBE-001 Import Pipeline
  RBE-002 RuleBook Integrity
  RBE-003 RuleBook API
  RBE-004 RuleBook Renderer
  RBE-005 Search

Rule Content
  RC-001 Core
  RC-002 Races
  RC-003 Martial
  RC-004 Divine
  RC-005 Arcane

Character Engine
  CE-001 Schema
  CE-002 Calculator
  CE-003 Character Builder
  CE-004 Save

Lore Engine
  LE-001 World
  LE-002 Nations
  LE-003 Timeline

AI Engine
  AE-001 Search
  AE-002 Rule QA
  AE-003 Character Assistant
  AE-004 GM Assistant
```

## Data Sources

`data_sources/` is the official source of durable project data.

Current official sources:

```text
data_sources/rulebook/chapters.json
data_sources/rules/*.json
```

Legacy sources:

```text
data/
pages/
index.html
```

Legacy files may be used for reference only. New importers must not read from `data/`.

## RuleBook Engine

The RuleBook Engine converts structured data into durable backend models.

Current model chain:

```text
RuleBook
  -> RuleChapter
      -> RuleSection
          -> RuleEntry
              -> RuleContentBlock
```

Existing query models remain available:

```text
RuleCategory
Rule
GlossaryTerm
```

`Rule` and `RuleEntry` must not be forcibly merged until the migration path is proven.

## Backend

`backend/` owns:

```text
Django models
management commands
import pipeline
future RuleBook API
future Search API
SimpleUI admin
```

Backend work should remain additive and scoped. Importers, APIs, and validation commands should be implemented as separate milestones.

## Frontend

`frontend/` owns the future official product interface.

The current `/rules` page is a technical validation page. The future `/rules` page must become the migrated RuleBook reader, replacing the legacy `pages/rules.html` experience.

Vue should consume backend APIs. Vue should not hard-code rule content or read legacy `data/` files as official sources.

## Legacy Boundary

Legacy files are frozen as reference:

```text
pages/rules.html
data/page-render.js
data/ash-data.js
data/chapters.json
pages/rules.css
```

Do not continue feature development in the legacy rule page.

## Future Engines

Character, lore, and AI systems should depend on the RuleBook Engine instead of duplicating rules.

Expected dependencies:

```text
Character Engine -> RuleBook Engine
Lore Engine      -> data_sources + backend APIs
AI Engine        -> RuleBook Engine + Search
```

This keeps rules, character calculations, search, and AI answers aligned to the same source of truth.
