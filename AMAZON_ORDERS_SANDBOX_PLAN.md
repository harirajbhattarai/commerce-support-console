# Plan: Safe Amazon Orders API Sandbox Lookup

This document outlines the implementation plan for testing the Amazon Selling Partner API (SP-API) Orders API within the sandbox environment. It establishes strict data boundaries and security rules to ensure that no Buyer Personally Identifiable Information (PII) is processed or exposed.

---

## 1. Selected Orders API Sandbox Endpoint
We will use the following read-only Selling Partner API endpoint:
* **Endpoint**: `GET /orders/v0/orders`
* **Description**: Lists orders created or updated during a specified time frame.
* **Sandbox Base URL**:
  * North America: `https://sandbox.sellingpartnerapi-na.amazon.com`
  * Europe (Default): `https://sandbox.sellingpartnerapi-eu.amazon.com`
  * Far East: `https://sandbox.sellingpartnerapi-fe.amazon.com`

---

## 2. Required Input Parameters
To make a valid request to `GET /orders/v0/orders`, the following query parameters are required:
* `MarketplaceIds`: A comma-delimited list of marketplace identifiers (e.g., `ATVPDKIKX0DER` or `A1F83G8C2ARO7P`).
* `CreatedAfter`: An ISO 8601 date-time string (e.g., `2026-06-17T00:00:00Z`).

*Note: In SP-API sandbox mode, Amazon returns a predefined, static mock response regardless of the actual values passed, but the query parameters must still be syntactically valid.*

---

## 3. Safe Response Fields (To Be Returned)
Only non-sensitive order metadata will be returned to the client. The following fields are safe:
* `AmazonOrderId`: The Amazon-defined identifier for the order (e.g., `902-3103855-6826623`).
* `PurchaseDate`: The date and time when the order was placed.
* `LastUpdateDate`: The date and time when the order was last updated.
* `OrderStatus`: The current state of the order (e.g., `Unshipped`, `Shipped`, `Pending`).
* `FulfillmentChannel`: How the order is fulfilled (`AFN` for Amazon-fulfilled, `MFN` for merchant-fulfilled).
* `SalesChannel`: The sales channel (e.g., `Amazon.com`).
* `OrderType`: The type of order (e.g., `StandardOrder`).
* `NumberOfItemsShipped` / `NumberOfItemsUnshipped`: Item count metadata.

---

## 4. Fields to Exclude (PII Protection)
To prevent processing any sensitive customer data, the backend integration client **must explicitly drop or omit** the following fields before sending response data to any frontend or logging systems:
* `ShippingAddress`: Entire object must be excluded (contains customer name, street address, city, state, postal code, country, and phone).
* `BuyerInfo`: Entire object must be excluded (contains buyer name, buyer email, and tax classification info).
* `BuyerTaxInformation`: Entire object must be excluded.

---

## 5. Backend Endpoint Naming
* **Name**: `/api/amazon/sandbox/orders`
* **HTTP Method**: `GET`
* **Implementation Details**:
  1. Reads configuration variables from `backend/.env`.
  2. Asynchronously requests an LWA access token.
  3. Queries the regional Orders API sandbox endpoint `GET /orders/v0/orders`.
  4. Parses the orders payload and sanitizes it by copying *only* the safe metadata fields.
  5. Returns a structured diagnostic envelope.

---

## 6. Expected Test URL
After implementation, the test URL will be:
`http://127.0.0.1:8000/api/amazon/sandbox/orders`

The response payload structure will resemble:
```json
{
  "configured": true,
  "token_exchange": "success",
  "sp_api_call": "success",
  "endpoint": "orders list",
  "order_count": 1,
  "orders": [
    {
      "amazon_order_id": "902-3103855-6826623",
      "purchase_date": "2020-01-20T02:08:26Z",
      "order_status": "Shipped",
      "fulfillment_channel": "Mfn",
      "sales_channel": "Amazon.com",
      "order_type": "StandardOrder"
    }
  ]
}
```

---

## 7. Failure Cases & Error Handling
We must catch and gracefully handle the following error scenarios:
* **Configuration Errors**: If environment variables are missing or use default placeholders, return `configured: false` with `"token_exchange": "skipped"`.
* **Token Exchange Failures**: If LWA rejected the client secret or refresh token, return `token_exchange: "failed"` with the raw error message (stripped of credentials).
* **API Connection/Timeout Errors**: Handled via `httpx` exceptions with safe logger prints.
* **SP-API Error Envelopes**: If the sandbox returns an HTTP error code (e.g., 400 Bad Request, 403 Forbidden, 429 Too Many Requests), return `sp_api_call: "failed"` along with the response status code.

---

## 8. Onboarding Requirements: Sandbox vs. Production
* **Sandbox App Sufficiency**: A sandbox/draft SP-API application is fully sufficient.
* **Explanation**: Amazon's sandbox endpoints do **not** perform actual authorization checks against real customer seller accounts or check for production app listing status. Any valid LWA access token generated from your client credentials is sufficient to query the sandbox. No production launch or publication is required for this phase.
