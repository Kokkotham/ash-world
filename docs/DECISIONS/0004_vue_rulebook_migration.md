# Decision 0004: Vue RuleBook Migration

Date: 2026-07-07

## Decision

The Vue RuleBook is not a new parallel feature. It is the official migration of the existing rulebook system.

The future single official rule entry is:

```text
frontend RuleBook
```

The legacy system:

```text
pages/rules.html
data/page-render.js
data/*.json
```

is now legacy reference material only.

## Reason

The existing rule page already has a mature information architecture:

```text
chapters
  -> sections
  -> detailed rule entries
```

The product experience is a rulebook reader, not a database list.

Therefore, the Vue migration should preserve:

- information structure
- reading flow
- rule rendering capability

It should not directly copy the old DOM implementation.

## Data Flow

The future rulebook data flow is:

```text
data_sources
  -> Importer
  -> Django RuleBook API
  -> Vue RuleBook
```

## Prohibited

1. Do not maintain a second rule page.
2. Do not continue enhancing `pages/rules.html`.
3. Do not hard-code rule content in Vue.
4. Do not read legacy `data/` files as the official source.

## Current Stage

Beta:

- Task 004: RuleBook design
- Task 005: Vue RuleBook implementation
