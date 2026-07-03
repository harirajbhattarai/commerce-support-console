# Database Migrations — README
## Hoverboard Store AI Support Agent — Commerce Support Console

**Location**: `backend/db/migrations/`  
**Last Updated**: 2026-07-03  
**Related Doc**: `backend/docs/DATABASE_PROMOTION_WORKFLOW.md`

---

## What Is a Migration?

A migration is a versioned SQL file that changes the **structure** of the database. It may create tables, add or modify columns, create indexes, add constraints, or enable extensions.

Migrations in this directory are the **only permitted way** to change the production Supabase schema.

Direct edits to the Supabase dashboard or unversioned SQL scripts applied to production are **not permitted**.

---

## File Naming Convention

```
NNNN_short_description_of_change.sql
```

- `NNNN` is a zero-padded 4-digit sequential number starting from `0001`
- `short_description_of_change` uses underscores, lowercase, no spaces
- Example: `0003_add_intent_tags_to_product_knowledge.sql`

**Always use the next available number.** Never reuse or skip a number.

---

## Required Header Block

Every migration file must start with this header:

```sql
-- =============================================================================
-- MIGRATION: NNNN_description.sql
-- =============================================================================
-- Purpose:
--   [Why this change is needed and what it does]
--
-- Affected Tables:
--   - table_name (OPERATION: e.g. ADD COLUMN / CREATE TABLE / CREATE INDEX)
--
-- Type: ADDITIVE | DESTRUCTIVE | MIXED
--
-- Staging Test:
--   [ ] Applied to staging Supabase on: YYYY-MM-DD
--   [ ] Application tests passed after migration
--   [ ] /api/test-agent results correct
--   [ ] Integration test suite passed
--
-- Production Execution Checklist:
--   [ ] Production backup confirmed before running
--   [ ] This migration runs BEFORE code deploy (if code depends on new schema)
--   [ ] Verified safe to re-run (idempotent)
--
-- Rollback Note:
--   [How to reverse this. Reference rollback file if one exists.]
--
-- Author: [name]
-- Date: YYYY-MM-DD
-- Approved By: [name/date — required for DESTRUCTIVE type]
-- =============================================================================
```

---

## Migration Types

| Type | Examples | Risk | Approval |
|:---|:---|:---|:---|
| **ADDITIVE** | `CREATE TABLE IF NOT EXISTS`, `ALTER TABLE ADD COLUMN` (nullable), `CREATE INDEX IF NOT EXISTS` | Low | Standard PR review |
| **DESTRUCTIVE** | `DROP TABLE`, `DROP COLUMN`, `RENAME COLUMN`, `ALTER COLUMN TYPE` | High | Explicit store owner sign-off |
| **MIXED** | Adds one column, drops a deprecated one in the same file | Medium | Standard PR + note on destructive part |

---

## Idempotency Rules

Write migrations to be **safe to run twice** wherever possible:

```sql
-- ✅ Good — idempotent
CREATE TABLE IF NOT EXISTS my_table (...);
CREATE INDEX IF NOT EXISTS idx_my_table_store ON my_table(store_id);
ALTER TABLE my_table ADD COLUMN IF NOT EXISTS new_col TEXT;

-- ❌ Risky — will error on second run
CREATE TABLE my_table (...);
ALTER TABLE my_table ADD COLUMN new_col TEXT;
```

For operations that cannot be made idempotent (e.g. `DROP COLUMN`), add a comment:
```sql
-- NOTE: This is NOT idempotent. Do not run more than once.
-- Confirm column exists before running: SELECT column_name FROM information_schema.columns WHERE table_name = '...'
```

---

## How to Apply a Migration

### To Staging

1. Open [Supabase Staging Dashboard](https://supabase.com) → SQL Editor
2. Paste the full contents of the migration file
3. Click **Run**
4. Confirm no errors
5. Verify the change: `SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'affected_table';`
6. Update the migration file header with the staging test date and result

### To Production

1. Complete all staging tests first
2. Take a production backup (see `DATABASE_PROMOTION_WORKFLOW.md` → Step 4)
3. Open [Supabase Production Dashboard](https://supabase.com) → SQL Editor
4. Paste the full contents of the migration file
5. Click **Run**
6. Verify the change
7. Update the Applied Migration Log in `DATABASE_PROMOTION_WORKFLOW.md`
8. Then proceed to merge the code PR (staging → main)

---

## Applied Migration Registry

> Keep this table up to date. Add a row every time a migration is applied to production.

| File | Purpose | Applied Staging | Applied Production |
|:---|:---|:---|:---|
| *(baseline)* `supabase_schema.sql` | Initial schema — chat_logs, articles, stores | ✅ Pre-existing | ✅ Pre-existing |
| *(baseline)* `knowledge_brain_schema.sql` | Extended schema additions | ✅ Pre-existing | ✅ Pre-existing |

> New migrations go here as rows are added.

---

## What Does NOT Belong in This Directory

- Seed data SQL (knowledge articles, store rows) → use `backend/db/seeds/`
- Rollback SQL → use `backend/db/rollbacks/`
- One-off debug or test SQL → do not commit these at all
- Any SQL containing customer data, session IDs, or chat content
