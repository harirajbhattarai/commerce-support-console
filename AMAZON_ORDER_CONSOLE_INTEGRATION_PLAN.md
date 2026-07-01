# Plan: Amazon Order Lookup Console Integration

This document outlines the planning for integrating the verified Amazon Selling Partner API (SP-API) sandbox order lookup capability into the HCHAHAL Support Console dashboard.

---

## 1. Mapping Amazon Orders to the Support Console
The HCHAHAL Support Console displays active support threads in the left sidebar, the message stream in the center, and order/customer information in the right-side panel.
* When an Amazon thread is selected from the sidebar, the right-side Order Details panel will display Amazon order metadata instead of Shopify details.
* The system will match the conversation thread's associated Amazon Order ID (stored in the thread metadata) and query the backend lookup endpoint.

---

## 2. Safe Fields for the Order Details Panel
To maintain strict data privacy, the right-side panel will display only non-PII metadata fields.
* **Safe to Show**:
  * Amazon Order ID (e.g., `902-1845936-5435065`)
  * Purchase Date & Last Update Date
  * Order Status (e.g., `Unshipped`, `Shipped`, `Pending`)
  * Fulfillment Channel (FBA/FBM)
  * Sales Channel (e.g., `Amazon.com`)
  * Order Type (e.g., `StandardOrder`)
  * Number of Items Shipped / Unshipped
* **Excluded (PII Protection)**:
  * Shipping Address (Customer name, street, city, zip, phone)
  * Buyer Info (Buyer name, buyer email, tax identifiers)

---

## 3. Channel Separation (Shopify vs. Amazon)
To prevent cross-channel data contamination, we will introduce a `channel` property.
* **Database & API Layer**: Conversation threads will include a `channel` tag (e.g., `shopify_widget` vs. `amazon`).
* **Console UI Badging**:
  * Threads from the Shopify widget will display a blue `[🛒 Shop]` badge.
  * Threads from Amazon will display a yellow `[📦 Amazon]` badge.
* **Dynamic Card Swapping**:
  * If `channel === 'shopify_widget'`, show the Shopify Order Card.
  * If `channel === 'amazon'`, show the Amazon Order Card.

---

## 4. Sandbox Order Lookup & Test Cases
Since we are using static sandbox mock cases, live lookups of arbitrary order IDs will return a 400 error in sandbox mode.
* **Test Case Dropdown**: During this development phase, we will display a **"Load Test Amazon Order"** helper dropdown in the Order Details panel containing the verified sandbox Order IDs (e.g., `902-1845936-5435065`).
* **Manual Lookup Input**: A lookup input field will allow manual searching of Amazon Order IDs. If a search matches a sandbox ID, it retrieves the mock record; otherwise, it handles the `InvalidInput` sandbox error gracefully.

---

## 5. Backend Endpoints Status
* `GET /api/amazon/orders/{order_id}`: **Implemented & Verified in Sandbox Mode**. Retrieves sanitized order details for a specific Amazon Order ID. Tested successfully with sandbox order ID `902-1845936-5435065`. Token exchange succeeded, and SP-API lookup succeeded.
* `GET /api/amazon/sandbox/orders`: **Implemented & Verified in Sandbox Mode**. Queries the list of orders with sanitized metadata.

---

## 6. Future Database Schema Adjustments
To support these features, the following database updates will be applied to the `chat_logs` table (and the `conversations` view if applicable):
* **`channel`** (`VARCHAR(50) DEFAULT 'shopify_widget'`): Indicates thread origin.
* **`external_order_id`** (`VARCHAR(100) NULL`): Links the thread to an external Shopify or Amazon order.

```sql
-- Planned migration queries
ALTER TABLE chat_logs ADD COLUMN IF NOT EXISTS channel VARCHAR(50) DEFAULT 'shopify_widget';
ALTER TABLE chat_logs ADD COLUMN IF NOT EXISTS external_order_id VARCHAR(100) NULL;
```

---

## 7. Strict Disabled Features & Safety Boundaries
To prevent unauthorized outbound communication, the following features will remain strictly **disabled/unimplemented**:
* **No "Send to Amazon" Composer Button**: The message composition card will disable the send button or display a status warning (`"Messaging API not connected"`) when an Amazon thread is selected.
* **No Auto-Reply Actions**: Auto-replies are completely locked for Amazon-labeled threads.
* **No Messaging API Integration**: No Messaging API was used, and no code to call the Amazon Messaging API will be added. No Amazon messages were sent.
* **Auto-send remains disabled**.
* **Buyer PII is strictly stripped/excluded** from response payloads (specifically `ShippingAddress`, `BuyerInfo`, and `BuyerTaxInformation`).
* **Important Implementation Note**:
  * **Sandbox Mode**: Sandbox uses mock order IDs and fallback mapping for known sandbox test IDs (specifically mapping `902-1845936-5435065` to `TEST_CASE_200` internally to match static sandbox rules).
  * **Production Mode**: Production order lookup later must use real order IDs and continue to exclude buyer PII unless explicitly approved and compliant.

---

## 8. Recommended Next Build Step
1. Apply the database column additions (`channel` and `external_order_id`) to the Supabase schema.
2. Refactor the frontend `admin-dashboard.html` right-side panel to dynamically fetch and display Amazon order card metadata when selecting Amazon threads.

