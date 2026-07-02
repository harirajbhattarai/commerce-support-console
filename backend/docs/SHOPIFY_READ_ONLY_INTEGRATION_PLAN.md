# Shopify Read-Only Integration Plan
## Phase 4 — Hoverboard Store AI Support Agent

> [!IMPORTANT]
> This plan covers Phase 4 scope only: **read-only order data retrieval**.
> No write operations. No refunds. No cancellations. No address changes.
> These are Phase 6 considerations and require the human approval system first.

---

## Objective

Allow the support bot to retrieve Shopify order data to:
1. Verify a customer's identity against their order
2. Provide accurate order status and tracking information
3. Confirm product purchased for case intake (warranty, return, wrong item)

---

## API Scope Required

Request a **Custom App** token from Shopify Partner admin with the following scopes ONLY:

| Scope | Purpose |
| :--- | :--- |
| `read_orders` | Read order status, line items, fulfilment |
| `read_fulfillments` | Read tracking numbers and carrier |
| `read_shipping` | Read shipping method |

**Explicitly NOT requested:**
- `write_orders`
- `write_fulfillments`
- `read_customers` (PII concern — use only what is embedded in order)
- `write_customers`
- `read_payment_details`
- `write_discounts`

---

## Data Fields Permitted for Bot Access

| Field | Used For |
| :--- | :--- |
| `order_number` | Customer verification |
| `financial_status` | Confirm if paid |
| `fulfillment_status` | Confirmed / Dispatched / Delivered |
| `tracking_number` | Customer tracking |
| `tracking_company` | Carrier name |
| `line_items[].name` | Product purchased |
| `line_items[].quantity` | Quantity ordered |
| `created_at` | Order date — warranty eligibility |
| `shipping_lines[].title` | Shipping method |

**Never exposed to customer by bot:**
- Full delivery address
- Payment method or card details
- Other customer's order data
- Internal Shopify admin notes

---

## Customer Verification Flow

```
Customer: "where is my order"
Bot: "I can look that up for you.
      Please share your order number and the email address or postcode on the order."

Customer provides: order #1234 + email or postcode
Bot → Shopify API: GET /admin/api/2024-01/orders.json?name=#1234
Bot verifies: Does email or postcode in the order match what customer provided?

  ├── MATCH: Provide order status and tracking
  └── NO MATCH: "I couldn't verify that order with those details.
                  Please check your confirmation email or contact us at contact@hoverboardstore.co.uk."

Bot: 3 attempts allowed. On 3rd fail → escalate to human.
```

---

## New Module: `backend/app/services/shopify_lookup.py`

```python
# Functions to implement:
# - lookup_order(order_number, email_or_postcode) -> OrderResult
# - get_order_status(order_id) -> status, fulfillment_status, tracking
# - get_order_line_items(order_id) -> list of product names
```

---

## New Config Variables

| Variable | Description |
| :--- | :--- |
| `SHOPIFY_ACCESS_TOKEN` | Read-only custom app token |
| `SHOPIFY_STORE_DOMAIN` | e.g. `hoverboardstore.myshopify.com` |
| `SHOPIFY_API_VERSION` | e.g. `2024-01` |

These variables must be added to both Railway services (different read-only tokens recommended for staging vs production).

---

## New API Endpoint

```
POST /api/shopify/order-status
Authorization: Bearer <ADMIN_DASHBOARD_TOKEN> or internal only

Body:
{
  "session_id": "...",
  "order_number": "1234",
  "email_or_postcode": "..."
}

Response (verified):
{
  "verified": true,
  "order_number": "1234",
  "fulfillment_status": "dispatched",
  "tracking_number": "JD0...",
  "tracking_company": "DHL",
  "product_names": ["6.5 Hoverboard Black"],
  "order_date": "2026-06-20"
}

Response (not verified):
{
  "verified": false,
  "message": "Order not found or details do not match."
}
```

---

## Security Rules

1. Shopify token must only be stored as a Railway environment variable — never committed to code
2. Bot must never return raw Shopify API response to customer — always extract and sanitise specific fields
3. Bot must never expose full delivery address
4. Bot must never expose payment information
5. All Shopify lookup calls must be logged with `session_id` and `order_number` (not customer email) for audit

---

## Testing Plan

- Unit tests for `shopify_lookup.py` using mocked Shopify API responses
- Integration tests covering verified, not-verified, and 3-attempt-fail flows
- Negative test: wrong order number returns no data
- Negative test: correct order number but wrong email returns no data
- Add 20+ order tracking questions to Phase 2 dataset with `requires_shopify_lookup: true`

---

## Acceptance Gate (Phase 4)

See `PHASE_GATES.md` — Section Phase 4 Gate for full checklist.
