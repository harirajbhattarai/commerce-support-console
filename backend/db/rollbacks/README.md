# Database Rollbacks — README
## Hoverboard Store AI Support Agent — Commerce Support Console

**Location**: `backend/db/rollbacks/`  
**Last Updated**: 2026-07-03  
**Related Doc**: `backend/docs/DATABASE_PROMOTION_WORKFLOW.md`

---

## What Is a Rollback File?

A rollback file is a SQL script that **reverses** a specific migration. It is the manual undo operation for a migration that has already been applied to a Supabase project.

Not every migration needs a rollback file. Additive migrations (adding a table, adding a nullable column, adding an index) do not need to be rolled back because the old code simply ignores unknown columns and tables. Rollback files are primarily needed for **destructive migrations**.

---

## When to Write a Rollback File

| Migration Type | Rollback File Required? |
|:---|:---|
| `CREATE TABLE IF NOT EXISTS` | No — old code ignores the new table |
| `ALTER TABLE ADD COLUMN` (nullable) | No — old code ignores the new column |
| `CREATE INDEX IF NOT EXISTS` | No — indexes are transparent to application code |
| `CREATE EXTENSION IF NOT EXISTS` | No — extensions are transparent |
| `ALTER TABLE ADD COLUMN NOT NULL` (with default) | Recommended — reverting may be needed if code breaks |
| `ALTER TABLE DROP COLUMN` | ✅ Yes — must write before applying the migration |
| `DROP TABLE` | ✅ Yes — must write before applying the migration |
| `ALTER TABLE RENAME COLUMN` | ✅ Yes — must write before applying the migration |
| `ALTER TABLE ALTER COLUMN TYPE` | ✅ Yes — must write before applying the migration |
| `TRUNCATE` or `DELETE` of reference data | ✅ Yes — must re-insert the deleted rows |

> [!IMPORTANT]
> For all **DESTRUCTIVE** migrations: the rollback file must be written, reviewed, and committed **before** the forward migration is applied to production. Do not apply a destructive migration without a tested rollback in place.

---

## File Naming Convention

```
NNNN_rollback_description.sql
```

- `NNNN` matches the **same number** as the forward migration it reverses
- Example: if `0005_drop_deprecated_columns.sql` is the migration, the rollback is `0005_rollback_drop_deprecated_columns.sql`

---

## Required Header Block

```sql
-- =============================================================================
-- ROLLBACK: NNNN_rollback_description.sql
-- =============================================================================
-- Reverses Migration: NNNN_description.sql
-- Purpose:
--   [What this rollback does and why it may be needed]
--
-- When to Run:
--   Run this ONLY if the forward migration NNNN caused a production failure
--   and the code has already been reverted via git revert.
--
-- Affected Tables:
--   - table_name (OPERATION reversed: e.g. RE-ADD COLUMN / RE-CREATE TABLE)
--
-- Data Risk:
--   [Note if data may have been lost by the forward migration and cannot be recovered
--    by this rollback alone — e.g. "Data in dropped_column is permanently lost"]
--
-- Pre-Rollback Checklist:
--   [ ] Code has been reverted to the version before the failed migration
--   [ ] Production Railway is deploying the reverted code
--   [ ] Production Supabase backup taken before running this rollback
--
-- Tested On Staging: [ ] YES / [ ] NOT YET
--   Note: Test the rollback on staging BEFORE applying to production.
--
-- Author: [name]
-- Date: YYYY-MM-DD
-- =============================================================================
```

---

## Rollback Decision Guide

### Step 1: Did the migration break production?

- **No** → No rollback needed. Monitor.
- **Yes** → Proceed to Step 2.

### Step 2: Was the migration additive (new table / new nullable column / new index)?

- **Yes** → Roll back the code only (`git revert` on main → Railway redeploys). The new table/column in the database is harmless to the old code — leave it. Do NOT attempt to drop it under time pressure.
- **No** (was destructive) → Proceed to Step 3.

### Step 3: Is a rollback SQL file available for this migration?

- **Yes** → Apply the rollback SQL to production Supabase. Then run the code revert.
- **No** → This is an incident. Escalate immediately. Do not improvise — contact your DBA or Supabase support. Never attempt to recreate a dropped table structure from memory under pressure.

### Step 4: After rollback applied, verify:

```sql
-- Verify table structure restored
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'affected_table'
ORDER BY ordinal_position;

-- Verify data restored (if rollback re-inserted rows)
SELECT COUNT(*) FROM affected_table WHERE [condition];
```

---

## Important Limitations

### Data Lost by `DROP COLUMN` Cannot Be Recovered by Rollback SQL Alone

If a `DROP COLUMN` migration was applied and then a rollback adds the column back, **the data that was in that column is permanently gone**. The rollback SQL can only re-add the column structure — not the data.

This is why:
1. Destructive migrations require explicit approval
2. A production backup must be taken before applying any destructive migration
3. The rollback note for a `DROP COLUMN` migration must say: "Column structure can be restored. Data that was in the column cannot be recovered unless a Supabase point-in-time recovery backup is used."

### Rollback Files Do Not Restore Customer Chat Data

Rollbacks in this directory cover **schema and seed data only**. If `chat_logs` rows are somehow lost or corrupted, they must be recovered from a Supabase automated backup or PITR — not from a rollback file in this directory.

---

## Example Rollback Files

### Example: Rollback for a `DROP COLUMN` Migration

Forward migration `0007_drop_confidence_from_chat_logs.sql`:
```sql
ALTER TABLE chat_logs DROP COLUMN IF EXISTS confidence;
```

Rollback `0007_rollback_drop_confidence_from_chat_logs.sql`:
```sql
-- =============================================================================
-- ROLLBACK: 0007_rollback_drop_confidence_from_chat_logs.sql
-- =============================================================================
-- Reverses Migration: 0007_drop_confidence_from_chat_logs.sql
-- Purpose:
--   Re-adds the `confidence` column to chat_logs.
--   Note: Data that was in the column before the DROP is permanently lost
--   unless a Supabase PITR backup is used.
--
-- When to Run:
--   Only if 0007 caused production errors and code has been reverted.
--
-- Data Risk:
--   PERMANENT DATA LOSS for confidence values. Column can be re-added
--   but will contain NULL for all existing rows.
-- =============================================================================

ALTER TABLE chat_logs ADD COLUMN IF NOT EXISTS confidence DOUBLE PRECISION NOT NULL DEFAULT 0.0;
```

---

### Example: Rollback for an `ALTER TABLE RENAME COLUMN`

Forward migration `0009_rename_matched_source_to_knowledge_source.sql`:
```sql
ALTER TABLE chat_logs RENAME COLUMN matched_source TO knowledge_source;
```

Rollback `0009_rollback_rename_matched_source.sql`:
```sql
-- =============================================================================
-- ROLLBACK: 0009_rollback_rename_matched_source.sql
-- =============================================================================
-- Reverses Migration: 0009_rename_matched_source_to_knowledge_source.sql
-- Purpose:
--   Renames knowledge_source back to matched_source.
--   Data in the column is preserved — only the name changes.
-- =============================================================================

ALTER TABLE chat_logs RENAME COLUMN knowledge_source TO matched_source;
```

---

## Current Rollback Files

| File | Reverses | Status |
|:---|:---|:---|
| *(none yet)* | — | No destructive migrations applied to date |

> Add a row here every time a rollback file is created.

---

## Rollback Files Are Not the Same as Restores

A rollback SQL file reverses a structural change. It does **not** restore:
- Deleted rows of customer data
- Dropped indexes (re-creating them may take time on large tables)
- Lost attachment metadata or file references

For point-in-time data recovery, use the Supabase dashboard:
- **Supabase Pro plan**: Database → Backups → choose a point-in-time restore
- **Supabase Free plan**: Download CSV exports from Table Editor before any destructive operation
