-- =========================================================================
-- HOVERBOARD STORE KNOWLEDGE PACK V1
-- =========================================================================
-- This script seeds website-derived policies, product guidelines, and
-- safety instructions into Supabase products, product_knowledge, and
-- support_articles tables for hoverboard_store.
--
-- Running this script is completely idempotent.
-- =========================================================================

-- -------------------------------------------------------------------------
-- 1. CLEANUP OLD ENTRIES (Enforcing Idempotency)
-- -------------------------------------------------------------------------
DELETE FROM product_knowledge 
WHERE product_id IN (
    SELECT product_id FROM products 
    WHERE store_id = 'hoverboard_store' 
      AND key_specs->>'source' = 'website_knowledge_v1'
);

DELETE FROM products 
WHERE store_id = 'hoverboard_store' 
  AND key_specs->>'source' = 'website_knowledge_v1';

DELETE FROM support_articles
WHERE store_id = 'hoverboard_store'
  AND title IN (
    'UK Delivery and Dispatch Policy',
    '12-Month Manufacturer Warranty',
    '30-Day Return and Refund Policy',
    'UKCA & CE Safety Certification',
    'Hoverboard and Electric Scooter Safety Regulations',
    'Helmet and Protective Gear Recommendation',
    'First Order Newsletter Discount',
    'Customer Support Contact Information',
    'Critical Battery and Charging Safety Escalation',
    'Order Status and Tracking Verification'
  );

-- -------------------------------------------------------------------------
-- 2. SEED PRODUCTS
-- -------------------------------------------------------------------------
-- We insert general categories and specific products to associate knowledge metadata.
-- Use temporary variables or lookups for child table insertion.

INSERT INTO products (sku, store_id, product_title, brand, category, product_type, key_specs, status) VALUES
(
    'hb-store-policy', 
    'hoverboard_store', 
    'Hoverboard Store General Policies & Support', 
    'Hoverboard Store', 
    'General Policies', 
    'policy', 
    '{"source": "website_knowledge_v1"}'::jsonb, 
    'active'
),
(
    'hb-65-classic', 
    'hoverboard_store', 
    '6.5 Inch Classic Hoverboard', 
    'Hoverboard Store', 
    'Hoverboards', 
    'hoverboard', 
    '{"source": "website_knowledge_v1", "size": "6.5 inch"}'::jsonb, 
    'active'
),
(
    'hb-kart-bundle-g1', 
    'hoverboard_store', 
    'G1 Pro Hoverboard + Hoverkart Bundle', 
    'Hoverboard Store', 
    'Hoverboard Bundles', 
    'hoverboard', 
    '{"source": "website_knowledge_v1", "bundle": true}'::jsonb, 
    'active'
),
(
    'hb-85-offroad', 
    'hoverboard_store', 
    '8.5 Inch Off-Road All-Terrain Hoverboard', 
    'Hoverboard Store', 
    'Hoverboards', 
    'hoverboard', 
    '{"source": "website_knowledge_v1", "size": "8.5 inch", "terrain": "off-road"}'::jsonb, 
    'active'
),
(
    'sc-kids-lite', 
    'hoverboard_store', 
    'Kids Electric Scooter Lite', 
    'Hoverboard Store', 
    'Electric Scooters', 
    'scooter', 
    '{"source": "website_knowledge_v1", "user_group": "kids"}'::jsonb, 
    'active'
),
(
    'hb-parts-acc', 
    'hoverboard_store', 
    'Hoverboard Replacement Parts and Accessories', 
    'Hoverboard Store', 
    'Parts & Accessories', 
    'accessory', 
    '{"source": "website_knowledge_v1"}'::jsonb, 
    'active'
);

-- -------------------------------------------------------------------------
-- 3. SEED PRODUCT KNOWLEDGE
-- -------------------------------------------------------------------------

-- A. General Store Policies & Contact Support (SKU: hb-store-policy)
INSERT INTO product_knowledge (product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required)
SELECT 
    product_id, 
    'delivery', 
    'UK Delivery and Dispatch Policy', 
    'Hoverboard Store offers Free UK Delivery with next-day dispatch or next-day delivery options available at checkout for orders placed before 2 PM GMT. Standard shipping usually takes 2-3 business days within the UK. We do not invent exact delivery dates for specific orders; please contact support to verify.', 
    'low', 
    'all', 
    false
FROM products WHERE sku = 'hb-store-policy' AND store_id = 'hoverboard_store';

INSERT INTO product_knowledge (product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required)
SELECT 
    product_id, 
    'warranty', 
    '12-Month Manufacturer Warranty', 
    'All hoverboards, hoverkarts, and electric scooters purchased from Hoverboard Store include a 12-Month Warranty covering manufacturing defects and technical malfunctions. The warranty does not cover accidental water damage, physical damage, or wear and tear from general usage.', 
    'low', 
    'all', 
    false
FROM products WHERE sku = 'hb-store-policy' AND store_id = 'hoverboard_store';

INSERT INTO product_knowledge (product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required)
SELECT 
    product_id, 
    'returns', 
    '30-Day Return and Refund Policy', 
    'We offer a 30-day return policy for unused items in their original packaging, complete with all accessories. To initiate a return, email contact@hoverboardstore.co.uk. Please note that we do not automatically promise refunds or replacements before checking returned items.', 
    'low', 
    'all', 
    false
FROM products WHERE sku = 'hb-store-policy' AND store_id = 'hoverboard_store';

INSERT INTO product_knowledge (product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required)
SELECT 
    product_id, 
    'safety', 
    'UKCA & CE Safety Certification', 
    'All hoverboards and ride-on tech sold by Hoverboard Store are UKCA & CE Certified, meaning they comply with stringent European and UK safety directives. We use only UL-certified chargers and high-quality batteries to ensure maximum safety.', 
    'low', 
    'all', 
    false
FROM products WHERE sku = 'hb-store-policy' AND store_id = 'hoverboard_store';

INSERT INTO product_knowledge (product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required)
SELECT 
    product_id, 
    'usage', 
    'Hoverboard and Electric Scooter Safety Regulations', 
    'Safety Guidance: Under current UK legislation, hoverboards and electric scooters must only be used on private land with the landowner''s permission. Riding them on public roads, pavements, cycle paths, or pedestrian zones is prohibited.', 
    'medium', 
    'all', 
    false
FROM products WHERE sku = 'hb-store-policy' AND store_id = 'hoverboard_store';

INSERT INTO product_knowledge (product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required)
SELECT 
    product_id, 
    'usage', 
    'Helmet and Protective Gear Recommendation', 
    'Safety Guidance: We highly recommend that all riders wear a helmet, elbow pads, knee pads, and wrist guards at all times when operating a hoverboard or electric scooter to prevent injuries.', 
    'low', 
    'all', 
    false
FROM products WHERE sku = 'hb-store-policy' AND store_id = 'hoverboard_store';

INSERT INTO product_knowledge (product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required)
SELECT 
    product_id, 
    'other', 
    'First Order Newsletter Discount', 
    'Sign up for our newsletter to get a 10% off coupon code for your first order at Hoverboard Store. Enter the code at checkout to redeem this newsletter offer.', 
    'low', 
    'all', 
    false
FROM products WHERE sku = 'hb-store-policy' AND store_id = 'hoverboard_store';

INSERT INTO product_knowledge (product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required)
SELECT 
    product_id, 
    'other', 
    'Customer Support Contact Information', 
    'For any inquiries, customer support, or warranty returns, please email contact@hoverboardstore.co.uk. Our UK-based support team will respond to your queries shortly. Do not use other contact channels; we respond exclusively via email.', 
    'low', 
    'all', 
    false
FROM products WHERE sku = 'hb-store-policy' AND store_id = 'hoverboard_store';

-- B. Product Specific Guidance
-- 6.5 inch Hoverboard (SKU: hb-65-classic)
INSERT INTO product_knowledge (product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required)
SELECT 
    product_id, 
    'usage', 
    '6.5 Inch Hoverboard Guidance', 
    'Our 6.5 inch hoverboards are the ideal beginner/kids entry-level model, featuring built-in learner modes and safety sensors. Please note that we do not guarantee product suitability for every child; suitability depends on age, weight, and coordination.', 
    'low', 
    'all', 
    false
FROM products WHERE sku = 'hb-65-classic' AND store_id = 'hoverboard_store';

-- Hoverkart bundle (SKU: hb-kart-bundle-g1)
INSERT INTO product_knowledge (product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required)
SELECT 
    product_id, 
    'usage', 
    'Hoverkart Bundle Beginner Guidance', 
    'The G1 Lite or 6.5 inch hoverboard and kart bundles turn your hoverboard into a three-wheeled go-kart. This hoverkart bundle is perfect for beginners and kids looking for a fun, stable riding experience. Adult supervision is recommended.', 
    'low', 
    'all', 
    false
FROM products WHERE sku = 'hb-kart-bundle-g1' AND store_id = 'hoverboard_store';

-- 8.5 inch off-road (SKU: hb-85-offroad)
INSERT INTO product_knowledge (product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required)
SELECT 
    product_id, 
    'usage', 
    '8.5 Inch Off-Road All-Terrain Hoverboard Guidance', 
    'Our 8.5 inch off-road/all-terrain hoverboards and the G1 Pro model feature heavy-duty wheels, rugged treads, and powerful motors designed for uneven surfaces, gravel, and grass. Ideal for intermediate and advanced riders.', 
    'low', 
    'all', 
    false
FROM products WHERE sku = 'hb-85-offroad' AND store_id = 'hoverboard_store';

-- Kids electric scooter (SKU: sc-kids-lite)
INSERT INTO product_knowledge (product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required)
SELECT 
    product_id, 
    'usage', 
    'Kids Electric Scooter Guidance', 
    'Hoverboard Store provides kids electric scooters designed with adjustable handlebars and safety speed limits. We do not guarantee product suitability for every child; please review weight limits and age recommendations before purchasing.', 
    'low', 
    'all', 
    false
FROM products WHERE sku = 'sc-kids-lite' AND store_id = 'hoverboard_store';

-- Parts/accessories (SKU: hb-parts-acc)
INSERT INTO product_knowledge (product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required)
SELECT 
    product_id, 
    'troubleshooting', 
    'Parts and Accessories Support', 
    'We offer replacement parts and accessories, including chargers, replacement hoverboard outer shells, batteries, hoverkart straps, and wheels. For technical support with replacement parts, contact contact@hoverboardstore.co.uk.', 
    'low', 
    'all', 
    false
FROM products WHERE sku = 'hb-parts-acc' AND store_id = 'hoverboard_store';

-- C. High Risk Safety / Support Escalations
-- Battery safety escalation (SKU: hb-store-policy)
INSERT INTO product_knowledge (product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required)
SELECT 
    product_id, 
    'battery', 
    'Critical Battery and Charging Safety Escalation', 
    'Safety Guidance: Always charge your hoverboard on a hard, flat surface in a well-ventilated room using the official UL-certified charger. Never leave charging unattended or overnight. Any issues involving battery heat, fire, smoke, sparks, overheating, swelling, or water damage MUST require immediate support agent review; do not attempt to troubleshoot yourself.', 
    'high', 
    'all', 
    true
FROM products WHERE sku = 'hb-store-policy' AND store_id = 'hoverboard_store';

-- Order tracking verification escalation (SKU: hb-store-policy)
INSERT INTO product_knowledge (product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required)
SELECT 
    product_id, 
    'delivery', 
    'Order Status and Tracking Verification', 
    'To track or check your order status, we require customer and order verification details (including your full name, email, billing address, and order reference number). Our system does not disclose tracking info without these verifications to protect privacy.', 
    'medium', 
    'all', 
    true
FROM products WHERE sku = 'hb-store-policy' AND store_id = 'hoverboard_store';

-- -------------------------------------------------------------------------
-- 4. SEED GENERAL SUPPORT ARTICLES
-- -------------------------------------------------------------------------
INSERT INTO support_articles (store_id, title, content) VALUES
('hoverboard_store', 'UK Delivery and Dispatch Policy', 'Hoverboard Store offers Free UK Delivery with next-day dispatch or next-day delivery options available at checkout for orders placed before 2 PM GMT. Standard shipping usually takes 2-3 business days within the UK. We do not invent exact delivery dates for specific orders; please contact support to verify.'),
('hoverboard_store', '12-Month Manufacturer Warranty', 'All hoverboards, hoverkarts, and electric scooters purchased from Hoverboard Store include a 12-Month Warranty covering manufacturing defects and technical malfunctions. The warranty does not cover accidental water damage, physical damage, or wear and tear from general usage.'),
('hoverboard_store', '30-Day Return and Refund Policy', 'We offer a 30-day return policy for unused items in their original packaging, complete with all accessories. To initiate a return, email contact@hoverboardstore.co.uk. Please note that we do not automatically promise refunds or replacements before checking returned items.'),
('hoverboard_store', 'UKCA & CE Safety Certification', 'All hoverboards and ride-on tech sold by Hoverboard Store are UKCA & CE Certified, meaning they comply with stringent European and UK safety directives. We use only UL-certified chargers and high-quality batteries to ensure maximum safety.'),
('hoverboard_store', 'Hoverboard and Electric Scooter Safety Regulations', 'Safety Guidance: Under current UK legislation, hoverboards and electric scooters must only be used on private land with the landowner''s permission. Riding them on public roads, pavements, cycle paths, or pedestrian zones is prohibited.'),
('hoverboard_store', 'Helmet and Protective Gear Recommendation', 'Safety Guidance: We highly recommend that all riders wear a helmet, elbow pads, knee pads, and wrist guards at all times when operating a hoverboard or electric scooter to prevent injuries.'),
('hoverboard_store', 'First Order Newsletter Discount', 'Sign up for our newsletter to get a 10% off coupon code for your first order at Hoverboard Store. Enter the code at checkout to redeem this newsletter offer.'),
('hoverboard_store', 'Customer Support Contact Information', 'For any inquiries, customer support, or warranty returns, please email contact@hoverboardstore.co.uk. Our UK-based support team will respond to your queries shortly. Do not use other contact channels; we respond exclusively via email.'),
('hoverboard_store', 'Critical Battery and Charging Safety Escalation', 'Safety Guidance: Always charge your hoverboard on a hard, flat surface in a well-ventilated room using the official UL-certified charger. Never leave charging unattended or overnight. Any issues involving battery heat, fire, smoke, sparks, overheating, swelling, or water damage MUST require immediate support agent review; do not attempt to troubleshoot yourself.'),
('hoverboard_store', 'Order Status and Tracking Verification', 'To track or check your order status, we require customer and order verification details (including your full name, email, billing address, and order reference number). Our system does not disclose tracking info without these verifications to protect privacy.');
