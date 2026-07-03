# Product Support Passport — Template
## Hoverboard Store AI Support Agent — Phase 3A

**Version**: 1.0  
**Status**: Reusable Template — Do Not Edit Without Master Plan Approval  
**Last Updated**: 2026-07-03  
**Usage**: Copy this file, rename for the target product family, and fill in every section before any SQL seed is written.

---

> [!IMPORTANT]
> This template must be completed in full before any knowledge chunks are written for the target product.
> Do not leave any section as a placeholder. Every answer in this document will become a customer-facing reply.
> Inaccurate information here becomes inaccurate bot answers.

---

## Document Header

**Product Family Name**: [e.g. "6.5 Inch Hoverboard + Hoverkart Bundle"]  
**Product Type**: [e.g. "Electric Hoverboard / Hoverkart Combo"]  
**Passport Version**: v1  
**Author**: [name/date]  
**Reviewed By**: [name/date]  
**Status**: ❌ Draft / ⚠️ In Review / ✅ Approved  
**Passport File**: `PRODUCT_SUPPORT_PASSPORT_<PRODUCT_CODE>_V1.md`  
**Derived Knowledge SQL**: `backend/knowledge_pack_<product_code>_v2.sql` (created after passport is approved)

---

## Section A — Product Identity

> Provide all the ways customers refer to this product. This section drives keyword matching and ensures the bot recognises the product even when the customer uses incorrect or informal language.

### A1. Official Product Family Name
[e.g. "6.5 Inch Self-Balancing Hoverboard + Hoverkart Bundle"]

### A2. Product Type
[e.g. "Electric self-balancing hoverboard with optional hoverkart seat attachment"]

### A3. Known Aliases and Customer Wording
List all informal names customers use — even misspellings:
- [e.g. "hoverboard", "hover board", "hoverborad", "segway", "self balancing scooter", "balance board"]
- [e.g. "hoverkart", "hover kart", "kart attachment", "go kart attachment", "seat attachment"]

### A4. Related SKUs / Products Sold Together
- [e.g. SKU: HBS-6.5-BLK (black), HBS-6.5-WHT (white), HBS-6.5-KRT (bundle with hoverkart)]
- [e.g. Hoverkart sold separately: SKU HVK-001]

### A5. Where Sold
- Hoverboard Store UK website (hoverboardstore.co.uk)
- [Other channels if applicable]

### A6. Certifications
- [e.g. UKCA certified, CE certified, UL 2272 compliant]

---

## Section B — Pre-Sale Questions

> Fill in factual answers to the most common questions asked before purchase. These become `presale` knowledge chunks.

### B1. Age Suitability
**What age is this product suitable for?**

[e.g. "The 6.5 inch hoverboard is designed for riders aged 8 and above. For younger children aged 6–8, we recommend using it only under close adult supervision on a flat, smooth, private surface. We do not recommend hoverboards for children under 6. Parental discretion is required as suitability depends on the individual child's balance, coordination, and confidence."]

**Bot must NOT say**: specific minimum weight without confirming the spec. Do not invent weight limits.

### B2. Beginner Suitability
**Is this product suitable for a complete beginner?**

[e.g. "Yes. The 6.5 inch hoverboard includes learner mode and self-balancing sensors that make it suitable for first-time riders. We recommend practising in a wide, flat, open space on private land. Adult supervision is recommended for all first-time riders, especially children."]

### B3. Product Comparison — 6.5 vs 8.5 Inch
**What is the difference between the 6.5 inch and the 8.5 inch model?**

[e.g. "The 6.5 inch model is our standard hoverboard designed for smooth, flat surfaces — ideal for children and beginners. The 8.5 inch all-terrain model features larger wheels suitable for grass, gravel, and uneven outdoor terrain. If your child will be riding mainly indoors or on flat paths, the 6.5 inch is the better choice. For outdoor and off-road use, the 8.5 inch is recommended."]

### B4. Hoverboard vs Hoverkart Bundle
**What is a hoverkart? Do I need it?**

[e.g. "The hoverkart is a seat attachment that converts the hoverboard into a three-wheeled go-kart style ride. It is a popular choice for younger children who may find standing on the hoverboard difficult at first. The hoverkart bundle includes both the hoverboard and the hoverkart frame. The hoverboard can be used standalone or with the hoverkart attached."]

### B5. Birthday Gift Questions
**Is this a good birthday gift?**

[e.g. "The 6.5 inch hoverboard and hoverkart bundle is one of our most popular birthday and Christmas gifts. It comes packaged ready to gift. Please allow up to 3 business days for standard delivery, or select next-day delivery at checkout for orders placed before 2 PM GMT."]

### B6. Safety Expectations
**Is the hoverboard safe?**

[e.g. "Our hoverboards are UKCA and CE certified to UK safety standards. We recommend wearing a helmet and appropriate protective gear at all times. Hoverboards must be used on private land with the landowner's permission — they are not permitted on public roads, pavements, or cycle paths under UK law. Always read the safety guide included in the box before first use."]

---

## Section C — Setup and First Use

> These answers become `setup` and `charging` knowledge chunks.

### C1. Unboxing
**What is in the box?**

[List what is included: hoverboard, charger, safety guide, any accessories]

### C2. First Charge
**How do I charge it for the first time?**

[e.g. "Before first use, charge the hoverboard fully using the supplied charger. Connect the charger to a standard UK wall socket and to the charging port on the hoverboard. The charger LED will turn red when charging and green when fully charged. A full first charge typically takes [X] hours. Do not use the hoverboard until the first charge is complete. Do not leave charging overnight or unattended."]

### C3. Power On
**How do I turn it on?**

[e.g. "Press and hold the power button for 3 seconds until the lights turn on and the board beeps once. Place it on a flat surface before stepping on."]

### C4. First Ride
**What should I know before riding for the first time?**

[e.g. "Start on a flat, smooth, private surface. Step onto the board one foot at a time, keeping your weight centred. Lean slightly forward to move forward, and slightly backward to slow down or reverse. Do not make sharp or sudden movements until you are comfortable. Adult supervision is recommended."]

### C5. Calibration / Reset After First Use
**Do I need to calibrate it?**

[e.g. "The hoverboard should be pre-calibrated when it arrives. If the board tilts to one side during use, calibration may be required. See the Troubleshooting section for calibration steps."]

### C6. Safety Gear
**What safety gear do I need?**

[e.g. "We strongly recommend a helmet, knee pads, and elbow pads for all riders, especially children. Protective gear is not included in the box but is available from most sports retailers."]

### C7. UK Private Land Rule
**Where can the hoverboard be used?**

[e.g. "Under UK law, hoverboards and electric scooters are not permitted on public roads, pavements, or cycle paths. They may only be used on private land with the landowner's permission. Hoverboard Store UK follows UK safety guidelines and recommends using your hoverboard only in appropriate private spaces such as gardens, driveways, or private parks with permission."]

---

## Section D — Troubleshooting

> These answers become `troubleshooting`, `reset_guide`, and `charging` knowledge chunks.

### D1. Not Turning On
**My hoverboard won't turn on. What do I do?**

[Step-by-step: check charge, check power button hold duration, check charging port, etc. End with: "If none of these steps resolve the issue, contact contact@hoverboardstore.co.uk with your order number and a description of the fault."]

### D2. Charger Light Not Coming On
**The charger light is not turning on. What does this mean?**

[e.g. "Check that the charger is firmly connected to both the wall socket and the charging port. Check the charging port for bent pins or debris. If the charger light still does not illuminate after 2 minutes, the charger may be faulty. Do not attempt to use a third-party charger. Contact contact@hoverboardstore.co.uk with your order number."]

### D3. Charger Light Colours
**What do the charger light colours mean?**

[e.g. "Red: charging in progress. Green: fully charged. No light: check connection. If the light is red but does not turn green after the expected charge time, or if the charger feels hot, stop charging and contact support."]

### D4. Beeping / Flashing Lights
**The hoverboard is beeping / the lights are flashing. What does it mean?**

[e.g. "Beeping during use usually indicates the board needs calibration, or that the battery is low. To reset and calibrate: turn the board off, place it on a completely flat surface, hold the power button for 10 seconds until the lights flash, release, then turn it off and on again. If beeping persists after calibration and charging, contact contact@hoverboardstore.co.uk."]

### D5. Balance / Tilting to One Side
**The hoverboard is not balanced. It tilts to one side.**

[e.g. "This usually indicates the board needs calibration. Place the board on a completely flat surface and perform a calibration reset: turn off, hold power button 10 seconds, turn off, turn on. Avoid riding on uneven surfaces. If the tilting persists after calibration, this may indicate a motor or sensor fault — contact contact@hoverboardstore.co.uk."]

### D6. Bluetooth / Speaker Not Working
**The Bluetooth or speaker is not working.**

[Fill in steps: ensure pairing mode, correct device, etc. Note whether all models have Bluetooth or only specific SKUs.]

### D7. LED Lights Not Working
**The lights are not working.**

[Fill in steps: check power, check any settings, note whether lights are a known feature of this model.]

### D8. Battery Not Lasting
**The battery runs out quickly.**

[e.g. "Battery life depends on rider weight, terrain, speed, and ambient temperature. Cold weather can reduce battery performance. If the battery drains very quickly even on a short ride (e.g. less than 15 minutes), this may indicate a battery issue. Contact contact@hoverboardstore.co.uk with your order number and a description."]

### D9. Hoverkart Fitting Issue
**I can't attach the hoverkart / it keeps falling off.**

[Fill in: attachment steps, check for compatibility, which models the hoverkart is compatible with. Note if hoverkart is universal or specific.]

---

## Section E — High-Risk Safety Escalation

> These answers become `battery_safety` knowledge chunks with `risk_level = "high"`. Every query matching any of these topics must trigger immediate escalation. No auto-reply with these.

> [!CAUTION]
> The bot must NEVER attempt to troubleshoot a high-risk safety event. The only permitted response is the stop-use safety message followed by immediate human escalation.

### E1. Burning Smell / Smoke / Sparks
**Trigger phrases**: "smells burning", "smoke", "sparks", "catching fire", "on fire", "smells weird", "unusual smell", "smells hot"

**Required bot response** (exact wording to use in knowledge chunk):

"Please stop using the hoverboard immediately. Do not charge it again. If it is safe to do so, unplug it from the power source and move it away from flammable materials. Do not attempt to repair the battery or charger yourself. Our support team has been notified and will reply here shortly. You can also contact contact@hoverboardstore.co.uk."

### E2. Overheating
**Trigger phrases**: "getting very hot", "overheating", "hot to touch", "burning hot", "too hot"

**Required bot response** (same as E1 — use same knowledge chunk or a linked one):

[Same as E1 response]

### E3. Swollen / Puffy Battery
**Trigger phrases**: "battery looks swollen", "battery is puffy", "battery looks different", "bulging"

**Required bot response**:

[Same as E1 response. Add: "A swollen or deformed battery is a serious safety risk. Do not attempt to puncture, press, or dispose of it in normal household waste. Contact your local hazardous waste authority for safe disposal guidance."]

### E4. Water Damage
**Trigger phrases**: "got wet", "water damage", "rained on", "dropped in water", "flooded"

**Required bot response**:

"Please do not attempt to charge or power on the hoverboard if it has been exposed to water. Water damage to electronics can cause a short circuit and fire risk. Leave it powered off in a dry area and contact contact@hoverboardstore.co.uk with your order number and details of the water exposure. Do not attempt to dry it with a hairdryer or heat source."

### E5. Visible Charger / Battery Damage
**Trigger phrases**: "charger is broken", "charger looks damaged", "wire is exposed", "cable is frayed", "battery looks cracked"

**Required bot response**:

"Please stop using the charger or hoverboard immediately if there is any visible damage to the charger cable, plug, or battery casing. Using damaged charging equipment is a fire and shock risk. Contact contact@hoverboardstore.co.uk with your order number and photographs of the damage."

---

## Section F — Returns and Warranty

> These answers become `return_warranty` knowledge chunks.

### F1. 30-Day Return Policy
**How do I return my hoverboard?**

[e.g. "We offer a 30-day return policy for unused items in their original packaging. To start a return, contact contact@hoverboardstore.co.uk with your order number and reason for return. We will provide return instructions. Items must be returned in their original condition and packaging. Return postage costs may apply for non-faulty items."]

### F2. 12-Month Warranty Scope
**What does the warranty cover?**

[e.g. "Our hoverboards come with a 12-month manufacturer warranty from the date of purchase. The warranty covers manufacturing faults, battery defects (excluding misuse), and technical failures under normal use."]

### F3. What Warranty Does NOT Cover
**What is not covered by the warranty?**

[e.g. "The warranty does not cover: physical damage caused by impact or misuse, water damage, damage caused by using non-approved chargers, damage caused by modifications, or normal wear and tear. Warranty claims for physical damage require photographic evidence."]

### F4. Evidence Required for Warranty Claim
**What do I need to make a warranty claim?**

[e.g. "To make a warranty claim, please email contact@hoverboardstore.co.uk with: your order number, a description of the fault, photographs or a short video showing the issue, and confirmation of when the issue started. Our team will assess the claim and respond within [X] business days."]

### F5. When Human Approval Is Required
The following situations require a human agent to review before any return, replacement, or refund action is taken:

- Customer reports physical damage alongside a warranty claim
- Customer requests a refund (not a return — refunds require Shopify order verification)
- Customer reports a safety incident (battery/fire — these are also Section E escalations)
- Customer disputes the warranty decision
- Replacement request for an order over [£X value threshold — confirm with store]

> [!WARNING]
> The bot must NEVER approve a refund, replacement, or return label without a human agent reviewing the case first.

---

## Section G — Case Intake

> This section defines what information the bot must collect before a support case is created. These become `case_intake` knowledge chunks and drive the conversation flow for escalated queries.

### G1. Required Fields for a Support Case

Before creating any support case or escalating to a human agent, the bot should collect:

| Field | Required? | Example |
| :--- | :--- | :--- |
| Order number | ✅ Yes | "HBS-12345" or Shopify order number |
| Customer email | ✅ Yes | Used for verification |
| Customer postcode | As backup if email unavailable | "M1 1AA" |
| Product name | ✅ Yes | "6.5 inch hoverboard", "bundle with hoverkart" |
| Issue description | ✅ Yes | "won't turn on", "smells burning" |
| Charger light colour | For charging issues | "red", "green", "no light" |
| When issue started | ✅ Yes | "yesterday", "after first charge", "since new" |
| Photos or video | For physical damage, safety events | "customer will email" |
| Safety check | For battery/fire events | "is it plugged in?", "is it in a safe place?" |

### G2. Recommended Dashboard Case Types

| Situation | Recommended Case Type |
| :--- | :--- |
| Not turning on (after basic troubleshooting fails) | `Stopped Working Report` |
| Charging fault | `Charging Issue Report` |
| Physical damage | `Damaged Item` |
| Missing part | `Missing Part` |
| Wrong item received | `Wrong Item Received` |
| Return request | `Return Request` |
| Warranty fault (non-safety) | `Warranty Fault` |
| Battery/fire/safety event | `Safety Escalation` — highest priority |

---

## Section H — Bot Behaviour Rules

> These rules govern what the bot is and is not allowed to do for this product family. They are enforced in `support_brain.py`.

### H1. Allowed Bot Answers
- Pre-sale product information (age, size, features) — from Section B chunks
- Setup and first use guidance — from Section C chunks
- Troubleshooting steps from Section D — only for low/medium risk issues
- Delivery and return policy answers — from Section F chunks
- Directing to contact@hoverboardstore.co.uk with order number for any unresolved issue

### H2. Forbidden Bot Answers
- The bot must NOT approve refunds, returns, or replacements
- The bot must NOT invent specifications (speed, weight limit, battery capacity) not in the passport
- The bot must NOT advise on third-party charger compatibility
- The bot must NOT advise on using hoverboards on public roads or pavements
- The bot must NOT minimise or dismiss a safety concern
- The bot must NOT tell a customer to wait if they have reported smoke, fire, or burning smell

### H3. When to Escalate (Trigger Escalation)
- Any safety event: smoke, fire, burning smell, sparks, overheating, swollen battery, water damage
- Explicit request to speak to a human
- Order-specific queries requiring verification (order status, tracking, cancellation, refund)
- Warranty disputes or replacement requests where human review is required (Section F5)
- Any fault that cannot be resolved by the troubleshooting steps in Section D

### H4. When to Create a Case
- After collecting all required fields from Section G1
- When a troubleshooting attempt fails and the issue requires staff review
- For any physical damage, missing part, or wrong item query

### H5. When Shopify Order Lookup Is Required
- Customer asks for tracking information
- Customer requests cancellation
- Customer requests a refund (requires order verification first)
- Warranty claim where purchase date needs to be confirmed

> [!NOTE]
> Shopify order lookup is a Phase 4 feature. Until Phase 4 is live, the bot must ask the customer to provide their order number and email, then escalate to a human agent for verification.
