# Staging and Production Rules
## Hoverboard Store AI Support Agent

---

## Hard Rules — No Exceptions

### Production Rules

1. **Production Railway service tracks `main` branch only.**
2. **No direct commits to `main` for chatbot logic, routing, or brain service changes.**
3. **Production `ADMIN_DASHBOARD_TOKEN` must never be shared or committed to version control.**
4. **Production `SUPABASE_SERVICE_ROLE_KEY` must never be logged or exposed in responses.**
5. **Production `APP_ENV` must always be set to `PRODUCTION`.**
6. **Production Supabase tables must never be manually truncated without a full backup.**
7. **No experimental MiniMax prompt changes may be pushed to production without staging sign-off.**

### Staging Rules

1. **Staging Railway service tracks `staging` branch only.**
2. **Staging `APP_ENV` must always be set to `STAGING`.**
3. **Staging dashboard must display the orange `STAGING` badge.**
4. **Staging responses must return `X-Robots-Tag: noindex, nofollow` to block search indexing.**
5. **Staging Supabase should be a separate project or clearly isolated schema.**
6. **Staging `ADMIN_DASHBOARD_TOKEN` must be different from production.**
7. **Staging Shopify widget (if configured) must point only to staging Railway URL.**

---

## Environment Variable Checklist

### Production Railway Service

| Variable | Required | Notes |
| :--- | :--- | :--- |
| `APP_ENV` | ✅ | Must be `PRODUCTION` |
| `PORT` | ✅ | Railway auto-injects |
| `ADMIN_DASHBOARD_TOKEN` | ✅ | Unique secure token — production only |
| `SUPABASE_URL` | ✅ | Production Supabase project |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ | Production Supabase service key |
| `MINIMAX_API_KEY` | ✅ | Live MiniMax API key |
| `MINIMAX_MODEL` | ✅ | `MiniMax-M2.7` or current model |
| `ALLOWED_ORIGINS` | ✅ | `https://hoverboardstore.co.uk,https://www.hoverboardstore.co.uk` |

### Staging Railway Service

| Variable | Required | Notes |
| :--- | :--- | :--- |
| `APP_ENV` | ✅ | Must be `STAGING` |
| `PORT` | ✅ | Railway auto-injects |
| `ADMIN_DASHBOARD_TOKEN` | ✅ | **Different** secure token from production |
| `SUPABASE_URL` | ✅ | Staging Supabase project (separate preferred) |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ | Staging Supabase service key |
| `MINIMAX_API_KEY` | ✅ | Same MiniMax key is acceptable for staging |
| `MINIMAX_MODEL` | ✅ | Same model as production |
| `ALLOWED_ORIGINS` | ✅ | Staging widget URL or `*` for internal QA |

---

## Supabase Data Isolation Strategy

### Recommended (Phase 0 Target): Separate Supabase Project
- Create a dedicated **Staging Supabase project** with a different URL and service key.
- Seed staging project with a clean copy of `knowledge_pack_hoverboard_store_v1.sql`.
- All staging test conversations are isolated from production logs.

### Minimum Acceptable (Current): Table-Level Prefix
If a separate Supabase project is not yet available, all staging test data must use a clearly identifiable `session_id` prefix (e.g. `staging-test-*`) so production analytics and dashboard views can filter them out.

---

## Dashboard Environment Badge

| Environment | Badge Colour | Badge Text |
| :--- | :--- | :--- |
| `PRODUCTION` | Green (`#067d62`) | `PRODUCTION` |
| `STAGING` | Orange (`#ff9900`) | `STAGING` |
| Any other value | Orange | Value of `APP_ENV` variable |

---

## Shopify Widget URL Rules

| Theme | Widget Backend URL |
| :--- | :--- |
| Live published theme | `https://commerce-support-console-production.up.railway.app/api/chat` |
| Duplicate QA theme | `https://commerce-support-staging.up.railway.app/api/chat` |

> [!WARNING]
> Never point the live published Shopify theme to the staging Railway URL.
> The staging bot may have experimental, untested routing logic.

---

## Incident Classification

| Severity | Example | Response |
| :--- | :--- | :--- |
| **P0 — Critical** | Live widget returns 500 for all messages | Immediate hotfix to `main`. Alert via email. |
| **P1 — High** | Battery safety query not escalating | Hotfix to `staging`, verify, merge to `main` within 2 hours |
| **P2 — Medium** | Wrong status label on dashboard | Fix in `feature/*`, merge to `staging`, standard deploy |
| **P3 — Low** | Missing article for minor topic | Scheduled knowledge update, Phase 3 work |
