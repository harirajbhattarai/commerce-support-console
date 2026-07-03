-- =============================================================================
-- STAGING SEED BASE
-- backend/db/staging_seed_base.sql
-- =============================================================================
--
-- PURPOSE:
--   Seeds safe reference and test data into the staging Supabase project.
--   Provides the minimum data needed for the Commerce Support Console backend
--   to start, serve the chat widget, and pass integration tests on staging.
--
-- SAFE FOR: STAGING ONLY
-- SAFE FOR PRODUCTION: NO — use numbered seed files in backend/db/seeds/ instead
--
-- CONTAINS CUSTOMER DATA: NO
--   This file contains NO real customer messages, sessions, emails, names,
--   order numbers, or personal information of any kind.
--
-- IDEMPOTENT: YES
--   Safe to run multiple times. Uses DELETE-then-INSERT for knowledge rows,
--   ON CONFLICT DO UPDATE for stores.
--
-- RUN ORDER:
--   STEP 1: staging_schema_baseline.sql  (run first — creates all tables)
--   STEP 2: staging_seed_base.sql        (this file — seeds data)
--
-- HOW TO RUN:
--   Supabase Dashboard → SQL Editor → paste this file → Run
--
-- WHAT IS SEEDED:
--   Section 1: stores — 5 store rows (hoverboard_store + amazon/test variants)
--   Section 2: support_articles — 8 articles covering Hoverboard Store core topics
--   Section 3: products — 3 test products for hoverboard_store
--   Section 4: product_knowledge — 5 knowledge entries tied to test products
--   Section 5: hcs_gadgets / aroma_haven — minimal placeholder articles
--
-- LAST UPDATED: 2026-07-03
-- =============================================================================


-- =============================================================================
-- SECTION 1: STORES
-- =============================================================================
-- Reference store rows. These are business-level identifiers used as foreign
-- keys by all other tables. Must exist before any other rows are inserted.
--
-- Idempotency: ON CONFLICT (id) DO UPDATE — safe to re-run.

INSERT INTO stores (id, name, domain, channel) VALUES
    ('hoverboard_store',   'Hoverboard Store UK',            'hoverboardstore.co.uk', 'shopify'),
    ('hcs_gadgets',        'HCS Gadgets',                    'hcsgadgets.co.uk',      'shopify'),
    ('aroma_haven',        'Aroma Haven Botanicals',         'aromahaven.co.uk',      'shopify'),
    ('gift_gadgets',       'GiftGadgets Amazon Sandbox',     'amazon.com',            'amazon'),
    ('GiftGadgets',        'GiftGadgets Amazon (Alt ID)',    'amazon.com',            'amazon')
ON CONFLICT (id) DO UPDATE
    SET name    = EXCLUDED.name,
        domain  = EXCLUDED.domain,
        channel = EXCLUDED.channel;


-- =============================================================================
-- SECTION 2: SUPPORT ARTICLES — HOVERBOARD STORE
-- =============================================================================
-- These are the core support knowledge articles that the bot uses to answer
-- customer questions about Hoverboard Store UK.
--
-- All articles are derived from publicly available website content and
-- established store policy — no customer data.
--
-- Idempotency: DELETE by (store_id, title) then INSERT.
-- This guarantees stale content is replaced if re-run with updated text.

DELETE FROM support_articles
WHERE store_id = 'hoverboard_store'
  AND title IN (
    'UK Delivery and Dispatch Policy',
    '30-Day Return and Refund Policy',
    '12-Month Manufacturer Warranty',
    'UKCA and CE Safety Certification',
    'Hoverboard and Electric Scooter Legal Usage Rules (UK)',
    'Critical Battery and Charging Safety — Stop Use Immediately',
    'Customer Support Contact Information',
    'Order Status and Tracking Verification',
    'Generic Hoverboard Battery and Charging Safety'
  );


-- Article 1: UK Delivery
INSERT INTO support_articles (store_id, title, content, intent_tags, channel)
VALUES (
    'hoverboard_store',
    'UK Delivery and Dispatch Policy',
    'Hoverboard Store UK offers free standard UK delivery on all orders. Orders placed before 2 PM GMT Monday to Friday are typically dispatched the same day. Standard delivery takes 2–3 working days. Next-day delivery is available at an additional charge and must be selected at checkout. Delivery is to mainland UK addresses only. For any delivery enquiries, please email contact@hoverboardstore.co.uk with your order number.',
    ARRAY['delivery_general', 'shipping_timeline', 'order_tracking'],
    'shopify'
);


-- Article 2: 30-Day Return
INSERT INTO support_articles (store_id, title, content, intent_tags, channel)
VALUES (
    'hoverboard_store',
    '30-Day Return and Refund Policy',
    'We offer a 30-day return policy for unused items returned in their original packaging. To start a return, please email contact@hoverboardstore.co.uk with your order number and reason for return. Our team will provide return instructions. Items must be returned in original condition. Return postage costs may apply for non-faulty items. Refunds are processed within 3–5 working days of receiving the returned item.',
    ARRAY['return_policy', 'refund_question', 'return_request'],
    'shopify'
);


-- Article 3: 12-Month Warranty
INSERT INTO support_articles (store_id, title, content, intent_tags, channel)
VALUES (
    'hoverboard_store',
    '12-Month Manufacturer Warranty',
    'All Hoverboard Store UK products come with a 12-month manufacturer warranty from the date of purchase. The warranty covers manufacturing defects and battery faults under normal use conditions. It does not cover physical damage from impact, water damage, damage from non-approved chargers, modifications, or normal wear and tear. To make a warranty claim, please email contact@hoverboardstore.co.uk with your order number, a description of the fault, and photographs or video evidence of the issue.',
    ARRAY['warranty_policy', 'warranty_claim', 'warranty_question'],
    'shopify'
);


-- Article 4: Safety certification
INSERT INTO support_articles (store_id, title, content, intent_tags, channel)
VALUES (
    'hoverboard_store',
    'UKCA and CE Safety Certification',
    'All hoverboards and electric scooters sold by Hoverboard Store UK are UKCA and CE certified, meeting UK and European safety standards. Our products are regularly tested to ensure they comply with electrical and battery safety regulations. We recommend using only the supplied charger and following all safety guidelines in the product manual.',
    ARRAY['safety_certification', 'product_safety', 'presale_safety'],
    'shopify'
);


-- Article 5: UK Legal Usage
INSERT INTO support_articles (store_id, title, content, intent_tags, channel)
VALUES (
    'hoverboard_store',
    'Hoverboard and Electric Scooter Legal Usage Rules (UK)',
    'Under UK law, hoverboards and personal electric vehicles are classified as Personal Light Electric Vehicles (PLEVs) and are not permitted on public roads, pavements, or cycle paths. They may only be used on private land with the landowner''s permission — for example, in your garden, driveway, or a private park with consent. Hoverboard Store UK recommends responsible use only on appropriate private terrain. We strongly advise all riders, especially children, to wear a helmet, knee pads, and wrist guards at all times.',
    ARRAY['legal_usage', 'road_law', 'where_to_ride', 'safety_guidance'],
    'shopify'
);


-- Article 6: Battery Safety Escalation (HIGH RISK — always escalate)
INSERT INTO support_articles (store_id, title, content, intent_tags, channel)
VALUES (
    'hoverboard_store',
    'Critical Battery and Charging Safety — Stop Use Immediately',
    'Please stop using the hoverboard immediately. Do not charge it again. If it is safe to do so, unplug it from any power source and move it away from flammable materials such as furniture, curtains, or carpets. Do not attempt to repair the battery or charger yourself. Our support team has been notified and will reply here shortly. You can also contact us directly at contact@hoverboardstore.co.uk.',
    ARRAY['battery_safety', 'fire_risk', 'smoke', 'burning_smell', 'overheating', 'sparks', 'swollen_battery'],
    'shopify'
);


-- Article 7: Contact Information
INSERT INTO support_articles (store_id, title, content, intent_tags, channel)
VALUES (
    'hoverboard_store',
    'Customer Support Contact Information',
    'The best way to reach Hoverboard Store UK customer support is by email at contact@hoverboardstore.co.uk. Please include your order number and a description of your query in your email. Our support team aims to respond within 1–2 working days. For urgent safety issues such as smoke, burning smells, or sparks from your device, please stop use immediately and email us straight away.',
    ARRAY['speak_to_human', 'contact_support', 'customer_service'],
    'shopify'
);


-- Article 8: Order tracking / verification
INSERT INTO support_articles (store_id, title, content, intent_tags, channel)
VALUES (
    'hoverboard_store',
    'Order Status and Tracking Verification',
    'To check the status of your order, please email contact@hoverboardstore.co.uk with your order number and the email address used at checkout. Our team will provide your current order status, fulfilment status, and tracking information. Please allow 2–3 working days from your order date before contacting us about delivery status, as dispatch confirmation emails are sent automatically when your order ships.',
    ARRAY['order_issue', 'order_tracking', 'delivery_status', 'where_is_my_order'],
    'shopify'
);


-- Article 9: Generic battery safety (matching existing production title used by support_brain.py)
INSERT INTO support_articles (store_id, title, content, intent_tags, channel)
VALUES (
    'hoverboard_store',
    'Generic Hoverboard Battery and Charging Safety',
    'Please stop using the hoverboard immediately if you notice any burning smell, smoke, sparks, unusual heat, or visible swelling of the battery. Do not charge it again. Unplug it from the power source if safe to do so, and keep it away from flammable materials. Do not attempt to open, repair, or dispose of the battery yourself. Contact contact@hoverboardstore.co.uk immediately with your order number. Our support team has been notified.',
    ARRAY['battery_safety', 'charging_safety', 'fire_risk', 'high_risk_safety'],
    'shopify'
);


-- =============================================================================
-- SECTION 3: PRODUCTS — HOVERBOARD STORE (TEST PRODUCTS)
-- =============================================================================
-- Minimal test product rows so that knowledge_service.py product queries
-- return results during staging integration tests.
--
-- These are fictionalised test products using real product category names
-- but generic test SKUs. They contain NO real customer data.
--
-- Idempotency: ON CONFLICT (store_id, sku) DO UPDATE.

INSERT INTO products (sku, store_id, channel, product_title, brand, category, product_type, key_specs, status)
VALUES
    (
        'TEST-HB-6.5-STAGING',
        'hoverboard_store',
        'shopify',
        '6.5 Inch Self-Balancing Hoverboard (Staging Test Product)',
        'Hoverboard Store',
        'Hoverboards',
        'hoverboard',
        '{
            "source": "staging_seed_v1",
            "wheel_size": "6.5 inch",
            "terrain": "flat smooth surfaces",
            "age_min": 8,
            "ukca_certified": true
        }'::jsonb,
        'active'
    ),
    (
        'TEST-HB-8.5-STAGING',
        'hoverboard_store',
        'shopify',
        '8.5 Inch All-Terrain Hoverboard (Staging Test Product)',
        'Hoverboard Store',
        'Hoverboards',
        'hoverboard',
        '{
            "source": "staging_seed_v1",
            "wheel_size": "8.5 inch",
            "terrain": "grass, gravel, off-road",
            "age_min": 8,
            "ukca_certified": true
        }'::jsonb,
        'active'
    ),
    (
        'TEST-HVK-STAGING',
        'hoverboard_store',
        'shopify',
        '6.5 Inch Hoverboard + Hoverkart Bundle (Staging Test Product)',
        'Hoverboard Store',
        'Bundles',
        'hoverboard',
        '{
            "source": "staging_seed_v1",
            "wheel_size": "6.5 inch",
            "includes_hoverkart": true,
            "age_min": 8,
            "ukca_certified": true
        }'::jsonb,
        'active'
    )
ON CONFLICT (store_id, sku) DO UPDATE
    SET product_title = EXCLUDED.product_title,
        key_specs     = EXCLUDED.key_specs,
        status        = EXCLUDED.status;


-- =============================================================================
-- SECTION 4: PRODUCT KNOWLEDGE — HOVERBOARD STORE (TEST ENTRIES)
-- =============================================================================
-- Core knowledge entries linked to the staging test products above.
-- These allow KnowledgeService.get_knowledge_for_product() to return results
-- during staging integration tests.
--
-- Idempotency: DELETE by (product_id, title) then INSERT.

-- Lookup the staging test 6.5" hoverboard product_id for FK references
-- (done with a DO block to handle PL/pgSQL without requiring a temp table)

DO $$
DECLARE
    v_hb65_id  UUID;
    v_hb85_id  UUID;
    v_hvk_id   UUID;
BEGIN
    SELECT product_id INTO v_hb65_id
    FROM products
    WHERE store_id = 'hoverboard_store' AND sku = 'TEST-HB-6.5-STAGING'
    LIMIT 1;

    SELECT product_id INTO v_hb85_id
    FROM products
    WHERE store_id = 'hoverboard_store' AND sku = 'TEST-HB-8.5-STAGING'
    LIMIT 1;

    SELECT product_id INTO v_hvk_id
    FROM products
    WHERE store_id = 'hoverboard_store' AND sku = 'TEST-HVK-STAGING'
    LIMIT 1;

    -- Clean up any previous staging seed knowledge rows
    DELETE FROM product_knowledge
    WHERE product_id IN (v_hb65_id, v_hb85_id, v_hvk_id)
      AND title IN (
        'Staging Test: 6.5 Inch Hoverboard — Not Turning On',
        'Staging Test: 6.5 Inch Hoverboard — Battery and Charging Safety',
        'Staging Test: 6.5 Inch Hoverboard — Reset and Calibration',
        'Staging Test: 8.5 Inch Hoverboard — Terrain and Usage Guide',
        'Staging Test: Hoverkart Bundle — Fitting and Compatibility'
      );

    -- Knowledge entry 1: Not turning on (6.5")
    IF v_hb65_id IS NOT NULL THEN
        INSERT INTO product_knowledge (
            product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required
        ) VALUES (
            v_hb65_id,
            'troubleshooting',
            'Staging Test: 6.5 Inch Hoverboard — Not Turning On',
            'If your 6.5 inch hoverboard will not turn on, try these steps: 1. Confirm the battery is charged — connect the charger and check the LED turns red. Leave on charge for at least 20 minutes before trying again. 2. Press and hold the power button firmly for 3–5 full seconds. 3. Inspect the charging port for debris or bent pins. If it still does not turn on after a full charge, contact contact@hoverboardstore.co.uk with your order number and a description of the issue.',
            'low',
            'shopify',
            false
        );
    END IF;

    -- Knowledge entry 2: Battery safety (6.5") — high risk
    IF v_hb65_id IS NOT NULL THEN
        INSERT INTO product_knowledge (
            product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required
        ) VALUES (
            v_hb65_id,
            'battery',
            'Staging Test: 6.5 Inch Hoverboard — Battery and Charging Safety',
            'Please stop using the hoverboard immediately if you notice any burning smell, smoke, sparks, or unusual heat. Do not charge it again. Unplug from the power source if safe, and move it away from flammable materials. Do not attempt to repair the battery or charger yourself. Contact contact@hoverboardstore.co.uk immediately. Our support team has been notified.',
            'high',
            'shopify',
            true
        );
    END IF;

    -- Knowledge entry 3: Reset and calibration (6.5")
    IF v_hb65_id IS NOT NULL THEN
        INSERT INTO product_knowledge (
            product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required
        ) VALUES (
            v_hb65_id,
            'reset_guide',
            'Staging Test: 6.5 Inch Hoverboard — Reset and Calibration',
            'To reset and calibrate your 6.5 inch hoverboard: 1. Place the board on a completely flat, level surface. 2. Ensure the board is powered off. 3. Press and hold the power button for 10 seconds until the lights flash rapidly. 4. Release the button. 5. Turn the board off. 6. Turn it back on. The board should now be calibrated. If beeping or tilting continues after calibration and a full charge, contact contact@hoverboardstore.co.uk with your order number.',
            'low',
            'shopify',
            false
        );
    END IF;

    -- Knowledge entry 4: Terrain guide (8.5")
    IF v_hb85_id IS NOT NULL THEN
        INSERT INTO product_knowledge (
            product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required
        ) VALUES (
            v_hb85_id,
            'usage',
            'Staging Test: 8.5 Inch Hoverboard — Terrain and Usage Guide',
            'The 8.5 inch all-terrain hoverboard is designed for use on grass, gravel, mud, and uneven outdoor surfaces. It is larger and heavier than the 6.5 inch model and may be more difficult for younger or smaller children to manage. It must be used on private land with the landowner''s permission only — not on public roads, pavements, or cycle paths under UK law. Always wear a helmet and protective gear.',
            'low',
            'shopify',
            false
        );
    END IF;

    -- Knowledge entry 5: Hoverkart fitting
    IF v_hvk_id IS NOT NULL THEN
        INSERT INTO product_knowledge (
            product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required
        ) VALUES (
            v_hvk_id,
            'usage',
            'Staging Test: Hoverkart Bundle — Fitting and Compatibility',
            'The hoverkart frame converts the 6.5 inch hoverboard into a three-wheeled seated go-kart style ride. To attach the hoverkart, place the hoverboard into the frame clamps and ensure all locking pins are fully engaged on both sides. Do not ride if the hoverkart feels loose or unstable. Check all attachment points before each use. If you are unable to attach the hoverkart securely, contact contact@hoverboardstore.co.uk with your order number and photographs of the attachment area.',
            'low',
            'shopify',
            false
        );
    END IF;

END $$;


-- =============================================================================
-- SECTION 5: SUPPORT ARTICLES — HCS GADGETS (MINIMAL PLACEHOLDER)
-- =============================================================================
-- Minimal article so that the admin dashboard does not error when filtering
-- by store_id = 'hcs_gadgets'. Contains no customer data.

DELETE FROM support_articles
WHERE store_id = 'hcs_gadgets'
  AND title = 'Staging Placeholder — HCS Gadgets General Support';

INSERT INTO support_articles (store_id, title, content, intent_tags, channel)
VALUES (
    'hcs_gadgets',
    'Staging Placeholder — HCS Gadgets General Support',
    'For HCS Gadgets support enquiries, please contact our support team. [Staging placeholder — replace with real content before production seeding.]',
    ARRAY['general_enquiry'],
    'shopify'
);


-- =============================================================================
-- SECTION 6: SUPPORT ARTICLES — AROMA HAVEN (MINIMAL PLACEHOLDER)
-- =============================================================================

DELETE FROM support_articles
WHERE store_id = 'aroma_haven'
  AND title = 'Staging Placeholder — Aroma Haven General Support';

INSERT INTO support_articles (store_id, title, content, intent_tags, channel)
VALUES (
    'aroma_haven',
    'Staging Placeholder — Aroma Haven General Support',
    'For Aroma Haven support enquiries, please contact our support team. [Staging placeholder — replace with real content before production seeding.]',
    ARRAY['general_enquiry'],
    'shopify'
);


-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================
-- After running this file, use these queries to confirm the seed worked:
--
-- SELECT id, name, domain, channel FROM stores ORDER BY id;
-- Expected: 5 rows (hoverboard_store, hcs_gadgets, aroma_haven, gift_gadgets, GiftGadgets)
--
-- SELECT store_id, title FROM support_articles ORDER BY store_id, title;
-- Expected: 11 rows (9 hoverboard_store + 1 hcs_gadgets + 1 aroma_haven)
--
-- SELECT sku, product_title, status FROM products WHERE store_id = 'hoverboard_store';
-- Expected: 3 rows (TEST-HB-6.5-STAGING, TEST-HB-8.5-STAGING, TEST-HVK-STAGING)
--
-- SELECT pk.title, pk.knowledge_type, pk.risk_level
-- FROM product_knowledge pk
-- JOIN products p ON p.product_id = pk.product_id
-- WHERE p.store_id = 'hoverboard_store'
-- ORDER BY pk.title;
-- Expected: 5 rows (3 for 6.5", 1 for 8.5", 1 for bundle)
--
-- SELECT COUNT(*) FROM chat_logs;
-- Expected: 0 (no customer data seeded)
--
-- SELECT COUNT(*) FROM agent_replies;
-- Expected: 0 (no customer data seeded)
-- =============================================================================
--
-- END OF STAGING SEED BASE
-- =============================================================================
