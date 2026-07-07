# Embers World Project Constitution

## Current Mainline

Embers World has officially moved from Alpha into Beta.

The current product mainline is:

```text
data_sources/
  -> importer
  -> backend Django + DRF API
  -> frontend Vue rulebook
```

Beta development focuses on the Vue rulebook and the rule query system.

## Core Principle

规则数据优先于界面，数据模型优先于功能，长期可维护性优先于短期开发速度。

任何新增功能，都应建立在统一的数据模型之上，而不是直接面向页面实现。

## Source Of Truth

`data_sources/` is the single source of truth for rule data.

Rule JSON files should be organized as durable project assets first, then imported into the database through controlled importers. New features should consume rules through backend APIs instead of reading page-specific static assets directly.

## System Roles

`backend/` is the Django + DRF API core.

It owns data import, database models, API routes, and admin editing.

`frontend/` is the future official product frontend.

It owns the Vue rulebook, rule search, rule detail pages, and later product-facing tools.

## Legacy Boundary

`data/`, `pages/`, and the old `index.html` are now in legacy status.

They remain useful as historical reference and prototype material, but should not receive new feature development. Future product work should be implemented in `frontend/` and backed by `backend/` APIs.

## Deferred Scope

Character sheets are deferred.

They should be designed after the rule API and Vue rulebook are stable, so character data can depend on a unified and maintainable rule model instead of page-specific logic.
