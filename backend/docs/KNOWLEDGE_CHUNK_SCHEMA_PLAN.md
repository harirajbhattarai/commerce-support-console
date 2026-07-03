# Knowledge Chunk Schema Plan
## Hoverboard Store AI Support Agent — Phase 3A

**Version**: 1.0  
**Status**: Active — Phase 3A  
**Last Updated**: 2026-07-03  
**Depends On**: `PRODUCT_SUPPORT_PASSPORT_TEMPLATE.md`

---

> [!IMPORTANT]
> Do not write a single Supabase knowledge SQL row until the Product Support Passport for that product family is complete, reviewed, and signed off.
> Knowledge chunks must be derived from passport content — not invented or guessed.

---

## What Is a Knowledge Chunk?

A knowledge chunk is a single, atomic, self-contained piece of support information that:

1. Answers **one specific customer question or intent** completely
2. Can be read by the bot and returned verbatim or near-verbatim as the reply
3. Contains **no contradictions**, **no hedging**, and **no placeholder text**
4. Has a clear, unique `title` that the bot uses to identify what was matched
5. Is tagged with the correct `intent`, `product_family`, `knowledge_type`, and `risk_level`

---

## Schema: `support_articles` Table

Used for general support guidance articles (shipping, returns, warranty policy, safety guidance).

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | UUID | Auto-generated primary key |
| `store_id` | TEXT | Must be `hoverboard_store` for all Hoverboard Store content |
| `title` | TEXT | Short, unique identifier string. Used for matched_source logging. e.g. `"6.5 Inch Hoverboard Reset and Calibration Guide"` |
| `content` | TEXT | The full customer-facing answer. Written as complete sentences. No markdown. No bullet shorthand unless the bot renders it. |
| `intent_tags` | TEXT[] | Array of intents this chunk can match. e.g. `["troubleshooting", "reset_calibration"]` |
| `channel` | TEXT | Channel filter. Use `shopify` for Hoverboard Store customer widget. |
| `created_at` | TIMESTAMP | Auto-set |

### Rules for `support_articles` Content

- Write in second person from the store's voice: "Our hoverboards…", "Please contact…"
- Do not write "I" or "we" unless the store naturally speaks that way
- End every troubleshooting chunk with a fallback: "If this does not resolve the issue, contact contact@hoverboardstore.co.uk with your order number and a description of the fault."
- Safety chunks must end with the emergency contact: "contact@hoverboardstore.co.uk"
- Do not include prices, links, or time-sensitive promotional information in knowledge chunks

---

## Schema: `product_knowledge` Table

Used for product-specific knowledge: troubleshooting guides, setup steps, age/weight guidance, compatibility notes.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | UUID | Auto-generated primary key |
| `store_id` | TEXT | Must be `hoverboard_store` |
| `product_family` | TEXT | e.g. `"6.5_inch_hoverboard_bundle"`, `"8.5_inch_off_road"`, `"g1_pro_bundle"` |
| `title` | TEXT | Short unique title. Used for logging. |
| `content` | TEXT | Full customer-facing answer. Plain prose. |
| `knowledge_type` | TEXT | One of: `presale`, `setup`, `troubleshooting`, `reset_guide`, `charging`, `battery_safety`, `return_warranty`, `case_intake`, `compatibility` |
| `risk_level` | TEXT | One of: `low`, `medium`, `high`. High = immediate escalation required. |
| `intent_tags` | TEXT[] | Array of intent strings this chunk matches. |
| `channel` | TEXT | Use `shopify` |
| `created_at` | TIMESTAMP | Auto-set |

### `knowledge_type` Values and When to Use Them

| `knowledge_type` | Use For |
| :--- | :--- |
| `presale` | Age suitability, beginner guidance, product comparisons, gift questions |
| `setup` | Unboxing, first charge, first power on, safety gear, private land rule |
| `troubleshooting` | Not turning on, charger light, beeping, balance issues, LED lights |
| `reset_guide` | Reset/calibration steps (specific to the product) |
| `charging` | Charging instructions, charger light colours, charging port inspection |
| `battery_safety` | Any overheating, smoke, sparks, burning smell, swollen battery, water damage |
| `return_warranty` | 30-day return window, 12-month warranty scope, what is and is not covered |
| `case_intake` | Required fields for opening a support case, what evidence to collect |
| `compatibility` | Hoverkart fitting, accessories, parts, product compatibility notes |

---

## Risk Level Rules

| `risk_level` | Meaning | Bot Action |
| :--- | :--- | :--- |
| `low` | General info, policy, pre-sale | Auto-reply, no escalation |
| `medium` | Fault, troubleshooting, setup issue | Auto-reply with contact email fallback |
| `high` | Battery/fire/safety, water damage | Immediate escalation + safety stop-use message. No auto-reply. |

> [!CAUTION]
> Any chunk with `risk_level = "high"` must trigger the safety escalation path regardless of the rest of the routing logic.
> Never return a `high` risk chunk as a standard auto-reply.

---

## Chunk Writing Rules

### 1. One Intent Per Chunk
Each chunk covers one specific topic. Do not combine "reset guide" and "battery safety" in a single chunk.

### 2. Derive From Passport
Every chunk must trace back to a specific section (A–H) of the Product Support Passport. If the passport does not cover it, do not write the chunk — update the passport first.

### 3. Chunk Length
- Minimum: 2 complete sentences.
- Maximum: 300 words per chunk. If a topic needs more, split into multiple chunks with clear titles.
- Do not write one-line answers. The bot needs enough context to sound authoritative.

### 4. No Contradictions Between Chunks
Before inserting, check that no existing chunk contradicts the new chunk. If they conflict, update the older chunk, do not add a contradicting second chunk.

### 5. Use Factual Store-Specific Details
Include real details from hoverboardstore.co.uk:
- 30-day return window
- 12-month warranty
- contact@hoverboardstore.co.uk
- UK private land usage rule
- UKCA/CE certification
- Free UK delivery, next-day dispatch

Do not invent specifications, weights, dimensions, or speeds unless confirmed from the product passport.

### 6. Title Format
Use descriptive, searchable titles. The title is logged as `matched_source` and seen by staff in the admin dashboard.

**Good titles:**
- `"6.5 Inch Hoverboard — Not Turning On Troubleshooting"`
- `"6.5 Inch Hoverboard + Hoverkart — Age Suitability Guide"`
- `"Hoverboard Battery Safety — Stop Use Immediately"`

**Bad titles:**
- `"Info"`
- `"Hoverboard stuff"`
- `"Q&A 1"`

---

## Embedding Notes

> [!WARNING]
> Do NOT add vector embeddings to `support_articles` or `product_knowledge` until Phase 3A is complete and at least one full Product Support Passport has been converted to clean chunks.
>
> Embedding strategy (Phase 3A+ only):
> - Embed `title + content` concatenated
> - Use cosine similarity threshold ≥ 0.75 for a match
> - Fall back to keyword matching if no embedding match above threshold
> - Never embed placeholder or stub content

---

## SQL Seed Template

```sql
-- KNOWLEDGE CHUNK SEED TEMPLATE
-- Derived from: PRODUCT_SUPPORT_PASSPORT_<PRODUCT>_V1.md
-- Section: <e.g. "D. Troubleshooting">
-- Approved by: [Reviewer name/date]

-- support_articles example
INSERT INTO support_articles (store_id, title, content, intent_tags, channel)
VALUES (
  'hoverboard_store',
  '<Descriptive Title>',
  '<Full customer-facing answer in plain prose. Minimum 2 sentences.>',
  ARRAY['<intent_1>', '<intent_2>'],
  'shopify'
);

-- product_knowledge example
INSERT INTO product_knowledge (store_id, product_family, title, content, knowledge_type, risk_level, intent_tags, channel)
VALUES (
  'hoverboard_store',
  '6.5_inch_hoverboard_bundle',
  '<Descriptive Title>',
  '<Full customer-facing answer in plain prose.>',
  '<knowledge_type>',
  '<low|medium|high>',
  ARRAY['<intent_1>', '<intent_2>'],
  'shopify'
);
```

---

## Chunk Inventory Per Product Family (Phase 3A Target)

For the **6.5" hoverboard + hoverkart bundle**, the minimum required chunks before Phase 3A is gated as complete:

| Section | Chunk | Table | Status |
| :--- | :--- | :--- | :--- |
| B. Pre-sale | Age suitability (kids/beginners) | `product_knowledge` | ❌ |
| B. Pre-sale | 6.5 vs 8.5 inch comparison | `product_knowledge` | ❌ |
| B. Pre-sale | Hoverkart vs hoverboard standalone | `product_knowledge` | ❌ |
| B. Pre-sale | Birthday gift guidance | `product_knowledge` | ❌ |
| C. Setup | First charge instructions | `product_knowledge` | ❌ |
| C. Setup | Power on and first ride | `product_knowledge` | ❌ |
| C. Setup | Safety gear + private land rule | `support_articles` | ❌ |
| D. Troubleshooting | Not turning on | `product_knowledge` | ❌ |
| D. Troubleshooting | Charger light not coming on | `product_knowledge` | ❌ |
| D. Troubleshooting | Beeping/flashing lights | `product_knowledge` | ❌ |
| D. Troubleshooting | Balance and calibration | `product_knowledge` | ❌ |
| D. Troubleshooting | Hoverkart fitting issue | `product_knowledge` | ❌ |
| E. Safety | Battery overheating / burning smell | `product_knowledge` | ❌ |
| E. Safety | Smoke or sparks | `product_knowledge` | ❌ |
| E. Safety | Water damage | `product_knowledge` | ❌ |
| F. Return/Warranty | 30-day return policy | `support_articles` | ⚠️ Exists (generic) |
| F. Return/Warranty | 12-month warranty scope | `support_articles` | ⚠️ Exists (generic) |
| F. Return/Warranty | What warranty covers vs does not cover | `support_articles` | ❌ |
| G. Case Intake | Required fields for support case | `support_articles` | ❌ |

Minimum: **18 chunks** before Phase 3A gate passes.
