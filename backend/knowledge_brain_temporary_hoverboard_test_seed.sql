-- =========================================================================
-- TEMPORARY HOVERBOARD TEST SEED DATA
-- =========================================================================
-- WARNING: This seed file is strictly for testing the Knowledge Service
-- retrieval pipeline. It is NOT the final Master Commerce Brain data structure
-- and should only be run in local/staging environments for prototyping.
-- =========================================================================

-- 1. Insert Generic Hoverboard Product for Support Cache Testing
INSERT INTO products (
    store_id, 
    channel, 
    sku, 
    asin, 
    product_title, 
    brand, 
    category, 
    product_type, 
    key_specs, 
    status
) VALUES (
    'hoverboard_store', 
    'all', 
    'HOVERBOARD-GENERIC-SUPPORT', 
    NULL, 
    'Generic Hoverboard Support Knowledge', 
    'Generic', 
    'Electric Ride-ons', 
    'hoverboard', 
    '{"support_scope": "generic hoverboard support", "safety_sensitive": true, "source": "temporary_support_cache_test"}'::jsonb, 
    'active'
) ON CONFLICT (store_id, sku) DO UPDATE SET 
    product_title = EXCLUDED.product_title,
    key_specs = EXCLUDED.key_specs,
    status = EXCLUDED.status;

-- 2. Insert Three Product Knowledge Records (Calibration, Battery Safety, Not Charging)
-- Idempotency is enforced using WHERE NOT EXISTS constraints on product_id, knowledge_type, and title.

-- Guide A: Reset and Calibration
INSERT INTO product_knowledge (
    product_id, 
    knowledge_type, 
    title, 
    content, 
    risk_level, 
    applies_to_channel, 
    human_review_required
) 
SELECT 
    p.product_id, 
    'reset_guide', 
    'Generic Hoverboard Reset and Calibration Guide', 
    'Follow these steps to calibrate the hoverboard: 1. Place the hoverboard on a completely flat and level surface. 2. Ensure the hoverboard is completely powered off. 3. Press and hold the power button down for 10 seconds until the lights flash. 4. Release the button, turn the hoverboard off. 5. Turn it back on to complete the calibration process.', 
    'low', 
    'all', 
    false
FROM products p
WHERE p.sku = 'HOVERBOARD-GENERIC-SUPPORT' 
  AND p.store_id = 'hoverboard_store'
  AND NOT EXISTS (
      SELECT 1 
      FROM product_knowledge pk 
      WHERE pk.product_id = p.product_id 
        AND pk.knowledge_type = 'reset_guide'
        AND pk.title = 'Generic Hoverboard Reset and Calibration Guide'
  );

-- Guide B: Battery and Charging Safety (High Risk / Escalate)
INSERT INTO product_knowledge (
    product_id, 
    knowledge_type, 
    title, 
    content, 
    risk_level, 
    applies_to_channel, 
    human_review_required
) 
SELECT 
    p.product_id, 
    'battery', 
    'Generic Hoverboard Battery and Charging Safety', 
    'Charge your hoverboard only on a flat, non-flammable surface in a well-ventilated room. Do not leave the device charging overnight or unattended. Always use the original charger supplied with the product or a manufacturer-approved replacement charger. If the battery becomes excessively hot, emits smoke, smells strange, or deforms, immediately unplug it, move it away from combustible materials, and do not use. If there is overheating, burning smell, smoke, sparks, swelling, liquid damage, charger overheating, or visible battery damage, stop using the product and escalate for human review.', 
    'high', 
    'all', 
    true
FROM products p
WHERE p.sku = 'HOVERBOARD-GENERIC-SUPPORT' 
  AND p.store_id = 'hoverboard_store'
  AND NOT EXISTS (
      SELECT 1 
      FROM product_knowledge pk 
      WHERE pk.product_id = p.product_id 
        AND pk.knowledge_type = 'battery'
        AND pk.title = 'Generic Hoverboard Battery and Charging Safety'
  );

-- Guide C: Not Charging Troubleshooting (Medium Risk)
INSERT INTO product_knowledge (
    product_id, 
    knowledge_type, 
    title, 
    content, 
    risk_level, 
    applies_to_channel, 
    human_review_required
) 
SELECT 
    p.product_id, 
    'charging', 
    'Generic Hoverboard Not Charging Troubleshooting', 
    'If the hoverboard is not charging: 1. Verify the charger adapter plug is firmly connected to both the wall socket and the hoverboard port. 2. Confirm the LED indicator light on the charger turns red (charging) or green (fully charged). 3. Inspect the charging port for any bent pins or dust. 4. If there are no signs of overheating, burning smell, smoke, sparks, swelling, liquid damage, or physical damage, leave it plugged in for up to 20 minutes to check whether the battery begins charging. 5. If there is overheating, burning smell, smoke, sparks, swelling, liquid damage, charger overheating, or visible battery damage, stop using the product and escalate for human review.', 
    'medium', 
    'all', 
    true
FROM products p
WHERE p.sku = 'HOVERBOARD-GENERIC-SUPPORT' 
  AND p.store_id = 'hoverboard_store'
  AND NOT EXISTS (
      SELECT 1 
      FROM product_knowledge pk 
      WHERE pk.product_id = p.product_id 
        AND pk.knowledge_type = 'charging'
        AND pk.title = 'Generic Hoverboard Not Charging Troubleshooting'
  );


-- =========================================================================
-- VERIFICATION QUERIES (Run these in Supabase SQL editor to verify)
-- =========================================================================
/*
-- Query 1: Verify the generic support product is active
SELECT * FROM products WHERE sku = 'HOVERBOARD-GENERIC-SUPPORT';

-- Query 2: Fetch the linked knowledge articles and check risk levels
SELECT pk.knowledge_id, p.sku, pk.knowledge_type, pk.title, pk.risk_level, pk.human_review_required
FROM product_knowledge pk
JOIN products p ON pk.product_id = p.product_id
WHERE p.sku = 'HOVERBOARD-GENERIC-SUPPORT';
*/
