# Database Promotion and Release Workflow
## Hoverboard Store AI Support Agent — Commerce Support Console

**Version**: 1.0  
**Status**: Active  
**Last Updated**: 2026-07-03  
**Applies To**: All Supabase schema changes and safe seed data promotions  
**Owner**: Backend lead / store owner  

---

> [!IMPORTANT]
> Staging Supabase and Production Supabase are **completely separate projects** with no shared data.
> Schema changes and safe seed SQL move by approved migration files — never by copying a staging database dump.
> Test data, chat logs, and customer records from staging must never reach production under any circumstances.

---

## 1. Architecture Overview

```
GitHub Repository
│
├── staging branch ────────────► Staging Railway Service
│                                       │
│                                Staging Supabase Project
│                                (test data only — disposable)
│
└── main branch ───────────────► Production Railway Service
                                        │
                                 Production Supabase Project
                                 (real customer data — protected)
```

### The Golden Rule

**Code moves by git.** Pull request from `staging` → `main`.  
**Database changes move by approved SQL migration files.** Applied manually to each Supabase project in sequence.  
These two operations are **always separated and sequenced** — never combined into a single automatic step.

---

## 2. What May and May Not Be Promoted

### ✅ Allowed: Safe Promotions

| Type | Examples | How |
|:---|:---|:---|
| Schema migration | `CREATE TABLE`, `ALTER TABLE ADD COLUMN`, `CREATE INDEX` | Numbered `.sql` file in `backend/db/migrations/` |
| Safe reference seed | `stores` table rows (known business entities only) | Numbered `.sql` file in `backend/db/seeds/` |
| Knowledge article seed | `support_articles`, `product_knowledge` rows | Numbered `.sql` file in `backend/db/seeds/` |
| Extension setup | `CREATE EXTENSION IF NOT EXISTS vector` | Schema migration file |

### ❌ Forbidden: Never Promote

| Type | Reason |
|:---|:---|
| `chat_logs` data from staging | Contains test/fake messages — not real customer data |
| `agent_replies` data from staging | Test replies — irrelevant in production |
| `reply_drafts` data from staging | Test drafts — irrelevant in production |
| `conversations` / `messages` from staging | Test sessions only |
| `escalations` from staging | Fake test escalations |
| Full Supabase project backup/restore from staging to production | Would overwrite real customer data |
| `pg_dump` of staging applied to production | Copies all test data — strictly forbidden |
| Any row that contains customer email, session ID, or chat content | PII — must not cross environments |

---

## 3. The Two Promotion Channels

### Channel 1: Schema Migration

A schema migration changes **the structure** of the database — tables, columns, indexes, constraints, triggers, or extensions. It contains no data rows (except reference data that is intrinsic to the schema, such as enum entries).

**File location**: `backend/db/migrations/`  
**File naming**: `NNNN_description.sql` where `NNNN` is a zero-padded sequential number.

Examples:
```
0001_initial_schema.sql
0002_add_chat_logs_status_column.sql
0003_add_product_knowledge_table.sql
0004_add_knowledge_intent_tags_column.sql
```

### Channel 2: Safe Seed Data

A seed file inserts or upserts known, static reference data that must exist in both staging and production for the application to function correctly.

**Allowed seed categories:**
- `stores` table rows (one row per store — `hoverboard_store` etc.)
- `support_articles` rows that are the production knowledge base
- `product_knowledge` rows from approved Product Support Passports

**File location**: `backend/db/seeds/`  
**File naming**: `SSSS_description.sql` where `SSSS` is a zero-padded sequential number.

Examples:
```
0001_stores_reference.sql
0002_hoverboard_store_support_articles_v1.sql
0003_knowledge_pack_6_5_hoverboard_bundle_v2.sql
```

**All seed SQL must be idempotent** — safe to run more than once without duplicating data. Use `ON CONFLICT DO UPDATE` or `ON CONFLICT DO NOTHING`. Never use bare `INSERT` for seed data.

---

## 4. Migration File Format

Every migration SQL file must begin with a header block:

```sql
-- =============================================================================
-- MIGRATION: NNNN_description.sql
-- =============================================================================
-- Purpose:
--   One paragraph describing why this change is needed and what it does.
--
-- Affected Tables:
--   - table_name_1 (ADD COLUMN / CREATE / ALTER / DROP)
--   - table_name_2 (CREATE INDEX)
--
-- Type: ADDITIVE | DESTRUCTIVE | MIXED
--   ADDITIVE   = adds new tables, columns, or indexes without removing anything
--   DESTRUCTIVE = drops, renames, or changes column types (requires explicit approval)
--   MIXED      = a combination of both
--
-- Staging Test:
--   [ ] Applied to staging Supabase on: YYYY-MM-DD
--   [ ] Application tests passed on staging after migration
--   [ ] /api/test-agent results unchanged or improved
--   [ ] Integration test suite passed: ./venv/bin/python test_takeover_flow.py
--
-- Production Execution Checklist:
--   [ ] Supabase production backup taken before running this migration
--   [ ] This migration runs BEFORE the code deploy if code depends on new columns/tables
--   [ ] This migration is SAFE TO RUN AGAIN if restarted (idempotent where possible)
--
-- Rollback Note:
--   Describe how to reverse this change if needed. Reference the corresponding
--   file in backend/db/rollbacks/NNNN_rollback_description.sql if one exists.
--
-- Author: [name]
-- Date: YYYY-MM-DD
-- Approved By: [name/date — required for DESTRUCTIVE migrations]
-- =============================================================================

-- [SQL STATEMENTS BELOW]
```

---

## 5. Seed File Format

Every seed SQL file must begin with a header block:

```sql
-- =============================================================================
-- SEED: SSSS_description.sql
-- =============================================================================
-- Purpose:
--   Describes what reference data this inserts and why it is safe for production.
--
-- Target Tables:
--   - table_name (INSERT ... ON CONFLICT DO UPDATE)
--
-- Safe for Production: YES
-- Contains Customer Data: NO (if yes — this file must NEVER reach production)
-- Idempotent: YES (safe to run multiple times)
--
-- Derived From:
--   - PRODUCT_SUPPORT_PASSPORT_<PRODUCT>_V1.md (for knowledge seeds)
--   - Confirmed by: [store owner name/date] (required for knowledge seeds)
--
-- Staging Test:
--   [ ] Applied to staging Supabase on: YYYY-MM-DD
--   [ ] All relevant /api/test-agent queries produce correct matched answers
--
-- Author: [name]
-- Date: YYYY-MM-DD
-- =============================================================================

-- [SQL STATEMENTS BELOW — all must use ON CONFLICT]
```

---

## 6. Migration and Seed Sequencing Rules

### 6A. Schema Must Precede Seed Data That Depends On It

If a seed file inserts rows into a table that a migration creates, the migration must be applied **before** the seed is run.

```
Apply migration 0003_add_product_knowledge_table.sql
         ↓
Apply seed 0003_knowledge_pack_6_5_hoverboard_bundle_v2.sql
```

### 6B. Migration Must Precede Code That Depends On It

If application code references a new column or table, apply the migration to the Supabase project **before** deploying the code to Railway.

```
Apply migration to production Supabase
         ↓
Deploy code to production Railway (via main branch merge)
```

**Never deploy code first.** If the code starts before the migration runs, it will crash trying to query a column that does not exist.

### 6C. Additive Migrations Are Preferred

| Migration Type | Risk | Approval Required |
|:---|:---|:---|
| `CREATE TABLE IF NOT EXISTS` | Low | Standard PR review |
| `ALTER TABLE ADD COLUMN` (nullable) | Low | Standard PR review |
| `CREATE INDEX IF NOT EXISTS` | Low | Standard PR review |
| `CREATE EXTENSION IF NOT EXISTS` | Low | Standard PR review |
| `ALTER TABLE ADD COLUMN NOT NULL` (with default) | Medium | Standard PR review + staging evidence |
| `ALTER TABLE RENAME COLUMN` | High | Explicit store owner approval |
| `ALTER TABLE DROP COLUMN` | High | Explicit store owner approval |
| `DROP TABLE` | Critical | Explicit store owner approval + rollback plan |
| `ALTER TABLE ALTER COLUMN TYPE` | High | Explicit store owner approval + rollback plan |

> [!CAUTION]
> Destructive migrations — `DROP`, `RENAME`, or `ALTER ... TYPE` — must have a written rollback plan and explicit store owner approval recorded in the migration header before they are applied to any environment.

---

## 7. Step-by-Step Release Checklist

Use this checklist for every release that includes database changes.

```
RELEASE: [short description — e.g. "Phase 3A 6.5 hoverboard knowledge seed"]
DATE: YYYY-MM-DD
Migration files: [list all migration and seed files included]
Railway deploy: staging → main PR: [PR link]
```

---

### Step 1 — Staging Branch Deployed to Staging Railway

```
[ ] Code for this release is merged into the staging branch
[ ] Staging Railway has auto-deployed from staging branch
[ ] Staging Railway health check passes: GET /health → 200 OK
[ ] No startup errors in staging Railway logs
```

---

### Step 2 — Staging SQL Migration Applied

```
[ ] Open Supabase dashboard for STAGING project
[ ] Navigate to: SQL Editor
[ ] Apply each migration file in ascending NNNN order:
    [ ] backend/db/migrations/NNNN_xxx.sql → copy → paste → Run
[ ] Apply each seed file in ascending SSSS order (after migrations):
    [ ] backend/db/seeds/SSSS_xxx.sql → copy → paste → Run
[ ] Confirm no SQL errors returned by Supabase SQL editor
[ ] Confirm affected tables exist with correct columns:
    SELECT column_name, data_type FROM information_schema.columns
    WHERE table_name = 'table_name' ORDER BY ordinal_position;
```

---

### Step 3 — Staging Tests Passed

```
[ ] Run integration test suite on staging:
    cd backend && ./venv/bin/python test_takeover_flow.py
[ ] All tests pass (no failures, no errors)
[ ] Manually test affected queries via /api/test-agent:
    GET https://commerce-support-console-staging-production.up.railway.app/api/test-agent?q=<test_query>
[ ] Review test-agent output: correct route_decision, correct final_answer_preview
[ ] No regression on existing queries confirmed
[ ] Record test results in migration file header:
    [x] Applied to staging Supabase on: YYYY-MM-DD
    [x] Application tests passed
```

---

### Step 4 — Production Backup Taken

```
[ ] Open Supabase dashboard for PRODUCTION project
[ ] Navigate to: Project Settings → Database → Backups
[ ] Confirm a recent automated backup exists (Supabase takes daily backups on paid plans)
[ ] For critical migrations: manually note the current schema state:
    -- Run this in production SQL Editor and save the output:
    SELECT table_name, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'public'
    ORDER BY table_name, ordinal_position;
[ ] Record backup timestamp in the release record
```

> [!WARNING]
> Supabase free tier does not provide on-demand backups. For production databases, use a paid Supabase plan that includes Point-in-Time Recovery (PITR) or daily automated backups. Before any migration, manually export any tables being modified using Supabase Table Editor → Export as CSV.

---

### Step 5 — Production SQL Migration Applied

```
[ ] Open Supabase dashboard for PRODUCTION project
[ ] Navigate to: SQL Editor
[ ] Apply each migration file in ascending NNNN order (same as staging):
    [ ] backend/db/migrations/NNNN_xxx.sql → copy → paste → Run
[ ] Apply each seed file in ascending SSSS order:
    [ ] backend/db/seeds/SSSS_xxx.sql → copy → paste → Run
[ ] Confirm no SQL errors
[ ] Confirm table structure in production matches staging:
    SELECT column_name, data_type FROM information_schema.columns
    WHERE table_name = 'table_name' ORDER BY ordinal_position;
[ ] Do NOT run any staging chat_logs, conversations, or messages data
[ ] Do NOT run any file that does not have "Safe for Production: YES" in its header
```

---

### Step 6 — Merge Staging Branch into Main (Code Deploy to Production)

```
[ ] Open GitHub → New Pull Request: base: main, compare: staging
[ ] PR title format: "release: [description] — YYYY-MM-DD"
[ ] PR description must include:
    - Migration files applied to production in Step 5
    - Staging test results from Step 3
    - Production backup confirmation from Step 4
[ ] At least one reviewer approves the PR
[ ] Merge the PR
[ ] Confirm Production Railway begins deploying from main branch
[ ] Wait for deployment to complete
[ ] Production Railway health check: GET https://[production-url]/health → 200 OK
```

---

### Step 7 — Production Smoke Test

```
[ ] Test critical customer-facing paths:
    [ ] Chat widget sends a message and receives a reply
    [ ] Battery safety query triggers escalation: "my hoverboard smells burning"
    [ ] Low-risk query returns auto-reply: "when will my order arrive"
    [ ] Admin dashboard loads and shows recent chat logs
    [ ] Human takeover reply sends successfully
[ ] Test all affected functionality introduced by this release
[ ] Confirm no 500 errors in production Railway logs
```

---

### Step 8 — Monitor Logs

```
[ ] Watch production Railway logs for 15 minutes after deployment
[ ] Watch Supabase production project logs for query errors
[ ] Confirm no unexpected escalation spikes in admin dashboard
[ ] If any error detected: execute rollback procedure (see Section 9)
[ ] Record release as complete in git commit message or changelog
```

---

## 8. Environment Variable Separation

Each Supabase project requires its own set of environment variables. These must be set separately in Railway for each service.

| Variable | Staging Railway | Production Railway |
|:---|:---|:---|
| `SUPABASE_URL` | Staging project URL | Production project URL |
| `SUPABASE_KEY` | Staging `service_role` key | Production `service_role` key |
| `APP_ENV` | `staging` | `production` |
| `ADMIN_DASHBOARD_TOKEN` | Staging token (different from production) | Production token |
| `MINIMAX_API_KEY` | Same key (shared OK) | Same key |
| `MINIMAX_GROUP_ID` | Same value | Same value |

> [!CAUTION]
> Never share a `SUPABASE_KEY` between staging and production. Each Supabase project has its own unique keys. Using a production key in staging means staging code can read and write production customer data — this is a critical data breach risk.

---

## 9. Rollback Procedure

### 9A. Rollback Before Main Merge (Easy)

If issues are found during steps 3–5 (staging tests or production migration), before merging to main:

1. Do not merge the PR
2. Fix the issue in the staging branch
3. Apply a corrective SQL to the staging Supabase (or, if the staging migration was destructive, restore from the staging project's backup)
4. Re-run steps 1–5 from the beginning
5. Production is not affected — no code was deployed

### 9B. Rollback After Main Merge (Serious)

If a critical bug is found after production deployment:

1. **Revert the code**: `git revert` the merge commit on main → push → Railway redeploys previous code
2. **Rollback the schema** (only if the migration was destructive — additive migrations are safe to leave): Apply the rollback SQL from `backend/db/rollbacks/`
3. Do NOT revert additive migrations (adding a column or table that is no longer referenced by code is harmless)
4. Document the incident in a rollback record with: what broke, when detected, what was reverted, root cause

### 9C. When NOT to Rollback a Migration

- If the migration was additive (new table, new nullable column, new index) — do not revert it. The old code will simply ignore the new column/table. It is safe.
- If the seed was additive (new knowledge articles) — do not revert. Old code ignores unknown knowledge rows.
- Only revert if the migration dropped, renamed, or changed a column that production code is actively querying.

---

## 10. Migration History Tracking

There is no automated migration runner (like Flyway or Alembic) in this project at Phase 3A. Migrations are tracked manually using:

1. The sequential file number `NNNN_` prefix in `backend/db/migrations/`
2. A comments header in each file recording applied dates
3. This document's migration log table below

### Applied Migration Log

> Update this table every time a migration is applied to production.

| # | File | Applied to Staging | Applied to Production | Notes |
|:---|:---|:---|:---|:---|
| baseline | `supabase_schema.sql` | ✅ Pre-existing | ✅ Pre-existing | Original schema — `chat_logs`, `support_articles`, `stores`, etc. |
| — | `knowledge_brain_schema.sql` | ✅ Pre-existing | ✅ Pre-existing | Additional schema additions from early dev |
| — | `knowledge_pack_hoverboard_store_v1.sql` | ✅ Pre-existing seed | ✅ Pre-existing seed | Original knowledge seed v1 |

> All future migrations must be added to this table at the time of production application.

---

## 11. File Directory Structure

```
backend/
├── db/
│   ├── migrations/
│   │   ├── README.md             ← Rules for writing migration files
│   │   └── NNNN_description.sql  ← Numbered migration files
│   ├── seeds/
│   │   ├── README.md             ← Rules for writing seed files
│   │   └── SSSS_description.sql  ← Numbered seed files
│   └── rollbacks/
│       ├── README.md             ← Rules for writing rollback files
│       └── NNNN_rollback_description.sql
├── docs/
│   └── DATABASE_PROMOTION_WORKFLOW.md  ← This file
└── supabase_schema.sql           ← Baseline schema (legacy — see db/migrations/ for changes)
```

---

## 12. Quick Reference Card

```
WHAT MOVES FROM STAGING TO PRODUCTION?
  ✅ Git code (via PR: staging → main)
  ✅ Migration SQL files (run manually in production Supabase SQL Editor)
  ✅ Seed SQL files for knowledge articles (run manually, ON CONFLICT safe)
  ❌ NEVER: chat_logs, conversations, messages, escalations, reply_drafts, agent_replies
  ❌ NEVER: pg_dump of staging database
  ❌ NEVER: customer email addresses, session IDs, or chat content

ORDER OF OPERATIONS:
  1. Test on staging (branch + Supabase)
  2. Run migration SQL on production Supabase
  3. Merge code to main (Railway deploys automatically)
  4. Run smoke test
  5. Monitor logs

IF SOMETHING BREAKS AFTER DEPLOY:
  1. Revert git merge → Railway rolls back code automatically
  2. Only revert DB migration if it was destructive (rare)
  3. Additive migrations (new tables/columns) are safe to leave
```
