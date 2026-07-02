# MiniMax AI Support Brain Integration Plan

This document outlines the architecture, routing constraints, safety rules, fallback mechanisms, and future roadmaps for the MiniMax AI Support Brain layer in customer support.

---

## 1. Scope & Capabilities
The Support Brain operates as a hybrid classification, safety validation, and text generation system:

*   **MiniMax AI Processing**: If a customer queries standard/non-risky topics, the Support Brain uses MiniMax completions to answer conversationally using the matching knowledge base context and chronological chat history.
*   **Allowed Topics (Auto-Answers)**:
    *   General shipping times and delivery policy questions.
    *   General return, exchange, and refund window guidelines.
    *   Standard battery safety basics (handling, ventilation, certified chargers).
    *   Standard reset, calibration, and beeping troubleshoot guidelines.
    *   Product suitability, recommendations, and age constraints.
    *   Discounts, coupons, promotional codes, and signups.
    *   Manufacturer warranty terms and diagnostic timelines.

---

## 2. Safety Routing (Forced Escalations)
To protect customer safety and avoid hallucinating transaction parameters, the system triggers **immediate human escalation** (forced transfer) if any high-risk category or terms match the safety router rules.

*   **Risk Classifications (Immediate Transfer)**:
    *   **Safety Danger**: Terms matching heat, melting, burning smells, smoke, fire, sparks, explosions, battery swelling, or sparks.
    *   **Legal Threat**: Customer mentioning suing, legal, lawyers, trading standards, or solicitors.
    *   **Billing/Payments**: Double-charges, checkout failures, declined credit cards, chargebacks, Stripe/PayPal issues.
    *   **Order-Specific Tracking**: Requests asking "where is my order" or tracking specific order IDs/postcodes (delegated to agents until official Shopify Admin API lookups are established).
    *   **Defective/Damaged Claims**: Reports of cracked, broken, faulty, scratched, or shattered items.
    *   **Angry Complaints**: Angry or abusive remarks, scam allegations, and extreme customer dissatisfaction.
    *   **Human Request**: Explicit customer requests to "speak to a human/agent/person/customer support".

---

## 3. Fallback Mechanics
To guarantee absolute robustness in live production:
1.  **Missing API Key**: If `MINIMAX_API_KEY` is not set in the environment, the brain falls back to local rules-based keyword matching (matching local JSON articles).
2.  **API Call Failures**: If the MiniMax API returns a non-200 code, times out, or encounters a connection issue, it catches the error and serves the matching local knowledge base article or the default escalation warning without crashing the API.
3.  **Output Safety Check**: If the generated MiniMax response contains any high-risk words (e.g., "smoke", "fire", "burning"), it blocks the text from being sent to the customer and instantly replaces it with the human escalation message.

---

## 4. Environment Variables Mappings
Add these to the backend `.env` file:
```bash
# MiniMax AI Support Brain Credentials
MINIMAX_API_KEY=your-secure-minimax-api-key
MINIMAX_MODEL=abab6.5g-chat
```

---

## 5. Future Shopify Order Lookup Integration
When the Shopify Admin API credentials are safe to store:
1.  **Intent Capture**: Detect `order_tracking` intent.
2.  **Verification**: Ask the customer to input their Order ID and Billing Postcode/Email.
3.  **API Query**: Query the Shopify Admin API `/orders.json` endpoint to fetch status and shipping carrier metadata.
4.  **Auto-Reply**: Feed order status details back to MiniMax to generate a personalized tracking answer, or transfer to an agent if delayed/missing.
