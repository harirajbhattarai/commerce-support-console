# AI Support Agent — 90% Problem Solver Master Plan
## Hoverboard Store UK | Commerce Support Console

**Version**: 1.0  
**Status**: LOCKED ROADMAP  
**Last Updated**: 2026-07-02  
**Contact**: contact@hoverboardstore.co.uk  

---

> [!IMPORTANT]
> This document is the single source of truth for the support automation roadmap.
> No chatbot change, prompt modification, database schema change, or Railway deployment may
> proceed unless it maps to a phase and task in this plan.
> All new customer queries that expose gaps must be added to the intent dataset before a fix is deployed.

---

## Mission Statement

Resolve **90% of inbound Hoverboard Store customer support messages automatically**, safely, and accurately — without human intervention — while routing the remaining 10% to human agents with full context, conversation history, and a structured case intake.

This is not a chatbot. This is a support automation system.

---

## Out of Plan Warnings

These actions are **explicitly prohibited** until the relevant phase is complete and gated:

| ❌ Forbidden Action | Reason |
| :--- | :--- |
| Build Amazon/eBay/TikTok integrations before Shopify read-only is stable | Multi-channel routing logic is undefined. Phase 4 must complete first. |
| Push risky changes to `main` without staging test | Could break live customer widget on hoverboardstore.co.uk |
| Add MiniMax prompt fixes without dataset tests | Regressions are invisible without test coverage |
| Build auto-refund or auto-replacement before human approval system | Financial risk. Phase 6 human approval gates must be in place first. |
| Add vector embeddings before clean knowledge and product data | Garbage in, garbage out. Phase 3 must complete first. |
| Change widget design while backend support logic is weak | UX improvements are meaningless if replies are wrong |
| Solve one random customer question without adding it to the dataset | Creates invisible technical debt |

---

## Current Status

| Layer | Status |
| :--- | :--- |
| FastAPI backend on Railway | ✅ Live |
| `main` branch → Production Railway | ✅ Configured |
| `staging` branch → Staging Railway | ✅ Configured |
| Shopify chat widget | ✅ Live |
| Admin dashboard | ✅ Live |
| Human takeover + staff reply | ✅ Live |
| Supabase chat logs + knowledge tables | ✅ Live |
| MiniMax AI connected | ✅ Live |
| `support_articles` + `product_knowledge` retrieval | ✅ Live |
| `/api/test-agent` debug endpoint | ✅ Live |
| STAGING dashboard badge | ✅ Live |
| Battery safety escalation (immediate guidance) | ✅ Live |
| Staging environment isolation | ⚠️ Partial — may share Supabase project |
| Accurate status routing (low/medium risk) | ⚠️ Known issue — Phase 1 |
| 200-question intent dataset | ❌ Not started — Phase 2 |
| Shopify read-only order lookup | ❌ Not started — Phase 4 |
| Support case intake system | ❌ Not started — Phase 5 |
| 90% resolution analytics | ❌ Not started — Phase 7 |

---

## Phase Overview

| Phase | Name | Target | Current |
| :--- | :--- | :--- | :--- |
| **Phase 0** | Environment Safety | Isolated staging, release controls | ⚠️ In Progress |
| **Phase 1** | Agent v1 Stability | Accurate routing, no wrong escalations | ⚠️ In Progress |
| **Phase 2** | Intent Dataset v2 | 200-question dataset, all intents covered | ❌ Not Started |
| **Phase 3** | Knowledge Brain v2 | Expanded articles + troubleshooting | ❌ Not Started |
| **Phase 4** | Shopify Read-Only | Order lookup for verification | ❌ Not Started |
| **Phase 5** | Case Intake | Structured case creation | ❌ Not Started |
| **Phase 6** | Controlled Actions | Draft reply, tag, case recommendation | ❌ Not Started |
| **Phase 7** | Analytics Loop | Resolution rate tracking, improvement tasks | ❌ Not Started |
| **Phase 8** | Multi-Channel | Amazon, eBay, TikTok, Email | ❌ Not Started |

---

## Phase 0: Environment Safety and Release Control

**Objective**: Ensure every change is tested in staging before it reaches production.

### Rules
- `main` branch → Production Railway → live hoverboardstore.co.uk widget
- `staging` branch → Staging Railway → internal QA use only
- No direct commits to `main` for chatbot logic or brain service changes
- All feature branches merge into `staging` first
- Production deploys only via pull request from `staging` → `main`

### Files/Modules
- `backend/app/config.py` (APP_ENV)
- `backend/app/main.py` (robots middleware)
- `backend/frontend/admin-dashboard.html` (env badge)
- `backend/docs/DEPLOYMENT_WORKFLOW.md`
- `backend/docs/STAGING_PRODUCTION_RULES.md`
- `backend/docs/STAGING_SETUP.md`

### Database Changes
- Staging Supabase: Separate project **strongly recommended**. At minimum, a dedicated staging schema or prefix for all tables to prevent contamination of production chat logs and knowledge base.

### Acceptance Gate
- STAGING dashboard shows orange `STAGING` badge ✅
- PRODUCTION dashboard shows green `PRODUCTION` badge ✅
- Staging responses return `X-Robots-Tag: noindex, nofollow` ✅
- Integration test suite passes on staging before any `main` merge

---

## Phase 1: AI Support Agent v1 Stability

**Objective**: Fix status routing so low/medium-risk helpful answers are not incorrectly escalated.

### Problem
Low-risk product questions (e.g. "which hoverboard is best for a 9 year old") may get routed to `needs_escalation` status instead of being auto-replied successfully.

### Rules
- Only `battery_safety` (high-risk) and verified `order_issue` (requiring Shopify data) escalate
- `speak_to_human` intent escalates with holding message
- All other intents must produce an auto-reply with `auto_replied` status
- The support email `contact@hoverboardstore.co.uk` must be used — no other contact method

### Files/Modules
- `backend/app/services/support_brain.py`
- `backend/app/main.py` (intent routing logic)
- `backend/test_takeover_flow.py`

### API Endpoints
- `POST /api/chat` — must return correct status
- `GET /api/test-agent?q=` — verify routing per query

### Acceptance Gate
- All 200 dataset questions in Phase 2 pass routing and response assertions
- No `product_recommendation`, `delivery_general`, `return_policy`, or `warranty_policy` queries are marked `needs_escalation`
- Battery and fire queries immediately return safety guidance

---

## Phase 2: Intent Matrix and 200-Question Dataset

**Objective**: Define all expected intents and create a repeatable regression test dataset.

### Rules
- Every new chatbot change must be validated against the full dataset before staging deploy
- Every new customer query that exposes a gap must be added to the dataset
- Dataset items define `must_include` and `must_not_include` assertions

### Files/Modules
- `backend/tests/customer_question_dataset_v2.json`
- `backend/docs/INTENT_TO_ACTION_MATRIX.md`
- New test runner: `backend/tests/run_dataset_tests.py`

### Acceptance Gate
- ≥ 200 questions covering all defined intents
- Dataset test runner achieves ≥ 90% pass rate before any phase advance

---

## Phase 3: Knowledge and Product Brain v2

**Objective**: Expand the Supabase knowledge base to cover all common support scenarios.

### Articles to Add
- Reset/calibration steps per model
- Charging port inspection guide
- Wheel/motor fault identification
- Return packaging guidance
- Warranty fault documentation steps
- Missing part report guide
- Damaged-on-arrival report guide
- Wrong item received guide
- Hoverboard + hoverkart compatibility guide
- Off-road 8.5-inch guide
- Weight/age limits per model

### Database Changes
- New rows in `support_articles` and `product_knowledge`
- No schema changes — extends existing tables

### Acceptance Gate
- All Phase 2 dataset questions relating to known topics produce a matched knowledge article
- Zero "I couldn't find a direct match" replies for known-topic queries

> [!WARNING]
> Do NOT implement vector/semantic embeddings until Phase 3 is complete and the knowledge data is clean and accurate. Embedding noisy or incomplete data makes retrieval worse, not better.

---

## Phase 4: Shopify Read-Only Order Lookup

**Objective**: Allow the bot to retrieve order information for customer verification and status checks.

### Allowed Shopify Data
- Order status
- Fulfilment status
- Tracking number and carrier
- Product purchased + quantity
- Order date
- Shipping method
- Customer email

### Forbidden Shopify Actions (Phase 4)
- No refunds
- No cancellations
- No address changes
- No order edits
- No write operations of any kind

### Verification Flow
1. Customer provides order number + email or postcode
2. Bot queries Shopify read-only API to verify the match
3. If verified: bot provides order status and tracking info
4. If not verified: bot asks customer to check their email confirmation and offers to escalate to human

### Files/Modules
- `backend/app/services/shopify_lookup.py` (new)
- `backend/app/main.py` (new `/api/shopify/order-status` route)
- `backend/app/config.py` (SHOPIFY_ACCESS_TOKEN, SHOPIFY_STORE_DOMAIN)

### API Endpoints
- `POST /api/shopify/order-status` — takes order_number + email/postcode, returns status

### Acceptance Gate
- Read-only test against Shopify sandbox confirms correct data retrieval
- No write operations possible from bot service
- Wrong verification attempts do not return order data

---

## Phase 5: Case Intake Workflows

**Objective**: Create a structured case system for escalated support issues.

### Case Types
- Return Request
- Warranty Fault
- Damaged on Arrival
- Missing Part
- Wrong Item Received
- Charging Issue Report
- Stopped Working Report

### Database Changes
- New `support_cases` table in Supabase
- Fields: `case_id`, `session_id`, `store_id`, `case_type`, `order_number`, `description`, `evidence_links`, `status`, `created_at`, `resolved_at`, `assigned_to`

### Files/Modules
- `backend/app/services/case_intake.py` (new)
- `backend/app/main.py` (new case API routes)
- `backend/frontend/admin-dashboard.html` (case view panel)

### Acceptance Gate
- Bot successfully creates a structured case for each defined case type
- Dashboard shows case reference number and case details
- Staff can update case status and add notes

---

## Phase 6: Controlled Actions

**Objective**: Allow the bot to perform safe, limited, reversible actions with human oversight.

### Allowed Bot Actions (Phase 6)
- Create a return case
- Create a warranty fault case
- Tag conversation
- Generate draft reply for staff review
- Flag conversation for manager review

### Forbidden Bot Actions (Phase 6)
- No automatic refunds
- No automatic replacements
- No order cancellations
- No address changes
- No direct customer-facing financial decisions

### Human Approval Required
- All draft replies for case-related responses must be reviewed by a staff member before sending
- Refund/replacement recommendations surfaced to dashboard only — not sent automatically

---

## Phase 7: Analytics and Improvement Loop

**Objective**: Measure auto-resolution rate and create a continuous improvement feedback loop.

### Metrics to Track
- `auto_replied` count per day
- `needs_escalation` count per day
- `resolved_by_bot` count (customer confirmed resolved)
- `resolved_by_human` count
- `failed_answer` count (customer re-asked or asked for human)
- `wrong_route` count (staff overrode bot route)
- `missing_knowledge` count (no match found)
- Top 10 intents per week

### Improvement Loop
1. Staff marks an answer as "wrong" or "incomplete" in dashboard
2. Query + wrong route is automatically added to the improvement queue
3. Improvement queue is reviewed weekly and new dataset entries are created
4. Dataset test runner is run before any deploy

### Acceptance Gate
- 90% auto-resolution rate across a rolling 7-day period
- Failed chats reviewed and added to dataset within 48 hours

---

## Phase 8: Multi-Channel Expansion

**Objective**: Extend the support system to Amazon, eBay, TikTok Shop, OnBuy, B&Q, The Range, and Email.

> [!CAUTION]
> Phase 8 must NOT begin until:
> - Phase 4 (Shopify read-only) is fully stable and tested
> - Phase 5 (Case intake) is fully operational
> - Phase 7 (Analytics loop) is generating accurate data
> - Auto-resolution rate is ≥ 90% on Shopify channel for 30 consecutive days

### Channel-Specific Rules
- Amazon: Subject to Amazon Seller Central messaging policy — no off-platform redirects
- eBay: Subject to eBay messaging policy — no external links in messages
- Marketplace channels: No auto-send without explicit staff approval on a per-message basis
- Email: Triage and draft only — no auto-send

---

## File Index

| File | Purpose |
| :--- | :--- |
| `AI_SUPPORT_AGENT_90_PERCENT_MASTER_PLAN.md` | This document — full roadmap |
| `PHASE_GATES.md` | Per-phase go/no-go acceptance gate definitions |
| `INTENT_TO_ACTION_MATRIX.md` | Every intent, route, and action mapping |
| `CHANGE_CONTROL_AND_RELEASE_WORKFLOW.md` | Branch rules, PR process, deploy checklist |
| `STAGING_PRODUCTION_RULES.md` | Hard rules for what may and may not go to production |
| `SHOPIFY_READ_ONLY_INTEGRATION_PLAN.md` | Shopify API scope, verification flow, forbidden actions |
| `CASE_INTAKE_WORKFLOWS.md` | Case types, fields, intake conversation flows |
| `HUMAN_APPROVAL_RULES.md` | What requires human sign-off before any action |
| `ANALYTICS_AND_IMPROVEMENT_LOOP.md` | Metrics, improvement queue, dataset update process |
| `backend/tests/customer_question_dataset_v2.json` | 200+ regression test questions |
