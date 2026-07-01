-- =========================================================================
-- KNOWLEDGE BRAIN SCHEMA MIGRATION
-- =========================================================================
-- This file defines the tables for the Product + Policy Knowledge Brain.
--
-- IMPORTANT RULES:
-- 1. Do not run it automatically. Review before executing.
-- 2. Do not delete or break existing support_articles.
-- 3. Existing support_articles table is preserved.
-- =========================================================================

-- Ensure Amazon store/account identifiers exist in the stores table to maintain referential integrity
INSERT INTO stores (id, name, domain) VALUES
('gift_gadgets', 'GiftGadgets Amazon Sandbox', 'amazon.com'),
('GiftGadgets', 'GiftGadgets Amazon Sandbox', 'amazon.com')
ON CONFLICT (id) DO NOTHING;

-- 1. Products Table
CREATE TABLE IF NOT EXISTS products (
    product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id VARCHAR(100) NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    channel TEXT NOT NULL DEFAULT 'shopify',
    sku TEXT,
    asin TEXT,
    product_title TEXT NOT NULL,
    brand TEXT,
    category TEXT,
    product_type TEXT,
    key_specs JSONB DEFAULT '{}'::jsonb,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'archived')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    CONSTRAINT unique_sku_per_store UNIQUE (store_id, sku)
);

-- 2. Product Knowledge Table
CREATE TABLE IF NOT EXISTS product_knowledge (
    knowledge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    knowledge_type TEXT NOT NULL CHECK (knowledge_type IN (
        'troubleshooting', 'safety', 'charging', 'battery', 
        'reset_guide', 'returns', 'warranty', 'damaged_item', 
        'cancellation', 'delivery', 'usage', 'other'
    )),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    risk_level TEXT DEFAULT 'low' CHECK (risk_level IN ('low', 'medium', 'high')),
    applies_to_channel TEXT DEFAULT 'all' CHECK (applies_to_channel IN ('all', 'shopify', 'amazon')),
    human_review_required BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- =========================================================================
-- INDEXES FOR QUERY OPTIMIZATION
-- =========================================================================
CREATE INDEX IF NOT EXISTS idx_products_store ON products(store_id);
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_products_asin ON products(asin);
CREATE INDEX IF NOT EXISTS idx_products_type ON products(product_type);

CREATE INDEX IF NOT EXISTS idx_product_knowledge_product ON product_knowledge(product_id);
CREATE INDEX IF NOT EXISTS idx_product_knowledge_type ON product_knowledge(knowledge_type);
CREATE INDEX IF NOT EXISTS idx_product_knowledge_risk ON product_knowledge(risk_level);

-- =========================================================================
-- TRIGGERS & FUNCTIONS TO UPDATE updated_at COLUMN
-- =========================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_products_updated_at ON products;
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_product_knowledge_updated_at ON product_knowledge;
CREATE TRIGGER update_product_knowledge_updated_at
    BEFORE UPDATE ON product_knowledge
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


