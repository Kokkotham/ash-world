# RuleBook Implementation Boundary

## Purpose

This document defines the first implementation boundary for the Embers World RuleBook backend.

The goal is to prepare the official RuleBook data path without expanding scope into the full rule system, legacy HTML, Vue migration, or character sheet work.

## First Version Scope

The first RuleBook implementation may include:

- `RuleBook`
- `RuleChapter`
- `RuleSection`
- `RuleEntry`
- `RuleContentBlock`
- Django migration for these models
- `import_rulebook` management command
- read-only DRF API for RuleBook reading

The first importer may only import:

- `data_sources/rulebook/chapters.json`
- `data_sources/rules/01_核心属性_结构化.json`
- `data_sources/rules/02_种族_结构化.json`

The first importer should create:

- the core RuleBook record
- the chapter tree
- section hierarchy
- core attribute entries
- race entries
- content blocks for chapter, section, and entry content

## Data Source Rule

`data_sources/` is the only official data source for new RuleBook work.

The importer must not read from legacy `data/`.

`data/` remains legacy reference material for the old static site and should not be treated as the official source for new backend importers.

## Legacy Boundary

The following legacy files may be used for reference only:

- `pages/rules.html`
- `data/chapters.json`
- `data/ash-data.js`
- `data/page-render.js`
- `pages/rules.css`

They should not receive new feature development as part of RuleBook implementation.

## Deferred Scope

The first RuleBook implementation must not import:

- weapon specializations
- martial arts
- divine arts
- non-arcane specializations
- combat mastery
- arcane arts

The first RuleBook implementation must not include:

- Vue official RuleBook migration
- character sheets
- user systems
- campaign systems
- legacy HTML enhancement

## Compatibility

Existing models remain in place:

- `RuleCategory`
- `Rule`
- `GlossaryTerm`

The new RuleBook models are additive. They should support the reading experience while existing Rule APIs continue to support simple rule querying and technical validation.

`Rule` and `RuleEntry` should not be merged in the first implementation.

## Next Step

After this boundary is accepted, the next task is:

```text
Task 005-A: add RuleBook backend models and migration
```
