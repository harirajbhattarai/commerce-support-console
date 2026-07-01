# Project Checkpoint: HCHAHAL Support Console / Shopify + Amazon Support Automation Prototype

This checkpoint file summarizes the current architecture, active workflows, database schema, security rules, and the roadmap for the support console.

---

## 1. Project Information & Tech Stack

* **Project Name**: HCHAHAL Support Console / Shopify + Amazon support automation prototype
* **Current Environment**: Local development only (Startup manual created. Use START_HCHAHAL_SUPPORT_CONSOLE.md to run the local system.)
* **Tech Stack**:
  * **Frontend**: Vanilla HTML5, CSS3, and JavaScript (with micro-animations)
  * **Backend**: FastAPI (Python)
  * **Database**: Supabase PostgreSQL
  * **Knowledge Base**: Local JSON knowledge base with pre-seeded support articles
  * **Human Reply Delivery**: REST polling (no WebSockets yet for simplicity)

---

## 2. Current Working System

1. **Supabase Connection**: Fully integrated and online via environment variables (`backend/.env`).
2. **Chat Logs**: Customer conversations and bot logs are securely recorded in the database.
3. **Staff Notes**: Internal support notes are saved and retrieved in the agent dashboard view.
4. **Status Management**: Thread status is trackable and transitionable (`new`, `in_progress`, `needs_escalation`, `resolved`).
5. **Reply Drafts & Agent Replies**: Fully implemented. Drafts persist across session selection changes and are deleted once replies are successfully transmitted.
6. **REST Polling**: Customer widget polls `/api/agent-replies/{session_id}` every 5 seconds to query sent messages.
7. **Unified Hosting**: FastAPI serves both the backend API and frontend static pages locally from:
   * **Base URL**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
8. **Admin Dashboard Console**: Accessible directly at [http://127.0.0.1:8000/admin-dashboard.html](http://127.0.0.1:8000/admin-dashboard.html)
9. **Customer Storefront / Widget Demo**: Accessible directly at [http://127.0.0.1:8000/index.html](http://127.0.0.1:8000/index.html)
10. **Multi-Channel Switcher & Labeling**: Includes channel and store switchers, dynamic thread badging (Shopify store IDs vs Amazon GiftGadgets and Sandbox labels), and an interactive sandbox order details panel.
11. **Guardrails**: No automatic replies, messaging APIs, or messages are sent to Amazon. Sandbox order lookup is completely read-only and strips all buyer PII (ShippingAddress, BuyerInfo, BuyerTaxInformation).
12. **Knowledge Brain Schema**: SQL foundation defined in `backend/knowledge_brain_schema.sql` for the new `products` and `product_knowledge` tables (not yet applied to Supabase; existing `support_articles` preserved).

---

## 3. Database Schema Layout (Supabase)

* **`stores`**: Setup configurations for multi-store routing.
* **`support_articles`**: Seeding container for article documents.
* **`chat_logs`**: Logs customer and assistant message pairs, RAG confidence, and status metadata.
* **`staff_notes`**: Internal team commentary linked to session threads.
* **`reply_drafts`**: Stores temporary, unsent agent message drafts.
* **`agent_replies`**: Stores finalized sent agent replies for customer consumption.
* **`products`**: Stores structured product catalogs (SKUs, ASINs, titles, brands) mapped to store environments.
* **`product_knowledge`**: Stores product-specific diagnostics, troubleshooting steps, and safety guides linked to products.

> [!IMPORTANT]
> **Knowledge Brain database foundation applied successfully.**
> The `products` and `product_knowledge` tables, along with their optimization indexes and triggers, have been successfully executed and applied in Supabase. Existing `support_articles` are fully preserved and untouched.
> * **Architecture Decision**: The local `products` and `product_knowledge` tables serve strictly as a **temporary support cache/prototype** for draft reply generation testing. The final company-wide source of truth is the **Master Commerce Brain** (built separately).
> * **Abstraction Layer**: **Knowledge Service adapter layer implemented for temporary local cache retrieval.** The abstraction layer `backend/app/services/knowledge_service.py` is fully implemented along with debug endpoints `/api/knowledge/` registered in `backend/app/routes/knowledge.py`. This encapsulates all database lookups, avoiding direct table dependencies and preparing the engine for seamless hot-swapping to the Master Commerce Brain later. *(An endpoint usability fix has been applied to `/api/knowledge/search` to support both `q` and `query` parameters, prioritizing `q`, and returning a friendly JSON error if neither is supplied).*
> * **Knowledge Connection**: **Knowledge Service connected to draft generation for Shopify/local and Amazon sandbox draft guidance.** The `/api/amazon/draft/analyse` endpoint retrieves cached guides from `KnowledgeService` based on query keywords. Suggested reply drafts automatically populate with safety-compliant troubleshooting instructions. High-risk safety detections (e.g. charger/battery smoke or burning smells) automatically elevate the risk level to high and mark the ticket for human escalation.
> * **Data Scale**: No bulk catalog loads are permitted; only minimal, reviewed verification records are used. *(Temporary hoverboard test seed drafted only, not final Master Commerce Brain data, located in `backend/knowledge_brain_temporary_hoverboard_test_seed.sql`).*
> * **Active Guardrails**: No production Amazon connection has been established; no Amazon Messaging API is in use; no Amazon messages have been sent; auto-reply remains disabled. Every generated reply draft continues to require manual agent review and approval.
> * **Live Deployment Preparation**: **Deployment files prepared; admin dashboard auth required before public launch.** Configured dynamic CORS whitelist middleware in FastAPI backend, locked build runtime and Procfiles, and implemented simple admin token gate authentication on `/admin-dashboard.html` and private admin APIs, and verified that `.gitignore` correctly ignores all secret environments. Handled Railway root folder context constraints by mirroring frontend static files to `backend/frontend` and refactoring mount paths to fail safely and gracefully without crashing the server container.
> * **Next Phase**: Initialize git and push to a private GitHub repository, followed by integrating pgvector similarity search inside the `KnowledgeService` retrieval pipeline.

---

## 4. Current Working Workflows

1. **Shopper Message Submission**: A shopper posts a message in the chat widget.
2. **FastAPI Ingestion**: FastAPI receives the payload.
3. **Auto-Reply Matcher**: The bot searches local knowledge base articles. If no keyword matches, it prompts for human handoff and tags the thread.
4. **Chat Log Persistence**: Logs of the interaction save to Supabase `chat_logs`.
5. **Console Sync**: The support agent opens the HCHAHAL Support Console dashboard.
6. **Ticket State Management**: The agent transitions conversation statuses.
7. **Staff Commentary**: The agent records internal notes on the case.
8. **Draft Operations**: The agent types a draft response (saved instantly and persists across thread swaps).
9. **Message Transmission**: The agent clicks **Send Reply**, which clears the draft and saves the message to `agent_replies`.
10. **Storefront Polling**: The customer widget polls every 5 seconds, gets the new agent message, and renders it in the bubble timeline.

---

## 5. Important Security Warnings

> [!WARNING]
> **1. Supabase Credentials Exposure**: Never expose the Supabase service role key inside frontend files. Keep it strictly inside `backend/.env`.
> 
> **2. Supabase Key Rotation**: Rotate your Supabase service role key before deploying to production as it appeared in screenshots during local development.
> 
> **3. Shopify Integration**: Do not install this codebase on a live Shopify production environment yet.
> 
> **4. Amazon Credentials**: Do not configure or connect real Amazon Seller Central or AWS credentials until the prototype's architecture has been reviewed.

---

## 6. Amazon SP-API Connector Status

### Connector Health Foundation
We have successfully implemented the **Amazon SP-API Connector Health Foundation** and fully configured it in the local environment:
* **Sandbox Application**: `HCHAHAL SUPPORT CONNECTOR` has been successfully created.
* **Credentials Configuration**: LWA Client ID, LWA Client Secret, LWA Refresh Token, `AMAZON_REGION` (`eu-west-1`), and `AMAZON_MARKETPLACE_ID` (`A1F83G8C2ARO7P`) are fully configured in the local `backend/.env`.
* **Health Check Endpoint**: `GET /api/amazon/health` now returns:
  * `configured`: `true`
  * `missing_env_vars`: `[]`
  * `mode`: `"ready_for_sp_api_test"`

> [!IMPORTANT]
> **AWS IAM Correction**:
> AWS IAM and Signature Version 4 are **not** required for our current standard SP-API test flow. They are treated as optional legacy settings.

### Sandbox Connection & API Test
* **Status**: **Implemented & Successfully Verified**
* **Endpoints**: 
  * `GET /api/amazon/token-test` (LWA Token exchange diagnostics - **Verified**)
  * `GET /api/amazon/sandbox/marketplaces` (Read-only SP-API Sellers sandbox connection call - **Verified**)
  * `GET /api/amazon/sandbox/orders` (Safe SP-API Orders sandbox connection call - **Verified**)
  * `GET /api/amazon/orders/{order_id}` (Safe SP-API Orders lookup by ID in sandbox mode - **Verified**)
* **Verification Results**:
  * **Token Exchange**: Works successfully. Exchanges the LWA Refresh Token for an access token without leaking credentials.
  * **First Safe SP-API Sandbox Call**: Works successfully. Calls the read-only Sellers endpoint to fetch participations.
  * **Orders API Sandbox Lookup**: Works successfully. Queries `GET /orders/v0/orders` on the regional sandbox endpoint and returns only sanitized order metadata. Uses working defaults (`ATVPDKIKX0DER` and `TEST_CASE_200`) when no parameters are provided to match static sandbox mock rules.
  * **Order Lookup by ID**: Implemented and verified in sandbox mode. Tested successfully with sandbox order ID `902-1845936-5435065`. Token exchange succeeded, and the SP-API order lookup succeeded, returning only sanitized order metadata.
* **HCHAHAL Support Console Layout & Switchers Integration**:
  * **Status**: **Implemented & Successfully Verified**
  * **Changes**: Redesigned console layout (widened details panel to `320px` to prevent input/button cutoff, adjusted height to `calc(100vh - 173px)`), added top switcher row with active Channel filters (All, Shopify, Amazon) and Store filter dropdown, rendered dynamic Channel/Store badges on threads list, toggled channel-aware order lookup placeholders (Shopify warning, Amazon sandbox lookup, future Coming Soon placeholder), and added monospace click-to-copy Order ID support.
  * **Label Customization**: Updated Amazon channel to use proper account labeling (`GiftGadgets` in sandbox mode with environment label `Sandbox`) instead of Shopify store labels. Shopify store IDs (`hoverboard_store`, `aroma_haven`, `hcs_gadgets`) remain exclusive to the Shopify channel.
  * **Mock Marketplace Data**: The Amazon sandbox returned mock marketplace data, which shows the US marketplace (`ATVPDKIKX0DER`) even though the UK marketplace (`A1F83G8C2ARO7P`) is configured in the environment.
* **Safety Boundaries & Guardrails**:
  * **No Amazon messages have been sent**.
  * **No buyer data, order data, or messaging APIs have been touched (other than safe sandbox read-only lookups)**.
  * **No Messaging API was used**.
  * **Auto-send remains disabled**.
  * **Buyer PII is strictly stripped/excluded** from response payloads (specifically `ShippingAddress`, `BuyerInfo`, and `BuyerTaxInformation`).
* **Important Implementation Note**:
  * **Sandbox Mode**: Sandbox uses mock order IDs and fallback mapping for known sandbox test IDs (specifically mapping `902-1845936-5435065` to `TEST_CASE_200` internally to match static sandbox rules).
  * **Production Mode**: Production order lookup later must use real order IDs and continue to exclude buyer PII unless explicitly approved and compliant.
* **Next Recommended Phase**: Provision the Product + Policy Knowledge Brain database tables (`products`, `product_knowledge`) via database migrations, seed them with mock products and policies, and connect the query routes in the backend.
* **API Invocations**:
  * **OAuth Token Exchange**: Asynchronously exchanges the LWA Refresh Token for an access token via LWA OAuth POST request.
  * **Sellers Sandbox Query**: Asynchronously queries the read-only endpoint `GET /sellers/v1/marketplaceParticipations` on `sandbox.sellingpartnerapi-eu.amazon.com` (using the fetched access token).
  * **Orders Sandbox Query**: Asynchronously queries the endpoint `GET /orders/v0/orders` on `sandbox.sellingpartnerapi-eu.amazon.com` (using the fetched access token).
* **Security & Guardrails**:
  * Safe diagnostic response envelopes. Credentials, tokens, and secrets are strictly stripped out of response payloads.
  * Completely read-only endpoints are invoked. No orders or messaging APIs are touched.
* **Test Verification Outputs**:
  * Response from `GET /api/amazon/sandbox/marketplaces` returns:
     ```json
     {
        "configured" : true,
        "endpoint" : "sellers marketplace participations",
        "marketplace_count" : 1,
        "marketplaces" : [
           {
              "country_code" : "US",
              "default_currency_code" : "USD",
              "is_participating" : true,
              "marketplace_id" : "ATVPDKIKX0DER",
              "name" : "Amazon.com"
           }
        ],
        "mode" : "sandbox_marketplace_test",
        "sp_api_call" : "success",
        "token_exchange" : "success"
     }
     ```
  * Response from `GET /api/amazon/sandbox/orders` returns:
     ```json
     {
        "configured" : true,
        "endpoint" : "orders list",
        "mode" : "sandbox_orders_test",
        "order_count" : 2,
        "orders" : [
           {
              "amazon_order_id" : "902-1845936-5435065",
              "fulfillment_channel" : "MFN",
              "last_update_date" : "1970-01-19T03:58:32Z",
              "number_of_items_shipped" : 0,
              "number_of_items_unshipped" : 1,
              "order_status" : "Unshipped",
              "order_type" : "StandardOrder",
              "purchase_date" : "1970-01-19T03:58:30Z",
              "sales_channel" : "Amazon.com"
           },
           {
              "amazon_order_id" : "902-8745147-1934268",
              "fulfillment_channel" : "MFN",
              "last_update_date" : "1970-01-19T03:58:32Z",
              "number_of_items_shipped" : 0,
              "number_of_items_unshipped" : 1,
              "order_status" : "Unshipped",
              "order_type" : "StandardOrder",
              "purchase_date" : "1970-01-19T03:58:30Z",
              "sales_channel" : "Amazon.com"
           }
        ],
        "sp_api_call" : "success",
        "token_exchange" : "success"
     }
     ```

### Issue Classification & Draft Reply Engine (Frontend & Backend Connected)
* **Status**: **Implemented & Successfully Verified**
* **Endpoints**: 
  * `POST /api/amazon/draft/analyse`
* **Features**:
  * **Amazon Issue Assistant UI**: Integrated a clean, compact assistant card above the Draft Customer Reply composer inside the admin dashboard. Visible exclusively on Amazon channel threads.
  * **Interactive Triage CTA**: Button triggers real-time sandbox triage requests to the analysis backend, loading results and loading drafts automatically.
  * **Channel-Aware Composer Actions**: The composer action bar adapts to the selected thread's channel:
    * **Shopify**: Displays standard `Clear Draft`, `Save Draft`, and `Send Reply` buttons.
    * **Amazon**: Hides the `Send Reply` button entirely, displays a `Copy Draft` button (to copy the composer contents to the clipboard), and displays a helpful warning message: *"Amazon sending is disabled. Review the draft and send manually in Seller Central."*
    * **Future Channels (eBay/TikTok/Email)**: Hides `Send Reply`, hides `Copy Draft`, and displays: *"Sending not connected yet."*
  * **Pydantic Validation**: Uses `AmazonAnalysisRequest` and `AmazonAnalysisResponse` models.
  * **Keyword/Regex Classifier**: Matches message strings against keywords to classify issues into 14 core prioritized categories (such as `delivery_status`, `item_not_received`, `return_request`, `faulty_product`, etc.).
  * **Risk/Action Routing**: Maps safety/battery concerns (`battery_or_safety_issue`), bad reviews (`negative_feedback_threat`), A-to-Z disputes (`a_to_z_claim_risk`), and legal threats (`angry_customer`) to `high` risk and `escalate` recommended action. Maps returns, delivery, wrong items, and faulty products (`faulty_product`) to safe `draft_reply` or `human_review` actions (usually medium risk).
  * **Tightened Safety Keywords**: Checks for expanded safety keywords (including `battery`, `fire`, `smoke`, `smell`, `odor`, `overheating`, `overheat`, `charge`, `charging`, `spark`, `unsafe`, `dangerous`, `shock`) to preemptively escalate issues as high risk.
  * **Generic Draft Safety Fallback**: If a product has a generic fault (`faulty_product`) but the category (e.g. hoverboard) is unknown, the engine generates a generic, safe holding template advising them to stop using it if unsafe, instead of recommending product-specific calibration/reset steps.
  * **Red Warning Banner Alert**: Displays a warning alert inside the composer card for high-risk safety or escalation triggers: *"⚠️ High-risk issue — human review required. Do not send without manager approval."*
  * **Regex Order ID Extraction**: Automatically extracts standard order IDs (`\b\d{3}-\d{7}-\d{7}\b`) from the message.
  * **Dynamic Order Context Lookup**: Invokes `get_sandbox_order(order_id)` and adjusts draft templates (e.g. confirming cancellation for `Unshipped` orders vs routing/refusing cancellation for `Shipped` transit orders).
* **Verification Outputs**:
  * **Invoice Query (Low-Priority Test Case)**: Returns category `invoice_request`, risk `low`, recommended action `draft_reply`, and VAT invoice guide text. (Note: Treated strictly as a low-priority diagnostic test case, not highlighted as a core customer service workflow).
  * **Safety Concern (Escalated)**: Any query containing battery/fire/smoke/overheating/burning words returns category `battery_or_safety_issue`, risk `high`, recommended action `escalate`.
  * **Faulty Product (Unknown Category)**: Returns category `faulty_product`, risk `medium`, and the generic safe troubleshooting draft warning.
  * **Faulty Product (Hoverboard Category)**: Returns category `faulty_product`, risk `medium`, and hoverboard-specific reset steps if keywords like "hoverboard" are matched.

### Amazon Support Workflow Decision
For Amazon customer service, we will **NOT** build full auto-send or automatic customer replies. The workflow is strictly defined as follows:
1. **Ingestion**: Import or receive a mock Amazon customer issue.
2. **Analysis**: Classify the issue type and analyze the risk level.
3. **Drafting**: Generate a suggested draft reply.
4. **Console Sync**: Display the draft reply inside the HCHAHAL Support Console.
5. **Review**: Human staff reviews, edits, and refines the draft.
6. **Approval**: Human staff clicks Approve/Send only when confirmed safe.
7. **Transmission (Future)**: Only later, after the Amazon SP-API connector is fully verified, approved messages may be sent through the Amazon Messaging API.

### Strict Guardrails & Safety Rules
* **No Automatic Amazon Sending**: Direct automated replies to customers are strictly prohibited.
* **Human Approval Required**: No message can be sent to Amazon without manual agent verification and approval.
* **Mandatory Review Lists**: The following high-risk, policy-sensitive cases must always be escalated and require human review:
  * A-to-Z claims
  * Refund disputes
  * Damaged items
  * Safety issues
  * Negative feedback threats
  * Warranty disputes
* **Connector Limits**: The Amazon API integration will start with connector health checks and safe order lookup queries only. Do not build Amazon message transmission capabilities yet.


---

## 7. Local Troubleshooting Notes

### Issue 1: Supabase Connection Failure
* **Symptom**: `/health` or dashboard reports:
  `connection_failed: [Errno 8] nodename nor servname provided, or not known`
* **Root Cause**: If the Supabase cloud project was recently unpaused, the local macOS resolver (`mDNSResponder`) may still serve a cached negative DNS record.
* **Resolution**: Flush the DNS cache in your macOS Terminal:
  ```bash
  sudo killall -HUP mDNSResponder
  ```
  Then restart and test the FastAPI server.

### Issue 2: Address Already In Use
* **Symptom**: Running the startup command fails with:
  `[Errno 48] error while attempting to bind on address ('127.0.0.1', 8000): [errno 48] address already in use`
* **Root Cause**: An existing FastAPI/Uvicorn process is already running on port 8000.
* **Resolution**: Find and kill the process:
  ```bash
  lsof -i :8000
  kill <PID>
  ```

