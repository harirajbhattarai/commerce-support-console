-- =============================================================================
-- STAGING SCHEMA BASELINE
-- backend/db/staging_schema_baseline.sql
-- =============================================================================
--
-- PURPOSE:
--   Initialises a brand-new Staging Supabase project with the complete table
--   structure required by the Commerce Support Console backend.
--
-- SAFE FOR: STAGING ONLY
-- SAFE FOR PRODUCTION: NO — use numbered migration files in backend/db/migrations/
--
-- RUN ORDER:
--   STEP 1: Run this file first (staging_schema_baseline.sql)
--   STEP 2: Then run staging_seed_base.sql
--
-- HOW TO RUN:
--   Supabase Dashboard → SQL Editor → paste this file → Run
--   Verify: Table Editor should show all tables listed in the Table Inventory below.
--
-- TABLE INVENTORY (14 tables + extensions + indexes + triggers):
--   1.  stores               — store registry (hoverboard_store, hcs_gadgets, etc.)
--   2.  support_articles     — knowledge base articles (keyword-matched support content)
--   3.  article_chunks       — future vector embedding chunks (pgvector, Phase 3A+)
--   4.  products             — product catalog (SKU, ASIN, product_type, specs)
--   5.  product_knowledge    — product-specific support knowledge entries
--   6.  chat_logs            — all customer chat messages and bot replies
--   7.  agent_replies        — human agent replies sent from admin dashboard
--   8.  staff_notes          — internal staff notes on a session
--   9.  reply_drafts         — draft replies composed in admin dashboard
--   10. conversations        — legacy conversation grouping (cascade delete support)
--   11. messages             — legacy message rows (cascade delete support)
--   12. escalations          — legacy escalation records (cascade delete support)
--
-- LAST UPDATED: 2026-07-03
-- =============================================================================


-- =============================================================================
-- EXTENSIONS
-- =============================================================================

-- pgvector: enables vector similarity search for future RAG / semantic embeddings
-- Required for article_chunks.embedding column (Phase 3A+)
CREATE EXTENSION IF NOT EXISTS vector;


-- =============================================================================
-- 1. STORES TABLE
-- =============================================================================
-- Registry of all stores connected to this Commerce Support Console.
-- The `channel` column is queried by main.py to determine if a store is
-- primarily shopify or amazon. It is NOT in the original supabase_schema.sql
-- but IS referenced in main.py line 1115 — added here to prevent query errors.

CREATE TABLE IF NOT EXISTS stores (
    id          VARCHAR(100) PRIMARY KEY,       -- e.g. 'hoverboard_store', 'hcs_gadgets'
    name        VARCHAR(255) NOT NULL,
    domain      VARCHAR(255),
    channel     TEXT         DEFAULT 'shopify', -- 'shopify' | 'amazon' | 'ebay' | 'all'
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);


-- =============================================================================
-- 2. SUPPORT ARTICLES TABLE
-- =============================================================================
-- General knowledge base articles for keyword-matched support replies.
-- Searched by KnowledgeService.get_support_knowledge() against title and content.
-- The `intent_tags` and `channel` columns are referenced in knowledge seeds
-- (KNOWLEDGE_CHUNK_SCHEMA_PLAN.md) — added here even though the original
-- supabase_schema.sql did not include them, to match the Phase 3A seed format.

CREATE TABLE IF NOT EXISTS support_articles (
    id          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id    VARCHAR(100) NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    title       VARCHAR(500) NOT NULL,
    content     TEXT         NOT NULL,
    intent_tags TEXT[]       DEFAULT '{}'::TEXT[],  -- e.g. ARRAY['troubleshooting', 'reset_guide']
    channel     TEXT         DEFAULT 'shopify',     -- 'shopify' | 'amazon' | 'all'
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);


-- =============================================================================
-- 3. ARTICLE CHUNKS TABLE (Phase 3A+ — vector embeddings)
-- =============================================================================
-- Sub-document chunks of support_articles, prepared for pgvector similarity search.
-- Not used in Phase 1 or Phase 3A document work. Schema created now so the
-- pgvector extension install does not conflict later.

CREATE TABLE IF NOT EXISTS article_chunks (
    id          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id  UUID         NOT NULL REFERENCES support_articles(id) ON DELETE CASCADE,
    store_id    VARCHAR(100) NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    content     TEXT         NOT NULL,
    embedding   vector(1536),    -- 1536 dimensions: text-embedding-3-small / Gemini embeddings
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);


-- =============================================================================
-- 4. PRODUCTS TABLE
-- =============================================================================
-- Product catalog. Queried by KnowledgeService.get_product_by_sku() and
-- get_product_by_asin(). Also searched by product_type and product_title keywords.
-- Source: knowledge_brain_schema.sql

CREATE TABLE IF NOT EXISTS products (
    product_id    UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id      VARCHAR(100) NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    channel       TEXT         NOT NULL DEFAULT 'shopify',
    sku           TEXT,
    asin          TEXT,
    product_title TEXT         NOT NULL,
    brand         TEXT,
    category      TEXT,
    product_type  TEXT,
    key_specs     JSONB        DEFAULT '{}'::jsonb,
    status        TEXT         DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'archived')),
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at    TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    CONSTRAINT unique_sku_per_store UNIQUE (store_id, sku)
);


-- =============================================================================
-- 5. PRODUCT KNOWLEDGE TABLE
-- =============================================================================
-- Product-specific support knowledge entries linked to a product row.
-- Queried by KnowledgeService.get_knowledge_for_product() filtered by
-- knowledge_type and applies_to_channel.
-- Source: knowledge_brain_schema.sql

CREATE TABLE IF NOT EXISTS product_knowledge (
    knowledge_id           UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id             UUID    NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    knowledge_type         TEXT    NOT NULL CHECK (knowledge_type IN (
                               'troubleshooting', 'safety', 'charging', 'battery',
                               'reset_guide', 'returns', 'warranty', 'damaged_item',
                               'cancellation', 'delivery', 'usage', 'other'
                           )),
    title                  TEXT    NOT NULL,
    content                TEXT    NOT NULL,
    risk_level             TEXT    DEFAULT 'low' CHECK (risk_level IN ('low', 'medium', 'high')),
    applies_to_channel     TEXT    DEFAULT 'all' CHECK (applies_to_channel IN ('all', 'shopify', 'amazon')),
    human_review_required  BOOLEAN DEFAULT false,
    created_at             TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at             TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);


-- =============================================================================
-- 6. CHAT LOGS TABLE
-- =============================================================================
-- Primary table for all customer↔bot conversation messages.
-- Written by POST /api/chat. Read by GET /api/conversations.
-- The `matched_source` column stores JSON metadata (brain_mode, intent, source,
-- confidence, escalation_reason, effective_status) serialised as a VARCHAR(255).
-- `status` is constrained to the 4 DB-safe values; effective_status is stored
-- in the matched_source JSON to surface 'auto_replied' to the dashboard without
-- a schema migration.

CREATE TABLE IF NOT EXISTS chat_logs (
    id                UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id          VARCHAR(100) NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    session_id        VARCHAR(255) NOT NULL,
    user_message      TEXT         NOT NULL,
    assistant_message TEXT         NOT NULL,
    matched_source    VARCHAR(255),             -- JSON metadata blob or plain title string
    confidence        DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    escalated         BOOLEAN      NOT NULL DEFAULT FALSE,
    status            VARCHAR(50)  NOT NULL DEFAULT 'new'
                          CHECK (status IN ('new', 'needs_escalation', 'in_progress', 'resolved')),
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);


-- =============================================================================
-- 7. AGENT REPLIES TABLE
-- =============================================================================
-- Stores replies sent by human agents from the admin dashboard.
-- Written by POST /api/agent-replies. Read by GET /api/agent-replies/{session_id}.
-- Also fetched in bulk by GET /api/conversations (joined with chat_logs in API layer).

CREATE TABLE IF NOT EXISTS agent_replies (
    id         UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) NOT NULL,
    message    TEXT         NOT NULL,
    status     VARCHAR(50)  NOT NULL DEFAULT 'sent',  -- 'sent' | 'read' | 'deleted'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);


-- =============================================================================
-- 8. STAFF NOTES TABLE
-- =============================================================================
-- Internal staff notes on a support session. Writable only from admin dashboard.
-- Two foreign key patterns exist in main.py:
--   a) Direct: staff_notes.session_id = session_id (primary query pattern)
--   b) Legacy: staff_notes.conversation_id = conversations.id (cascade delete path)
-- Both `session_id` and `conversation_id` columns are included here.

CREATE TABLE IF NOT EXISTS staff_notes (
    id              UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      VARCHAR(255),              -- Primary lookup column (modern path)
    conversation_id UUID,                      -- Legacy FK for cascade delete (may be NULL)
    author          VARCHAR(255) NOT NULL DEFAULT 'Agent',
    note            TEXT         NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);


-- =============================================================================
-- 9. REPLY DRAFTS TABLE
-- =============================================================================
-- Draft reply text composed in the admin dashboard reply box.
-- `session_id` has a UNIQUE constraint because the app uses upsert:
--   supabase_client.table("reply_drafts").upsert(draft_entry, on_conflict="session_id")
-- `updated_at` is maintained by a trigger.

CREATE TABLE IF NOT EXISTS reply_drafts (
    id         UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    draft_text TEXT         NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);


-- =============================================================================
-- 10. CONVERSATIONS TABLE (Legacy / cascade delete support)
-- =============================================================================
-- Original conversation grouping table. No longer the primary write path but
-- is still queried during conversation delete to cascade-clean staff_notes
-- and messages. Included so delete operations do not fail.

CREATE TABLE IF NOT EXISTS conversations (
    id         UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id   VARCHAR(100) NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    session_id VARCHAR(255) NOT NULL,
    status     VARCHAR(50)  NOT NULL DEFAULT 'active'
                   CHECK (status IN ('active', 'escalated', 'closed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);


-- =============================================================================
-- 11. MESSAGES TABLE (Legacy / cascade delete support)
-- =============================================================================
-- Original per-message rows. Not the primary write path. Included so the
-- conversations cascade delete does not error on a missing messages table.

CREATE TABLE IF NOT EXISTS messages (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID        NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender          VARCHAR(50) NOT NULL CHECK (sender IN ('user', 'bot', 'agent')),
    content         TEXT        NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);


-- =============================================================================
-- 12. ESCALATIONS TABLE (Legacy / cascade delete support)
-- =============================================================================
-- Original escalation records linked to conversations.
-- Included so the conversations cascade delete does not error on a missing
-- escalations table.

CREATE TABLE IF NOT EXISTS escalations (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID        NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    reason          TEXT,
    status          VARCHAR(50) NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'resolved', 'ignored')),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);


-- =============================================================================
-- INDEXES
-- =============================================================================

-- stores
-- (Primary key index on `id` is automatic)

-- support_articles
CREATE INDEX IF NOT EXISTS idx_support_articles_store   ON support_articles(store_id);
CREATE INDEX IF NOT EXISTS idx_support_articles_channel ON support_articles(channel);

-- article_chunks
CREATE INDEX IF NOT EXISTS idx_article_chunks_article   ON article_chunks(article_id);
CREATE INDEX IF NOT EXISTS idx_article_chunks_store     ON article_chunks(store_id);

-- products
CREATE INDEX IF NOT EXISTS idx_products_store           ON products(store_id);
CREATE INDEX IF NOT EXISTS idx_products_sku             ON products(sku);
CREATE INDEX IF NOT EXISTS idx_products_asin            ON products(asin);
CREATE INDEX IF NOT EXISTS idx_products_type            ON products(product_type);
CREATE INDEX IF NOT EXISTS idx_products_channel         ON products(channel);

-- product_knowledge
CREATE INDEX IF NOT EXISTS idx_product_knowledge_product ON product_knowledge(product_id);
CREATE INDEX IF NOT EXISTS idx_product_knowledge_type    ON product_knowledge(knowledge_type);
CREATE INDEX IF NOT EXISTS idx_product_knowledge_risk    ON product_knowledge(risk_level);

-- chat_logs
CREATE INDEX IF NOT EXISTS idx_chat_logs_session        ON chat_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_logs_store          ON chat_logs(store_id);
CREATE INDEX IF NOT EXISTS idx_chat_logs_status         ON chat_logs(status);
CREATE INDEX IF NOT EXISTS idx_chat_logs_created        ON chat_logs(created_at DESC);

-- agent_replies
CREATE INDEX IF NOT EXISTS idx_agent_replies_session    ON agent_replies(session_id);

-- staff_notes
CREATE INDEX IF NOT EXISTS idx_staff_notes_session      ON staff_notes(session_id);
CREATE INDEX IF NOT EXISTS idx_staff_notes_conv         ON staff_notes(conversation_id);

-- reply_drafts
CREATE INDEX IF NOT EXISTS idx_reply_drafts_session     ON reply_drafts(session_id);

-- conversations
CREATE INDEX IF NOT EXISTS idx_conversations_session    ON conversations(session_id);

-- messages
CREATE INDEX IF NOT EXISTS idx_messages_conversation    ON messages(conversation_id);


-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Shared trigger function: auto-updates `updated_at` column on UPDATE
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';


-- Trigger: products.updated_at
DROP TRIGGER IF EXISTS update_products_updated_at ON products;
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- Trigger: product_knowledge.updated_at
DROP TRIGGER IF EXISTS update_product_knowledge_updated_at ON product_knowledge;
CREATE TRIGGER update_product_knowledge_updated_at
    BEFORE UPDATE ON product_knowledge
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- Trigger: reply_drafts.updated_at
DROP TRIGGER IF EXISTS update_reply_drafts_updated_at ON reply_drafts;
CREATE TRIGGER update_reply_drafts_updated_at
    BEFORE UPDATE ON reply_drafts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- =============================================================================
-- END OF STAGING SCHEMA BASELINE
-- =============================================================================
-- Next step: Run backend/db/staging_seed_base.sql
-- =============================================================================
