# Phase 1: Routing & Retrieval Root Cause Audit

This document details the root causes of the inconsistent behavior observed in the Phase 1 AI Support Agent chatbot, specifically analyzing the disconnect between intent detection, knowledge retrieval, and answer generation.

## 1. Trace of `/api/chat` Execution Path

The exact sequence of execution for an incoming customer message is:

1. **Request Parsing**: Validates `store_id` and `conversation_id`.
2. **Session / Takeover Check**: Queries `chat_logs`. If the session is already `in_progress` or `needs_escalation`, the pipeline aborts and directly returns a "Staff Takeover Active" message.
3. **Supabase Retrieval (`get_support_knowledge`)**: Uses naive keyword matching and hardcoded product mapping to fetch rows from `products`, `product_knowledge`, and `support_articles`.
4. **Match Ranking (`rank_knowledge_matches`)**: Uses a simple term-frequency overlap score to pick the single best article. Awards arbitrary bonus points (+5) if words like "kids" or "9" match articles containing "6.5".
5. **Context Fetch**: Fetches the last 3 messages from `chat_logs`.
6. **Support Brain Routing (`generate_support_reply`)**:
   - **Intent & Safety Detection (`detect_intent_and_risk`)**: Scans the current message against hardcoded substring lists.
7. **Escalation Decision (Hard Gate)**: 
   - If `detect_intent_and_risk` returns `should_escalate = True`, the system completely skips the LLM and returns a hardcoded holding message (`brain_mode: "rules"`).
8. **MiniMax Invocation**:
   - If `should_escalate = False`, it checks for the `MINIMAX_API_KEY`.
   - If the key is missing (or if an exception occurs), it falls back to hardcoded regex-like responses or verbatim outputs the retrieved knowledge (`brain_mode: "fallback"`).
   - If the key is present, it calls MiniMax (`brain_mode: "minimax"`).
9. **Chat Log Save**: Saves to Supabase with the final `escalated` flag and `effective_status`.

## 2. MiniMax Bypass Paths

There are three code paths that completely bypass the MiniMax LLM:

| Bypass Path | Trigger Condition | Brain Mode Produced | MiniMax Called? | Is Retrieval Result the Direct Answer? |
| :--- | :--- | :--- | :--- | :--- |
| **Safety / Human Router** | Exact substring matches a danger/human keyword. | `rules` | No | No (returns hardcoded holding message) |
| **Missing API Key** | `settings.MINIMAX_API_KEY` is missing/empty. | `fallback` | No | Yes (if no hardcoded rules trigger, verbatim knowledge is returned) |
| **API Exception** | MiniMax times out or throws an error. | `fallback` | Attempted | Yes (verbatim knowledge returned) |

## 3. Analysis of `detect_intent_and_risk`

The router relies **entirely on exact substring phrase lists**. It does not use fuzzy matching, lemmatization, semantic understanding, or LLM classification.

*   **Why “smells burning” works**: "burning" is explicitly listed in `safety_danger_keywords`.
*   **Why “smelling” works**: "smelling" is in `smell_words`. If the message also contains "hoverboard" (in `device_words`), it passes the contextual smell check.
*   **Why “my hoverboard is burn” FAILS**: "burn" is missing from `safety_danger_keywords`. It only contains "burning", "melt", "smoke", etc.
*   **Why “i want to talk to a person” works**: That exact phrase is in `human_keywords`.
*   **Why “i want talk to person” FAILS**: Missing the word "to a". The exact phrase is not in the list, so the router misses it.

## 4. Analysis of Knowledge Retrieval (`get_support_knowledge`)

Retrieval is highly fragile and disjointed from intent detection:
*   **Keyword Extraction**: Splits the query by whitespace, drops words `<= 3` chars, and drops a hardcoded list of 21 stop-words.
*   **OR Query Behavior**: Takes the first 3 surviving keywords and executes an `ilike` OR query across `title` and `content`. If *any* word matches, the row is retrieved.
*   **Product Type Hard-Filter**: `product_type` is guessed via hardcoded words. Critically, **"scooter" is hardcoded to map to `product_type = "hoverboard"`**.
*   **Risk Metadata Ignored**: The retrieval system does not respect `risk_level` or `human_review_required`. If it retrieves high-risk knowledge, it does not force escalation.
*   **Why “scooter” retrieves 6.5 inch hoverboard calibration**: "scooter" forces the product filter to "hoverboard". The ranking function sees "9" and "kid" and blindly adds +5 bonus points to the 6.5 inch calibration article, forcing it to the top.
*   **Why “i want talk to person” retrieves legal rules**: "want", "talk", "person" survive the stop-word filter. The OR query searches for "%person%". It hits "Personal Light Electric Vehicle legal usage rules".

## 5. The "Confidence" Value

The current `confidence` value is **highly misleading and entirely uncalibrated**. 
*   If the fallback brain is used and a `matched_title` exists, confidence is hardcoded to **1.0 (100%)**.
*   Because retrieval uses broad `ilike` OR queries, a single matching substring (like "person" in "Personal") will yield a `matched_title`.
*   Therefore, a completely irrelevant match will be displayed as **Confidence: 100%**.

## 6. Disconnect Between Retrieval Risk and Escalation

**Critical Flaw**: If `get_support_knowledge` selects an article with `risk_level = "high"` (e.g., Battery Safety), this does **not** automatically force escalation.
The article's text is passed to the answer generator, but the escalation flag is determined solely by the exact-match substring list in `detect_intent_and_risk`. 
Thus, "my hoverboard is burn" fails the exact-match check, does not escalate, but successfully retrieves the battery safety article. The bot outputs the safety text while the session remains `auto_replied` and `escalated=False`.

## 7. Product / Entity Understanding

The system has **no real product entity resolver**.
For: *“i have 9 year old kid which scooter should i buy”*
*   **Expected**: `product_type = electric_scooter`, `intent = product_recommendation`, `age = 9`.
*   **Actual**: `product_type = "hoverboard"` (hardcoded mistake), `intent = product_recommendation` (substring match), retrieval gets corrupted by `+5` points for "9/kid", fetching irrelevant calibration articles.

## 8. Root-Cause Matrix

| Message | Normalized | Detected Intent | Risk | Product Type | Selected Source | MiniMax | Brain Mode | Escalated? | Root Cause |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **"my hoverboard is burn"** | `my hoverboard is burn` | `unknown` | `low` | `hoverboard` | Battery Safety | No | `fallback` | **False** | "burn" missing from safety substrings. Router disjoint from retrieval. |
| **"i want talk to person"** | `i want talk to person` | `unknown` | `low` | `hoverboard` | Legal Usage Rules | No | `fallback` | **False** | Exact human phrase missing. OR query matches "person" to "Personal". |
| **"i have 9 year old kid which scooter should i buy"**| `i have 9 year old...` | `product_recommendation`| `low` | `hoverboard` | 6.5 Calibration | No | `fallback` | **False** | "scooter" hardcoded to "hoverboard". Ranking adds +5 for "9". |
| **"i need agent to talk"** | `i need agent to talk` | `speak_to_human` | `high` | None | Safety Router | No | `rules` | **True** | Hits exact substring. |
| **"my hoverboard smells burning"** | `my hoverboard smells...`| `battery_safety` | `high` | `hoverboard` | Safety Router | No | `rules` | **True** | Hits exact substring. |
| **"Return policy"** | `return policy` | `return_policy` | `low` | None | Returns Policy | No | `fallback` | **False** | Standard low-risk behavior. |

## 9. Recommended Target Architecture

Do not attempt to patch individual keywords. The architecture must be fundamentally updated to separate understanding from retrieval. We must maintain deterministic safety gates *before* the LLM is invoked. The deterministic gate is designed for high recall on critical hazards even if the LLM API fails. Target: 100% escalation recall on the approved critical-safety evaluation set before Phase 1 can close. This is a measured engineering gate, not an absolute guarantee that every possible future human phrase is covered forever; Phase 1 cannot close unless all approved critical-safety test cases escalate correctly.

**Approved Target Pipeline**:
Customer message &rarr; Message Normalisation &rarr; Deterministic Hard Safety Gate &rarr; Deterministic Explicit Human Handoff Gate &rarr; MiniMax Structured Semantic Understanding &rarr; Product Entity Resolver &rarr; Filtered Retrieval &rarr; Relevance Validation &rarr; MiniMax Answer Generation &rarr; Post-Answer Safety Audit &rarr; Final Status/Case/Escalation Save.

### Architecture Responsibilities:

1. **Deterministic hard safety gate**: Must be narrow and high-recall. Covers critical danger concepts (smoke, fire, sparks, burning/thermal hazard, dangerous overheating, swollen battery, severe battery/charger physical damage). Uses normalisation, word-family/pattern handling, and device context rather than endless exact-phrase FAQs.
2. **Deterministic explicit human handoff gate**: Must guarantee direct human requests are never blocked by LLM or retrieval failure. Covers requests for an agent, human/person, adviser/advisor, representative/support team using pattern matching rather than single exact sentences.
3. **MiniMax structured understanding**: Used *after* hard gates for semantic classification of messy natural language. Outputs structured JSON with: `intent`, `sub_intent`, `product_type`, `product_entity/product_family` (if known), `issue_category`, `risk_level`, `human_request`, `age` (if explicitly provided), `correction_or_clarification`, and a `confidence/reasoning` signal (not exposed to customers).
4. **Product entity resolver**: Removes hardcoded mappings (e.g., "scooter" -> "hoverboard"). Product families must remain distinct (hoverboard, electric_scooter, hoverkart, bundle, charger/accessory, unknown). Prevents cross-product retrieval failures.
5. **Filtered retrieval**: Retrieval must use structured classification metadata (e.g., `store_id`, `product_type/product_family`, `issue_category`, `intent/sub_intent`) as strict filters to prevent mismatched content.
6. **Relevance validation**: The top result is validated to reject conflicts in product type, intent, or issue category. Replaces misleading 100% confidence scores based purely on keyword matches.
7. **MiniMax answer generation**: For safe customer questions, generates the final conversational answer using validated retrieved context. Rules/fallback act only as emergency degradation paths.
8. **Post-answer safety audit**: Validates before saving/sending by enforcing:
   - **Deterministic safety policy checks**: Ensures dangerous repair guidance was not generated. This can remain deterministic.
   - **Forbidden claim/promise checks**: Ensures unapproved actions (e.g., unauthorized refunds) are not promised.
   - **Product/context consistency validation**: Ensures wrong-product claims were avoided.
   - **Grounded-claim/provenance validation**: Claims about orders, delivery, refunds, warranty, stock, product specs or customer-specific facts must be supported by approved retrieved context or connected system data.
     - *Examples*: "This product has a 12-month warranty" is allowed only if supported by approved knowledge. "Your order will arrive tomorrow" must not be stated without verified order/carrier data. "We have refunded you" must not be stated without a completed approved action/result.
   - If an important factual claim is unsupported, the answer must be rejected, rewritten, clarified, or escalated.
   - Do not expose chain-of-thought to the customer. Internal provenance/source references may be stored for audit/debugging.

## 10. Measurable Gates for Grouped Fix

*   **Safety Escalation Recall**: Target 100% escalation recall on the approved critical-safety evaluation set.
*   **Explicit Human Request Recall**: 100% on test set.
*   **Wrong-Product Answer Rate**: 0% (Hoverboard issues do not bleed into Scooter answers).
*   **Irrelevant 100% Confidence**: 0% (confidence must represent actual semantic match, not string overlap).
