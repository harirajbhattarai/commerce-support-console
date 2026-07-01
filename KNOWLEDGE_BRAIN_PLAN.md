# Design Plan: Product & Policy Knowledge Brain Foundation

This document outlines the architecture for the **Product + Policy Knowledge Brain**, which serves as the structured knowledge foundation for future AI/RAG-driven support drafts inside the HCHAHAL Support Console (covering Shopify widgets and the Amazon sandbox channel).

---

## 1. Structured Knowledge Categories

To ensure the draft generation engine relies on authoritative, verified data rather than LLM hallucination, all store and channel data will map to specific policy and guide categories:

*   **Policy Articles**:
    *   `delivery_policy`: Ship times, shipping rates, carrier rules, and exceptions.
    *   `returns_policy`: Return window constraints, label generation, and restocking fees.
    *   `refund_policy`: Money-back rules, timelines, and conditions for deduction.
    *   `warranty_policy`: Coverage bounds (e.g., 12-month manufacturer limitations).
    *   `damaged_item_process`: Carrier claim guidelines, photo submission requirements.
    *   `cancellation_policy`: Unshipped vs Shipped cancellation rules.
    *   `amazon_reply_rules`: Strict compliance constraints (e.g., zero external domains, no direct contact requests).
    *   `shopify_reply_rules`: Shopify-specific response rules.
*   **Product-Specific Guides**:
    *   `product_troubleshooting`: General product maintenance.
    *   `battery_safety`: Specific warnings regarding battery use.
    *   `charging_safety`: Specific warnings regarding plugs, adapters, and chargers.
    *   `hoverboard_reset_guides`: Step-by-step recalibration sequences (Flat surface ➔ 10-second power hold ➔ restart).
    *   `scooter_fault_guides`: Troubleshooting instructions for motor or steering issues.
    *   `essential_oil_safety`: Warnings regarding diffuser usage around pets/children.
    *   `aroma_diffuser_usage`: Water level limits, cleaning guides, and mist adjustments.
    *   `order_status_help`: Dynamic templates linked to transaction milestones.

---

## 2. Product Catalog Schema

We require a structured product table to tie customer issues and purchased orders directly to physical catalog items. Each product record contains:

```
+-------------------------------------------------------------+
|                          products                           |
+-------------------------------------------------------------+
| id (UUID, PK)                                               |
| store_id (VARCHAR NOT NULL REFERENCES stores(id))           |
| channel (VARCHAR NOT NULL) -- 'shopify_widget' / 'amazon'   |
| sku (VARCHAR UNIQUE)                                        |
| asin (VARCHAR UNIQUE) -- Amazon Standard Identification No. |
| product_title (VARCHAR NOT NULL)                            |
| product_type (VARCHAR) -- 'hoverboard', 'diffuser', etc.     |
| brand (VARCHAR)                                             |
| category (VARCHAR)                                          |
| key_specs (JSONB)                                           |
| created_at (TIMESTAMP)                                      |
+-------------------------------------------------------------+
```

---

## 3. Database Table Recommendations

To support both unstructured RAG articles and structured product troubleshooting data, we will reuse and extend the database schema:

### 3.1 Reuse & Extend Existing Tables
*   **`support_articles`**: Represents whole policy documents. We will add a `category VARCHAR(100)` column to classify them (e.g., `returns_policy`, `delivery_policy`).
*   **`article_chunks`**: Houses split sections of policy documents prepared with a 1536-dimensional `embedding` vector for pgvector semantic search.

### 3.2 Create New Tables
*   **`products`** (defined above): Stores specifications, SKUs, and ASIN mappings for Hoverboards, Diffusers, and Gadgets.
*   **`product_knowledge`**: Stores structured product diagnostics, troubleshooting steps, safety warnings, warranty notes, and common faults linked directly to a product record:
    ```sql
    CREATE TABLE IF NOT EXISTS product_knowledge (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
        common_faults TEXT[], -- list of symptoms (e.g., "beeping", "not turning on")
        troubleshooting_steps JSONB, -- map of symptom -> list of steps
        safety_warnings TEXT[],
        warranty_notes TEXT,
        return_notes TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
    );
    ```

---

## 4. Draft Reply Lifecycle Workflow

The draft engine will follow a strict, context-aware sequence to generate safe, policy-compliant responses:

```
[Customer Message] 
       │
       ▼
1. Classify Message  ──► Detects category (e.g., faulty_product) and risk level.
       │
       ▼
2. Context Lookup    ──► Extracts Order ID / SKU / ASIN from thread or sandbox order lookup.
       │
       ▼
3. Knowledge Query   ──► Queries `product_knowledge` (for SKU) and `support_articles` (for policy).
       │
       ▼
4. Template Routing  ──► Merges retrieved context and constructs response.
       │
       ▼
5. Human Review      ──► Injects into composer for manual edit, approval, and copy.
```

---

## 5. Store Knowledge Isolation

Knowledge is strictly isolated at the database query level to prevent cross-store leaks:
*   Every query to `support_articles`, `article_chunks`, and `products` must explicitly check `store_id = current_active_store_id`.
*   Amazon queries default to the `GiftGadgets` store context (`store_id = GiftGadgets`), keeping Shopify widget queries isolated to `hoverboard_store`, `aroma_haven`, or `hcs_gadgets`.

---

## 6. Future RAG & LLM Embedding Path

*   **Embeddings Generation**:
    *   We will run a background script that chunks documents inside `support_articles` and calls the OpenAI `text-embedding-3-small` (1536 dim) or Gemini Embeddings API.
    *   The generated vectors are saved directly to `article_chunks.embedding`.
*   **Semantic Retrieval**:
    *   When a customer query is ingested, the engine generates an embedding of the query and runs a cosine similarity search (`<=>` operator in pgvector) against `article_chunks` filtered by `store_id`.
*   **LLM Synthesis (MiniMax / Gemini)**:
    *   The retrieved text chunks and product troubleshooting steps are passed into the LLM system prompt:
        ```
        System: You are a support bot. Use only the following verified context to draft a reply. Do not invent details.
        Context: [Retrieved chunks & product troubleshooting data]
        Customer Query: [User query text]
        ```
    *   This forces the LLM to output accurate, policy-safe templates.

---

## 7. Strict Safety & Guardrail Rules

*   **No Hallucinations**: Under no circumstances should the engine invent product specifications, ship dates, or policy details.
*   **Handoff Fallback**: If matching product knowledge is missing for a product fault category, the draft engine must populate the composer with a handoff holding response: *"We have received your message regarding a product fault. This has been routed to our technical support team for review..."*
*   **No Safety Drafting**: If safety keywords are matched, the engine must immediately classify as `battery_or_safety_issue`, recommend `escalate`, and display the escalation manager warning banner.
*   **No Financial Guarantees**: Any mentions of refunds, credits, or direct replacements must include placeholders indicating human verification is required (e.g., `[Pending agent review of product photos]`).
*   **Human Review Enforcement**: Live automatic sending remains disabled. All outputs are injected only into the composer textarea for human editing/approval.

---

## 8. Smallest Next Build Step

To begin implementation in the next phase, we recommend executing a database migration to provision the `products` and `product_knowledge` tables, followed by seeding sample products and policies for our core stores (`hoverboard_store`, `aroma_haven`, `hcs_gadgets`).
