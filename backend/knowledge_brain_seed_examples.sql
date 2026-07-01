-- =========================================================================
-- KNOWLEDGE BRAIN SAMPLE SEED EXAMPLES
-- =========================================================================
-- WARNING: This seed script is optional and intended for local development
-- and staging testing only. DO NOT run this on a production database 
-- unless specifically reviewed and approved.
-- =========================================================================

-- 1. Insert Hoverboard Product Example
INSERT INTO products (store_id, channel, sku, asin, product_title, brand, category, product_type, key_specs, status)
VALUES (
    'hoverboard_store', 
    'shopify', 
    'HB-V1-BLK', 
    'B08EXAMPLE1', 
    'AeroGlide Hoverboard V1 - Black', 
    'AeroGlide', 
    'Outdoors', 
    'hoverboard', 
    '{"battery": "36V 4.0Ah Li-ion", "motor": "250W Dual Motors", "max_speed": "12 km/h"}'::jsonb, 
    'active'
) ON CONFLICT (store_id, sku) DO NOTHING;

-- 2. Insert Hoverboard Product Knowledge (Calibration Reset & Battery Safety)
INSERT INTO product_knowledge (product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required)
SELECT 
    product_id, 
    'reset_guide', 
    'Hoverboard Calibration & Reset Guide', 
    'To calibrate: 1. Place the hoverboard on a completely flat, level surface. 2. Ensure the board is powered off. 3. Press and hold the power button down for 10 seconds. You will hear a beep and see the indicator lights flash. 4. Release the button and turn the board off. 5. Turn it back on to complete calibration.', 
    'low', 
    'all', 
    false
FROM products WHERE sku = 'HB-V1-BLK' AND store_id = 'hoverboard_store'
ON CONFLICT DO NOTHING;

INSERT INTO product_knowledge (product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required)
SELECT 
    product_id, 
    'battery', 
    'Hoverboard Battery and Charging Safety Guide', 
    'Always charge your hoverboard on a hard, flat surface in a well-ventilated room. Do not leave the hoverboard charging unattended or overnight. Only use the UL-certified charger provided with your purchase. If the board becomes hot, emits a smell, smoke, or is deformed, disconnect the power immediately, move it away from flammable objects, and do not use.', 
    'high', 
    'all', 
    true
FROM products WHERE sku = 'HB-V1-BLK' AND store_id = 'hoverboard_store'
ON CONFLICT DO NOTHING;


-- 3. Insert Aroma Diffuser Product Example
INSERT INTO products (store_id, channel, sku, asin, product_title, brand, category, product_type, key_specs, status)
VALUES (
    'aroma_haven', 
    'shopify', 
    'DF-ZEN-WHT', 
    'B08EXAMPLE2', 
    'ZenMist Ultrasonic Aroma Diffuser', 
    'ZenMist', 
    'Home & Kitchen', 
    'diffuser', 
    '{"capacity": "300ml", "run_time": "10 hours", "led_modes": 7}'::jsonb, 
    'active'
) ON CONFLICT (store_id, sku) DO NOTHING;

-- 4. Insert Aroma Diffuser Product Knowledge (Usage Instructions & Pet Safety)
INSERT INTO product_knowledge (product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required)
SELECT 
    product_id, 
    'usage', 
    'ZenMist Diffuser Usage Guide', 
    'Fill the water tank up to the max line (300ml). Add 3-5 drops of pure essential oil. Do not overfill or add oil while the device is running. Clean the water tank once a week using warm water and a small amount of neutral detergent to prevent oil buildup.', 
    'low', 
    'all', 
    false
FROM products WHERE sku = 'DF-ZEN-WHT' AND store_id = 'aroma_haven'
ON CONFLICT DO NOTHING;

INSERT INTO product_knowledge (product_id, knowledge_type, title, content, risk_level, applies_to_channel, human_review_required)
SELECT 
    product_id, 
    'safety', 
    'Pet Safety and Essential Oils Guide', 
    'Keep diffusers out of reach of cats and dogs as some essential oils (such as tea tree, eucalyptus, and peppermint) can be toxic to pets if inhaled or ingested in high concentrations. Ensure the room is well-ventilated.', 
    'low', 
    'all', 
    false
FROM products WHERE sku = 'DF-ZEN-WHT' AND store_id = 'aroma_haven'
ON CONFLICT DO NOTHING;
