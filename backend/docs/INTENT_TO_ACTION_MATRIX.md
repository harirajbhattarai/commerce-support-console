# Intent-to-Action Matrix
## Hoverboard Store AI Support Agent

This matrix defines the complete routing and action rules for every supported customer intent.
Any intent not listed here must be routed as `unknown_general` until it is formally defined and added.

**Routes**:
- `answer` — Bot replies directly from knowledge base or rules
- `verify` — Bot requests order/customer verification before proceeding
- `collect_details` — Bot asks structured intake questions to capture case details
- `create_case` — Bot creates a structured support case record
- `escalate` — Bot transfers to human agent with holding message

**Dashboard Status Mapping**:
- `auto_replied` — Route was `answer` and reply was sent successfully
- `in_progress` — Staff has opened the conversation
- `needs_escalation` (UI: "Needs Agent") — Route was `escalate`
- `resolved` — Conversation closed

---

## 1. product_recommendation

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "which one should i get", "what hoverboard do you recommend", "best one for beginners", "im not sure what to buy", "whats good for a gift", "which is most popular" |
| **Expected Route** | `answer` |
| **Risk Level** | low |
| **Required Knowledge** | product_knowledge — beginner models, feature comparison |
| **Required Shopify Data** | None |
| **Allowed Action** | Reply with product guidance |
| **Forbidden Action** | Do not escalate, do not ask for order number |
| **Human Approval Rule** | None required |
| **Ideal Response Style** | Friendly, specific — recommend 6.5 inch for beginners, mention G1 Lite for kids, 8.5 for off-road |
| **Dashboard Status** | `auto_replied` |

---

## 2. age_suitability

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "my son is 7 can he use it", "is it safe for a 5 year old", "what age is ok", "my daughter is 9 years old which one", "is there a minimum age", "too young for hoverboard" |
| **Expected Route** | `answer` |
| **Risk Level** | low |
| **Required Knowledge** | product_knowledge — age/weight guidelines |
| **Required Shopify Data** | None |
| **Allowed Action** | Reply with age/weight guidance and safety note |
| **Forbidden Action** | Do not guarantee suitability for specific child — add disclaimer |
| **Human Approval Rule** | None required |
| **Ideal Response Style** | Helpful with clear safety caveat: "suitability depends on individual coordination and weight" |
| **Dashboard Status** | `auto_replied` |

---

## 3. size_guidance_6_5_vs_8_5

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "whats the difference between 6.5 and 8.5", "is bigger better", "which size for indoor", "8.5 too big?", "6.5 for outdoor?", "which wheel size is off road" |
| **Expected Route** | `answer` |
| **Risk Level** | low |
| **Required Knowledge** | product_knowledge — size comparison |
| **Required Shopify Data** | None |
| **Allowed Action** | Reply with size guidance |
| **Forbidden Action** | Do not escalate |
| **Human Approval Rule** | None required |
| **Ideal Response Style** | Clear table-style comparison: 6.5 = smooth surfaces/beginners, 8.5 = off-road/grass/rough terrain |
| **Dashboard Status** | `auto_replied` |

---

## 4. hoverkart_guidance

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "what is a hoverkart", "does the kart work with all boards", "is the kart included", "how do i attach the kart", "can i buy kart separately", "kart bundle what does it come with" |
| **Expected Route** | `answer` |
| **Risk Level** | low |
| **Required Knowledge** | product_knowledge — hoverkart compatibility, bundles |
| **Required Shopify Data** | None |
| **Allowed Action** | Reply with hoverkart guidance |
| **Forbidden Action** | Do not escalate |
| **Human Approval Rule** | None required |
| **Ideal Response Style** | Explain bundle contents and compatibility. Mention G1 Lite hoverkart bundle for kids. |
| **Dashboard Status** | `auto_replied` |

---

## 5. delivery_general

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "how long does delivery take", "when will it arrive", "do you do next day", "is delivery free", "standard shipping time", "how long uk delivery", "can i get it tomorrow" |
| **Expected Route** | `answer` |
| **Risk Level** | low |
| **Required Knowledge** | support_articles — delivery policy |
| **Required Shopify Data** | None |
| **Allowed Action** | Reply with delivery policy |
| **Forbidden Action** | Do not escalate. Do not promise specific delivery dates. |
| **Human Approval Rule** | None required |
| **Ideal Response Style** | "Standard shipping: 2-3 business days, free UK delivery. Next-day available before 2 PM GMT." |
| **Dashboard Status** | `auto_replied` |

---

## 6. order_tracking

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "where is my order", "whats my tracking number", "my parcel hasnt arrived", "when will my order get here", "i ordered 3 days ago nothing", "tracking not updating", "order number 12345 where is it" |
| **Expected Route** | `verify` then `answer` (Phase 4+) |
| **Risk Level** | medium |
| **Required Knowledge** | support_articles — delivery timescales |
| **Required Shopify Data** | Order status, fulfilment status, tracking number (Phase 4+) |
| **Allowed Action** | Collect order number + email/postcode, retrieve status, provide tracking info |
| **Forbidden Action** | Do not provide order data without verification. Do not promise delivery date. |
| **Human Approval Rule** | Escalate if tracking shows "returned to sender" or "lost in transit" |
| **Ideal Response Style** | "Please provide your order number and email so I can check the status for you." |
| **Dashboard Status** | `needs_escalation` pre-Phase 4. `auto_replied` post-Phase 4 if verified. |

---

## 7. return_policy

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "can i return it", "what is your returns policy", "how do i send it back", "30 day return", "i dont want it anymore", "can i get a refund if i change my mind" |
| **Expected Route** | `answer` |
| **Risk Level** | low |
| **Required Knowledge** | support_articles — 30-day return policy |
| **Required Shopify Data** | None |
| **Allowed Action** | Reply with return policy |
| **Forbidden Action** | Do not approve return or initiate refund |
| **Human Approval Rule** | None required for policy info |
| **Ideal Response Style** | "We offer a 30-day return policy for unused items in original packaging. Email contact@hoverboardstore.co.uk to start your return." |
| **Dashboard Status** | `auto_replied` |

---

## 8. return_request

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "i want to return my hoverboard", "can you start a return for me", "i need to send it back", "i changed my mind after buying", "please process my return", "how do i get a refund" |
| **Expected Route** | `collect_details` then `create_case` (Phase 5+) |
| **Risk Level** | medium |
| **Required Knowledge** | support_articles — return policy, return packaging |
| **Required Shopify Data** | Order number + product purchased (Phase 4+) |
| **Allowed Action** | Collect order number, reason, condition. Create return case. Provide instructions. |
| **Forbidden Action** | Do not approve refund. Do not issue return label without staff review. |
| **Human Approval Rule** | Staff must review and approve return case before confirming to customer |
| **Ideal Response Style** | Collect details, create case, advise return steps, confirm case reference number |
| **Dashboard Status** | `needs_escalation` |

---

## 9. warranty_policy

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "how long is the warranty", "what does warranty cover", "is my board still under warranty", "warranty details", "12 month warranty?" |
| **Expected Route** | `answer` |
| **Risk Level** | low |
| **Required Knowledge** | support_articles — 12-month warranty policy |
| **Required Shopify Data** | None |
| **Allowed Action** | Reply with warranty policy |
| **Forbidden Action** | Do not approve warranty claim |
| **Human Approval Rule** | None required for policy info |
| **Ideal Response Style** | "Our hoverboards come with a 12-month warranty covering manufacturing faults. Physical damage is not covered." |
| **Dashboard Status** | `auto_replied` |

---

## 10. warranty_fault

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "my board stopped working after 2 months", "warranty claim", "its broken and i bought it in january", "i think its a manufacturing fault", "it failed within warranty period", "stopped working 3 months after buying" |
| **Expected Route** | `collect_details` then `create_case` (Phase 5+) |
| **Risk Level** | medium |
| **Required Knowledge** | support_articles — warranty fault documentation |
| **Required Shopify Data** | Order number, order date, product purchased (Phase 4+) |
| **Allowed Action** | Collect fault description and evidence. Create warranty fault case. |
| **Forbidden Action** | Do not approve replacement or refund. Do not make warranty decision. |
| **Human Approval Rule** | Staff must assess warranty fault case and approve action |
| **Ideal Response Style** | Collect details systematically, create case, advise customer of next steps |
| **Dashboard Status** | `needs_escalation` |

---

## 11. stopped_working

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "my hoverboard stopped working", "it just died", "it wont work anymore", "if it stops working what do i do", "it just stopped mid ride", "completely dead now" |
| **Expected Route** | `answer` with troubleshooting, then escalate if not resolved |
| **Risk Level** | low-medium |
| **Required Knowledge** | support_articles — stopped working, charging check, reset steps |
| **Required Shopify Data** | None |
| **Allowed Action** | Provide troubleshooting steps. If issue persists, collect details and escalate. |
| **Forbidden Action** | Do not approve replacement or refund. Do not diagnose remotely beyond basic steps. |
| **Human Approval Rule** | None for troubleshooting. Human required if fault persists. |
| **Ideal Response Style** | Step-by-step: check charge, try reset, check for safety issues. If none resolve, escalate. |
| **Dashboard Status** | `auto_replied` for first pass. `needs_escalation` if customer confirms issue persists. |

---

## 12. not_turning_on

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "hoverboard not turning on", "wont switch on", "power button not working", "press power nothing happens", "dead wont start", "not powering up" |
| **Expected Route** | `answer` with reset/charge steps |
| **Risk Level** | low |
| **Required Knowledge** | support_articles — reset/calibration, charging check |
| **Required Shopify Data** | None |
| **Allowed Action** | Provide reset and charge check steps |
| **Forbidden Action** | Do not escalate immediately without providing troubleshooting first |
| **Human Approval Rule** | None for troubleshooting |
| **Ideal Response Style** | Provide calibration steps. Check if red light flashing. Advise charge first. |
| **Dashboard Status** | `auto_replied` |

---

## 13. charging_issue

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "charger light not coming on", "not charging", "wont charge", "green light immediately", "charger getting hot", "charging port not working", "how long to charge", "blinks when charging" |
| **Expected Route** | `answer` with charging steps. Escalate if heat/smoke present. |
| **Risk Level** | low (no heat/smoke) / high (heat/smoke/sparks) |
| **Required Knowledge** | support_articles — charging guide |
| **Required Shopify Data** | None |
| **Allowed Action** | Provide charging troubleshooting. If heat/smoke/sparks: immediate safety guidance + escalate |
| **Forbidden Action** | Do not advise ignoring heat or sparks |
| **Human Approval Rule** | Escalate all heat/spark/smoke charging issues to human |
| **Ideal Response Style** | Step-by-step charging check. Safety bifurcation for heat/smoke. |
| **Dashboard Status** | `auto_replied` (no safety risk) / `needs_escalation` (heat/smoke present) |

---

## 14. reset_calibration

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "how do i reset it", "needs calibration", "beeping and flashing", "red light flashing", "how to recalibrate", "balance mode not working", "spinning in circles" |
| **Expected Route** | `answer` |
| **Risk Level** | low |
| **Required Knowledge** | support_articles — reset/calibration steps |
| **Required Shopify Data** | None |
| **Allowed Action** | Provide reset steps |
| **Forbidden Action** | Do not escalate for simple reset queries |
| **Human Approval Rule** | None |
| **Ideal Response Style** | Numbered reset steps: flat surface, hold power 10 sec, turn off, turn on. |
| **Dashboard Status** | `auto_replied` |

---

## 15. battery_safety_high_risk

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "my board smells burning", "smoke coming from battery", "catching fire", "sparks from charger", "battery swelling", "overheating", "battery getting very hot", "i think its going to catch fire" |
| **Expected Route** | `escalate` — IMMEDIATELY |
| **Risk Level** | **HIGH** |
| **Required Knowledge** | Hardcoded safety guidance — no knowledge lookup required |
| **Required Shopify Data** | None |
| **Allowed Action** | Return immediate safety instructions. Mark `needs_escalation`. Notify human agent. |
| **Forbidden Action** | Never delay safety guidance. Never provide DIY battery repair advice. Never downgrade to `auto_replied`. |
| **Human Approval Rule** | Human agent must review and follow up within 1 hour |
| **Ideal Response Style** | "Please stop using the hoverboard immediately. Do not charge it again. If it is safe, unplug it and keep it away from flammable materials. Do not attempt to repair the battery or charger yourself. Our support team has been notified and will reply here shortly. You can also contact contact@hoverboardstore.co.uk." |
| **Dashboard Status** | `needs_escalation` |

---

## 16. damaged_on_arrival

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "arrived damaged", "box was crushed", "arrived broken", "screen cracked on delivery", "damaged when i opened it", "item damaged in post" |
| **Expected Route** | `collect_details` then `create_case` (Phase 5+) |
| **Risk Level** | medium |
| **Required Knowledge** | support_articles — damaged on arrival guidance |
| **Required Shopify Data** | Order number, product purchased (Phase 4+) |
| **Allowed Action** | Ask for photos, order number, description. Create DOA case. |
| **Forbidden Action** | Do not promise replacement or refund. Do not dismiss without case. |
| **Human Approval Rule** | Staff must review DOA evidence and approve replacement/refund |
| **Ideal Response Style** | Empathetic, collect evidence promptly, create case reference |
| **Dashboard Status** | `needs_escalation` |

---

## 17. missing_part

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "charger not in box", "missing charger", "no manual included", "parts missing", "kart attachment not in package", "only got one wheel pad" |
| **Expected Route** | `collect_details` then `create_case` (Phase 5+) |
| **Risk Level** | medium |
| **Required Knowledge** | support_articles — missing parts guidance |
| **Required Shopify Data** | Order number, product purchased (Phase 4+) |
| **Allowed Action** | Collect order number and missing part details. Create missing part case. |
| **Forbidden Action** | Do not promise dispatch without staff confirmation |
| **Human Approval Rule** | Staff must confirm and dispatch missing part |
| **Ideal Response Style** | Apologise, confirm order details, create case, advise next steps |
| **Dashboard Status** | `needs_escalation` |

---

## 18. wrong_item

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "received wrong colour", "got the wrong model", "sent wrong hoverboard", "i ordered 8.5 got 6.5", "this isnt what i ordered", "wrong item in box" |
| **Expected Route** | `collect_details` then `create_case` (Phase 5+) |
| **Risk Level** | medium |
| **Required Knowledge** | support_articles — wrong item guidance |
| **Required Shopify Data** | Order number, product ordered, product received (Phase 4+) |
| **Allowed Action** | Collect order number and photo evidence. Create wrong item case. |
| **Forbidden Action** | Do not send replacement without staff approval |
| **Human Approval Rule** | Staff must confirm and arrange exchange or return |
| **Ideal Response Style** | Apologise, collect evidence, create case, advise return and exchange steps |
| **Dashboard Status** | `needs_escalation` |

---

## 19. cancel_order

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "cancel my order", "i want to cancel", "please cancel order 12345", "changed my mind cancel", "stop the order", "i dont want it anymore cancel" |
| **Expected Route** | `verify` then `escalate` |
| **Risk Level** | high |
| **Required Knowledge** | None |
| **Required Shopify Data** | Order status (Phase 4+) — cannot cancel if already dispatched |
| **Allowed Action** | Verify identity. Escalate to human with full context. |
| **Forbidden Action** | **Never cancel an order automatically.** No write actions. |
| **Human Approval Rule** | Human must action any cancellation |
| **Ideal Response Style** | "To process a cancellation, please provide your order number and email. I'll pass this to our team immediately." |
| **Dashboard Status** | `needs_escalation` |

---

## 20. change_address

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "change my delivery address", "i put wrong address", "update shipping address", "wrong postcode on order", "can you change where its going" |
| **Expected Route** | `verify` then `escalate` |
| **Risk Level** | high |
| **Required Knowledge** | None |
| **Required Shopify Data** | Order status — cannot change if dispatched |
| **Allowed Action** | Verify identity. Escalate immediately. |
| **Forbidden Action** | **Never change an address automatically.** |
| **Human Approval Rule** | Human must make any address change in Shopify admin |
| **Ideal Response Style** | "Please provide your order number and email. Address changes must be actioned by our team and may not be possible if already dispatched." |
| **Dashboard Status** | `needs_escalation` |

---

## 21. discount_question

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "do you have discount codes", "any vouchers", "10% off newsletter", "student discount", "sale on?", "promo code", "can i get a discount" |
| **Expected Route** | `answer` |
| **Risk Level** | low |
| **Required Knowledge** | support_articles — discount/newsletter offer |
| **Required Shopify Data** | None |
| **Allowed Action** | Mention newsletter 10% offer. Do not generate custom codes. |
| **Forbidden Action** | Do not create discount codes. Do not promise a discount beyond newsletter offer. |
| **Human Approval Rule** | None |
| **Ideal Response Style** | Mention sign-up to newsletter for 10% off first order. |
| **Dashboard Status** | `auto_replied` |

---

## 22. human_request

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "can i speak to someone", "i want to talk to a human", "get me a real person", "i need a human", "stop giving me bot answers", "speak to customer service", "i want to talk to a person" |
| **Expected Route** | `escalate` |
| **Risk Level** | medium |
| **Required Knowledge** | None |
| **Required Shopify Data** | None |
| **Allowed Action** | Acknowledge request, escalate with holding message |
| **Forbidden Action** | Do not continue answering as bot after explicit human request |
| **Human Approval Rule** | Human agent must pick up within reasonable time |
| **Ideal Response Style** | "Of course. I've passed this conversation to our support team. A team member will reply here shortly. You can also email contact@hoverboardstore.co.uk." |
| **Dashboard Status** | `needs_escalation` |

---

## 23. complaint

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "this is disgusting service", "absolute rubbish", "i want to make a complaint", "your customer service is terrible", "im going to report you", "trading standards", "this is unacceptable" |
| **Expected Route** | `escalate` |
| **Risk Level** | high |
| **Required Knowledge** | None |
| **Required Shopify Data** | None |
| **Allowed Action** | Acknowledge, apologise, escalate immediately |
| **Forbidden Action** | Do not argue. Do not dismiss. Do not auto-reply with generic response. |
| **Human Approval Rule** | Human must handle all formal complaints |
| **Ideal Response Style** | Brief, empathetic acknowledgement, escalate: "I'm sorry to hear this. I'm passing you directly to a senior team member now." |
| **Dashboard Status** | `needs_escalation` |

---

## 24. unknown_general

| Field | Value |
| :--- | :--- |
| **Messy Examples** | "hello", "hi there", "what can you do", "are you open", "can i ask a question", "do you sell spare parts", "question about my order" |
| **Expected Route** | `answer` with a general greeting or topic prompt |
| **Risk Level** | low |
| **Required Knowledge** | General store introduction |
| **Required Shopify Data** | None |
| **Allowed Action** | Respond with friendly greeting and list of topics bot can help with |
| **Forbidden Action** | Do not escalate unknown_general unless customer follows with a high-risk query |
| **Human Approval Rule** | None |
| **Ideal Response Style** | "Hi! I'm the Hoverboard Store support assistant. I can help with product advice, delivery, returns, warranties, and technical issues. What can I help you with today?" |
| **Dashboard Status** | `auto_replied` |
