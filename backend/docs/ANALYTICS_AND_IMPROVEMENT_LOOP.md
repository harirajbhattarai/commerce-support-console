# Analytics and Improvement Loop
## Phase 7 — Hoverboard Store AI Support Agent

---

## Objective

Track resolution rates, identify failure patterns, and continuously improve the bot's accuracy through a structured feedback loop — targeting and maintaining a **90% automatic resolution rate**.

---

## Core Metrics

### Resolution Outcome Tracking (per conversation)

| Metric | Definition | Captured By |
| :--- | :--- | :--- |
| `auto_replied` | Bot replied and customer did not re-ask or escalate | Status at conversation close |
| `resolved_by_bot` | Customer explicitly confirmed issue resolved by bot | Customer confirmation or no re-open within 24h |
| `needs_agent` | Conversation required human takeover | `needs_escalation` status |
| `resolved_by_human` | Human replied and conversation was marked resolved | Staff marks resolved |
| `failed_answer` | Bot produced a reply but customer followed up with same question | Same-session re-query detected |
| `wrong_route` | Staff manually overrode bot's route decision | Staff override logged |
| `missing_knowledge` | Bot returned "I couldn't find a match" or generic fallback | `source_used == fallback` detected |

### Aggregate Dashboard Metrics (daily / weekly)

- Total conversations
- Auto-resolution rate (%) = `auto_replied` + `resolved_by_bot` / total conversations
- Human escalation rate (%)
- Average conversations per day
- Top 10 intents of the week
- Top 5 missed intents (no match or wrong route)
- Average first response time for human escalations

---

## Supabase Table: `conversation_analytics`

```sql
CREATE TABLE conversation_analytics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id TEXT NOT NULL,
  store_id TEXT,
  detected_intent TEXT,
  route_decision TEXT,
  outcome TEXT,            -- auto_replied / needs_agent / resolved_by_bot / resolved_by_human / failed_answer
  brain_mode TEXT,         -- minimax / rules / fallback
  source_used TEXT,
  staff_overrode BOOLEAN DEFAULT FALSE,
  staff_quality_rating TEXT,  -- good / wrong / incomplete (set by staff)
  improvement_flagged BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Staff Quality Rating Flow

After a conversation closes, staff can rate the bot's last auto-reply:

| Rating | Meaning | Action |
| :--- | :--- | :--- |
| `good` | Bot reply was correct and helpful | No action needed |
| `wrong` | Bot gave incorrect information | Auto-add to improvement queue |
| `incomplete` | Bot gave partial information | Auto-add to improvement queue |

Dashboard control: Small thumbs-up / thumbs-down / partial button visible in each conversation detail.

---

## Improvement Queue

When a conversation is flagged as `wrong` or `incomplete`, it is automatically added to an improvement queue:

**Supabase Table: `improvement_queue`**

```sql
CREATE TABLE improvement_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id TEXT NOT NULL,
  customer_query TEXT NOT NULL,
  bot_reply TEXT,
  detected_intent TEXT,
  route_decision TEXT,
  staff_rating TEXT,         -- wrong / incomplete
  staff_note TEXT,           -- Optional explanation from staff
  resolution_action TEXT,    -- add_knowledge / fix_routing / add_to_dataset / other
  resolved BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Weekly Improvement Review Process

**Every Monday, the following steps must be performed:**

1. **Export improvement queue** for the past 7 days:
   ```sql
   SELECT * FROM improvement_queue
   WHERE resolved = FALSE
   ORDER BY created_at ASC;
   ```

2. **For each flagged conversation**, classify the failure:
   - **Missing knowledge** → Add new `support_articles` row
   - **Wrong routing** → Update routing rules in `support_brain.py`
   - **Prompt drift** → Review MiniMax system prompt
   - **New intent found** → Add to `INTENT_TO_ACTION_MATRIX.md` and dataset

3. **Add the customer query to the dataset**:
   - Add entry to `customer_question_dataset_v2.json`
   - Include correct `expected_intent`, `expected_route`, `must_include`, `must_not_include`

4. **Run dataset test runner** to validate fixes:
   ```bash
   ./venv/bin/python tests/run_dataset_tests.py
   ```

5. **Deploy fix to staging**, verify, then deploy to production.

6. **Mark improvement queue items as resolved**.

---

## 90% Resolution Rate Calculation

```
Auto-Resolution Rate = (auto_replied + resolved_by_bot) / total_conversations * 100
```

Measured over a rolling **7-day window**.

### Target Milestones

| Phase | Target Rate |
| :--- | :--- |
| Phase 1 (v1 Stability) | ≥ 60% |
| Phase 2 (Dataset coverage) | ≥ 70% |
| Phase 3 (Knowledge Brain v2) | ≥ 80% |
| Phase 4 (Shopify lookup) | ≥ 85% |
| Phase 5 + 6 (Case intake + actions) | ≥ 90% |
| Phase 8 trigger condition | ≥ 90% sustained for 30 days |

---

## Dashboard Analytics View (Phase 7)

New "Analytics" tab in admin dashboard showing:

- Auto-resolution rate gauge (large, prominent)
- Conversation volume chart (daily, last 30 days)
- Intent breakdown bar chart (top 10)
- Failed answer list (most recent `missing_knowledge` and `wrong_route` entries)
- Improvement queue item count with link to queue view
- Top 5 improvement items pending resolution
