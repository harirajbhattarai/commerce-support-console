# Phase Gates — Go / No-Go Acceptance Criteria
## Hoverboard Store AI Support Agent

> [!IMPORTANT]
> No phase may advance to production until ALL acceptance gates listed for that phase are passed.
> Gate failures block deployment. There are no exceptions.

---

## Phase 0 Gate: Environment Safety

| # | Gate | Evidence Required | Status |
| :--- | :--- | :--- | :--- |
| 0.1 | `main` branch deploys only to Production Railway service | Railway deploy settings screenshot | ✅ |
| 0.2 | `staging` branch deploys only to Staging Railway service | Railway deploy settings screenshot | ✅ |
| 0.3 | Staging dashboard shows orange `STAGING` badge | Manual check or screenshot | ✅ |
| 0.4 | Production dashboard shows green `PRODUCTION` badge | Manual check or screenshot | ✅ |
| 0.5 | Staging responses return `X-Robots-Tag: noindex, nofollow` | curl response header check | ✅ |
| 0.6 | Integration test suite passes green on staging before any `main` merge | `./venv/bin/python test_takeover_flow.py` output | ✅ |
| 0.7 | Staging Supabase is isolated or clearly prefixed from production data | Supabase project dashboard | ⚠️ Pending |
| 0.8 | Staging demo widget calls staging backend (not localhost or port 8000) | curl/browser check on staging root page | ✅ |

**Phase 0 Overall**: ⚠️ Substantially complete. Gate 0.7 required for full sign-off.

---

## Phase 1 Gate: Agent v1 Stability

| # | Gate | Evidence Required | Status |
| :--- | :--- | :--- | :--- |
| 1.1 | No `product_recommendation` queries produce `needs_escalation` status | `test_status_routing_assertions` output | ✅ |
| 1.2 | No `delivery_general` queries produce `needs_escalation` status | `test_status_routing_assertions` output | ✅ |
| 1.3 | No `return_policy` or `warranty_policy` queries produce `needs_escalation` status | `test_status_routing_assertions` output | ✅ |
| 1.4 | All `battery_safety` queries return immediate safety guidance | `test_status_routing_assertions` output | ✅ |
| 1.5 | All `speak_to_human` queries produce `needs_escalation` status | `test_status_routing_assertions` output | ✅ |
| 1.6 | All `order_issue` queries ask for verification details before escalating | Integration test | ✅ |
| 1.7 | `/api/test-agent` returns correct `route_decision` for at least 30 sampled queries | Manual API test | ✅ |
| 1.8 | Full integration test suite passes on staging | `./venv/bin/python test_takeover_flow.py` | ✅ |
| 1.9 | Low-risk helpful bot answers saved with `auto_replied` status (not `needs_escalation`) | Test suite + Supabase query | ✅ |

**Phase 1 Overall**: ❌ Reopened (Batch 1 Complete). Phase 1 remains open pending the rest of the routing/retrieval foundation correction outlined in `PHASE1_ROUTING_RETRIEVAL_ROOT_CAUSE_AUDIT.md`. Batch 1 (Deterministic Gates) has been implemented and validated.

> [!WARNING]
> Foundational refactor required to separate intent understanding (LLM structured output) from retrieval. Keyword-guessing approach has failed safety and product entity gates.

> [!NOTE]
> The 204-question evaluation dataset (`customer_question_dataset_v2.json`) exists and covers 24 intents.
> It is used for regression testing only — not for exact customer message matching.
> The dataset test runner (`run_dataset_tests.py`) is the remaining Phase 2 item.

**Must pass before**: Phase 2 dataset test runner work begins.

---

## Phase 2 Gate: Intent Dataset v2

| # | Gate | Evidence Required | Status |
| :--- | :--- | :--- | :--- |
| 2.1 | Dataset contains ≥ 200 unique customer questions | `customer_question_dataset_v2.json` item count | ✅ 204 items |
| 2.2 | All 24 defined intents have ≥ 5 dataset examples each | Dataset intent coverage report | ✅ |
| 2.3 | Dataset test runner (`run_dataset_tests.py`) exists and runs without error | Script execution | ❌ Pending |
| 2.4 | Dataset test runner achieves ≥ 85% pass rate on staging | Test runner output | ❌ Pending |
| 2.5 | Dataset test runner achieves ≥ 90% pass rate before production deploy | Test runner output | ❌ Pending |
| 2.6 | Every chatbot code change is validated against full dataset before staging push | Git PR checklist | ❌ Pending |

**Phase 2 Overall**: ⚠️ Dataset created. Test runner not yet built.

**Must pass before**: Phase 3A passport implementation begins (Phase 3A may proceed in parallel with Phase 2 test runner build since the passport work is documentation, not code).

---

## Phase 3 Gate: Knowledge Brain v2

| # | Gate | Evidence Required | Status |
| :--- | :--- | :--- | :--- |
| 3.1 | ≥ 12 new `support_articles` rows added to Supabase | Database count query | ❌ Pending |
| 3.2 | All common troubleshooting intents (reset, charging, stopped working, not turning on) return a matched article | `/api/test-agent` output for each query | ❌ Pending |
| 3.3 | Zero `"I couldn't find a direct match"` replies for known-topic queries in the Phase 2 dataset | Dataset test runner output | ❌ Pending |
| 3.4 | New knowledge rows are seeded into staging Supabase before production | Staging test confirmation | ❌ Pending |
| 3.5 | Full dataset test runner achieves ≥ 90% pass rate with new knowledge | Test runner output | ❌ Pending |
| 3.6 | Phase 3A Product Support Passport is complete before any knowledge SQL is written | Passport document review | ❌ Pending |

**Phase 3 Overall**: ❌ Not started. Phase 3A passport work must precede SQL seed creation.

**Must pass before**: Phase 4 Shopify integration begins.

---

## Phase 3A Gate: Product Support Passport — Vertical Slice

> [!IMPORTANT]
> Phase 3A is the primary execution path for Phase 3. Completing Phase 3A is required before:
> - Writing the Supabase knowledge SQL seed (`knowledge_pack_6_5_hoverboard_v2.sql`)
> - Starting vector/semantic embeddings
> - Advancing to Phase 3B (8.5" off-road hoverboard)

| # | Gate | Evidence Required | Status |
| :--- | :--- | :--- | :--- |
| 3A.1 | `KNOWLEDGE_CHUNK_SCHEMA_PLAN.md` is written and reviewed | Document review | ❌ Pending |
| 3A.2 | `PRODUCT_SUPPORT_PASSPORT_TEMPLATE.md` is written with all 8 sections (A–H) | Document review | ❌ Pending |
| 3A.3 | `PRODUCT_SUPPORT_PASSPORT_6_5_HOVERBOARD_BUNDLE_V1.md` is completed using the template | Document review | ❌ Pending |
| 3A.4 | All passport sections A–H contain factual, accurate, store-specific content (not placeholders) | Reviewer sign-off | ❌ Pending |
| 3A.5 | Knowledge chunks are derived from the passport and inserted into staging Supabase | Staging database check | ❌ Pending |
| 3A.6 | All 6.5" bundle queries in the Phase 2 dataset return matched answers (not fallback) | `/api/test-agent` output | ❌ Pending |
| 3A.7 | Battery/fire/smoke/overheating queries for this product trigger safety escalation | Integration test | ❌ Pending |
| 3A.8 | At least 20 passport-specific queries reviewed in `/api/test-agent` | Manual check log | ❌ Pending |
| 3A.9 | Full integration test suite passes on staging with new passport knowledge | `test_takeover_flow.py` output | ❌ Pending |
| 3A.10 | No embeddings added until this gate is fully passed | Code audit | ❌ Pending |

**Phase 3A Overall**: ❌ Docs created — implementation not yet started.

**Enables**: Phase 3B (next product family), vector embeddings, and Phase 4 Shopify integration.

---

## Phase 4 Gate: Shopify Read-Only Order Lookup

| # | Gate | Evidence Required |
| :--- | :--- | :--- |
| 4.1 | `shopify_lookup.py` service only calls Shopify read endpoints | Code review — no POST/PUT/DELETE calls |
| 4.2 | Shopify API token has read-only scope — no write scopes granted | Shopify Partner admin confirmation |
| 4.3 | Verification requires order number AND (email OR postcode) | Integration test |
| 4.4 | Failed verification never returns order data | Negative-path integration test |
| 4.5 | Successful verification returns order status, fulfillment, tracking, product | Positive-path integration test |
| 4.6 | Bot never exposes full customer address or payment data | Code audit |
| 4.7 | All order lookup queries pass in staging before production | Staging test confirmation |
| 4.8 | Full dataset test runner achieves ≥ 90% pass rate including order queries | Test runner output |

**Must pass before**: Phase 5 case intake begins.

---

## Phase 5 Gate: Case Intake Workflows

| # | Gate | Evidence Required |
| :--- | :--- | :--- |
| 5.1 | `support_cases` table exists in Supabase with all required fields | Database schema check |
| 5.2 | Bot successfully creates a case for each of the 7 defined case types | Integration test for each type |
| 5.3 | Each created case has a unique human-readable reference number | Case creation test |
| 5.4 | Dashboard shows case list and case detail view | Manual dashboard check |
| 5.5 | Staff can update case status | Manual dashboard test |
| 5.6 | Intake conversation collects all required fields before creating case | Conversation flow test |

---

## Phase 6 Gate: Controlled Actions

| # | Gate | Evidence Required |
| :--- | :--- | :--- |
| 6.1 | Bot cannot issue a refund or replacement without staff approval | Code audit — no auto-approve logic |
| 6.2 | Draft replies are held in dashboard for staff review before sending | Integration test |
| 6.3 | Bot cannot cancel an order | Code audit |
| 6.4 | Bot cannot change a customer address | Code audit |
| 6.5 | All bot-proposed actions are logged with intent, action, and timestamp | Database audit |

---

## Phase 7 Gate: Analytics and Improvement Loop

| # | Gate | Evidence Required |
| :--- | :--- | :--- |
| 7.1 | Auto-resolution rate tracking is live and visible in dashboard | Dashboard screenshot |
| 7.2 | Staff can mark a bot reply as "wrong" or "incomplete" | Dashboard test |
| 7.3 | Marked replies appear in improvement queue | Improvement queue view |
| 7.4 | Auto-resolution rate ≥ 90% over rolling 7-day period | Analytics dashboard |

---

## Phase 8 Gate: Multi-Channel Expansion

| # | Gate | Evidence Required |
| :--- | :--- | :--- |
| 8.1 | Phase 4, 5, and 7 gates are all passed | Gate completion records |
| 8.2 | Auto-resolution rate ≥ 90% on Shopify for ≥ 30 consecutive days | Analytics data |
| 8.3 | Channel-specific policy rules are documented | Per-channel policy document |
| 8.4 | No auto-send to any marketplace channel | Code audit |
