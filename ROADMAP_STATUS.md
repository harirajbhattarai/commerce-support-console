# Roadmap Status: HCHAHAL Support Console / Shopify + Amazon Support Automation Prototype

This document reviews the current development progress of the HCHAHAL Support Console prototype against the 12 key phases of the roadmap.

---

## 1. Confirm/Document Current System
* **Status**: **Done**
* **What exists**: 
  * `CHECKPOINT.md` containing the overall technical state, tables, and workflows.
  * `walkthrough.md` mapping the Human Reply Draft Box and customer widget polling features.
  * `AMAZON_CREDENTIALS_GUIDE.md` explaining environment variables, credentials sources, and security rules.
  * `AMAZON_SETUP_CHECKLIST.md` guiding Amazon developer setup flow step-by-step.
  * `AWS_IAM_SP_API_SETUP_GUIDE.md` explaining AWS User/Role setup for SP-API.
  * `AMAZON_REFRESH_TOKEN_GUIDE.md` guiding LWA Refresh Token retrieval.
  * `KNOWLEDGE_BRAIN_PLAN.md` mapping out the Product + Policy Knowledge Brain design and schema.
  * `task.md` detailing the development checklist.
  * Backend health diagnostic endpoint `/health`.
* **What is missing**: None.
* **Recommended next action**: Keep documentation in sync as codebase features expand.

---

## 2. Clean Database/Schema
* **Status**: **Done**
* **What exists**: 
  * `supabase_schema.sql` providing structured table setups for `stores`, `support_articles`, `article_chunks`, `conversations`, `messages`, `escalations`, `staff_notes`, `chat_logs`, `reply_drafts`, and `agent_replies`.
  * Proper indexing and Postgres triggers configured.
* **What is missing**: Automated migration scripts or CI/CD pipelines (currently migrations are run manually in the Supabase SQL editor).
* **Recommended next action**: Set up a migration runner or seeding scripts for local development environments.

---

## 3. Improve Support Console Workflow
* **Status**: **Done**
* **What exists**: 
  * `admin-dashboard.html` with real-time UI updates upon sending replies, clearing drafts, or saving internal staff notes.
  * Fading success micro-animations for UX completeness.
* **What is missing**: Real-time push updates for the thread lists on the admin console (the panel relies on manual "Refresh" button clicks).
* **Recommended next action**: Add a background REST polling hook or Server-Sent Events (SSE) to update active threads dynamically.

---

## 4. Move Knowledge Base from JSON to Supabase
* **Status**: **Partially done (Knowledge Service connected to draft generation for Shopify/local and Amazon sandbox draft guidance)**
* **What exists**: 
  * Database tables `support_articles` and `article_chunks` defined in `supabase_schema.sql`.
  * `KNOWLEDGE_BRAIN_PLAN.md` detailing the Product & Policy Knowledge Brain database design, schemas, and query flows.
  * `backend/knowledge_brain_schema.sql` migration containing `products` and `product_knowledge` tables, fully applied in Supabase.
  * `backend/knowledge_brain_seed_examples.sql` housing separated optional sample seeds.
  * `backend/knowledge_brain_temporary_hoverboard_test_seed.sql` containing drafted temporary validation seeds for the generic hoverboard support prototyping (not final Master Commerce Brain data).
  * `SUPPORT_CONSOLE_KNOWLEDGE_SOURCE_DECISION.md` outlining the architectural decision to abstract support knowledge lookups from the local cache to facilitate future transition to the Master Commerce Brain.
  * `backend/app/services/knowledge_service.py` implementing database retrieval functions (`get_product_by_sku`, `get_product_by_asin`, `get_knowledge_for_product`, and `get_support_knowledge`).
  * `backend/app/routes/knowledge.py` exposing local testing endpoints for SKU/ASIN lookup and search (updated to support both `q` and `query` parameters, prioritizing `q`, and returning a friendly JSON error if neither is supplied), registered in `main.py`.
  * Integrated `/api/amazon/draft/analyse` endpoint in `backend/app/main.py` calling `KnowledgeService.get_support_knowledge()` to fetch cached product troubleshooting guides and safety rules dynamically.
* **What is missing**: 
  * The main `/api/chat` customer storefront widget endpoint still performs simple keyword matching on the local `knowledge_base.json` memory array.
* **Recommended next action**: Refactor the customer storefront widget `/api/chat` endpoint to retrieve policy articles through `KnowledgeService` instead of checking the static `knowledge_base.json` memory array.
  * *Active Guardrails*: Ensure no production Amazon connection, LWA messaging endpoints, or automatic replies are introduced. Human review must remain strictly required for all drafts.
  * *Commerce Brain Isolation*: Keep the local tables as a temporary cache and isolate lookups behind the service layer.

---

## 5. Add Real RAG/Vector Search
* **Status**: **Not started**
* **What exists**: 
  * `pgvector` Postgres extension declaration in `supabase_schema.sql`.
  * `embedding vector(1536)` column on the `article_chunks` table.
* **What is missing**: 
  * Text embedding generator scripts.
  * Embedding model API integration in the backend.
  * Cosine similarity query function in Supabase.
* **Recommended next action**: Write a backend service to chunk guideline files, generate embeddings via API, save to Supabase, and implement similarity lookup routes.

---

## 6. Add AI Model
* **Status**: **Not started**
* **What exists**: 
  * Mock responses in `main.py` based on exact keyword matching.
* **What is missing**: 
  * Integration with LLMs (e.g., Gemini API, OpenAI API).
  * Prompts to synthesize answers from fetched RAG chunks.
* **Recommended next action**: Add an AI processing orchestrator to write contextual responses using matched guidelines.

---

## 7. Deploy FastAPI Online
* **Status**: **Partially done (Deployment files prepared; admin dashboard auth required before public launch.)**
* **What exists**: 
  * Local Uvicorn server configuration.
  * Production configurations `Procfile` and `runtime.txt` built and ready.
  * Dynamic environment-configurable CORS whitelist middleware implemented.
  * Live deployment blueprint and checklists documented in `DEPLOYMENT_LIVE_READINESS_PLAN.md` and `START_HCHAHAL_SUPPORT_CONSOLE.md`.
  * Access control security and token-gate architecture drafted in `ADMIN_DASHBOARD_SECURITY_PLAN.md`.
* **What is missing**: 
  * Gated auth token verification logic implemented in static route handlers.
  * Hosting setup on Railway or Render, and linking production Supabase variables.
* **Recommended next action**: Implement the Option A Token authentication guard on private FastAPI route middleware, and deploy the backend to Railway/Render.

---

## 8. Install Shopify Widget Live
* **Status**: **Not started**
* **What exists**: 
  * Storefront mock `index.html` and script `widget.js` serving the chatbot widget locally.
* **What is missing**: 
  * Shopify App structure.
  * Theme app extension configurations to inject the widget into a live Shopify theme.
* **Recommended next action**: Create a Shopify Partner App template and configure the theme extension to load widget scripts dynamically.

---

## 9. Add Security/Auth/Rate Limits
* **Status**: **Not started**
* **What exists**: 
  * Safe service role separation (keys restricted to `.env` on backend).
* **What is missing**: 
  * Admin authorization guards (login screen on `/admin-dashboard.html` using Supabase Auth).
  * Rate-limiting middleware on chat routes.
  * API Key rotation protocols.
* **Recommended next action**: Integrate Supabase Auth on the console page and build a login wrapper block.

---

## 10. Add Order Lookup
* **Status**: **Done for Amazon channel (Shopify lookup pending)**
* **What exists**: 
  * Sandbox order ID lookup for Amazon SP-API sandbox integrated into the right-side Order Details panel.
  * Monospace copy-to-clipboard support for retrieved Amazon Order IDs.
  * Channel-aware warning placeholder for Shopify threads ("Shopify order lookup not connected yet").
* **What is missing**: 
  * Backend API hooks to connect to real Shopify Admin API.
  * Real order database mappings.
* **Recommended next action**: Build mock Shopify order endpoints to support Shopify checkout lookups.

---

## 11. Add Courier Tracking
* **Status**: **Not started**
* **What exists**: 
  * Visual placeholder card in `admin-dashboard.html`.
* **What is missing**: 
  * Courier tracking API adapters (USPS, FedEx, DHL, Royal Mail).
  * Webhook handlers to capture status transit updates.
* **Recommended next action**: Integrate a shipping tracking API client or set up a mock carrier endpoint.

---

## 12. Amazon SP-API Connector/Testing Layer
* **Status**: **Done (Sandbox Connection & Orders Lookup Complete)**
* **What exists**: 
  * Sandbox app `HCHAHAL SUPPORT CONNECTOR` created.
  * LWA Client ID, Secret, and Refresh Token configured in `backend/.env`.
  * Region `eu-west-1` and Marketplace `A1F83G8C2ARO7P` configured.
  * `GET /api/amazon/health` successfully returning `configured: true`, `missing_env_vars: []`.
  * `GET /api/amazon/token-test` is verified and successfully exchanges the refresh token for a temporary LWA access token (HTTP 200).
  * `GET /api/amazon/sandbox/marketplaces` is verified and successfully queries the Sellers marketplace participations API in the sandbox, returning sanitized data.
  * `GET /api/amazon/sandbox/orders` is verified and successfully queries the Orders API in the sandbox, using correct mock parameters (`ATVPDKIKX0DER`, `TEST_CASE_200`) as fallback defaults, and returning sanitized metadata with PII stripped out.
  * `GET /api/amazon/orders/{order_id}` is verified and successfully queries the Orders API in sandbox mode for a specific order ID (tested with sandbox order ID `902-1845936-5435065`). Token exchange succeeded and the lookup succeeded, returning sanitized metadata.
  * **HCHAHAL Support Console Layout & Switchers Integration**:
    * Redesigned dashboard layout: widened right details panel to `320px` to prevent control cutoff, adjusted workspace height to `calc(100vh - 173px)`.
    * Multi-Channel Switcher: Added Channel switcher options (All, Shopify, Amazon active; eBay, TikTok, Email future).
    * Store Filter Switcher: Added dropdown option (All, Hoverboard Store, Aroma Haven, HCS Gadgets).
    * Dynamic Placeholders: Selecting Shopify thread shows unconnected notice; Amazon thread shows sandbox order lookup; future shows coming soon.
    * Monospace & Copyable Order ID: Renders retrieved ID in monospace, supports click-to-copy to clipboard.
    * Label Customization: Updated Amazon channel to use proper account labeling (`GiftGadgets` in sandbox mode with environment label `Sandbox`) instead of Shopify store labels. Shopify store IDs (`hoverboard_store`, `aroma_haven`, `hcs_gadgets`) remain exclusive to the Shopify channel.
  * Sandbox returned mock marketplace data, which may show the US marketplace (`ATVPDKIKX0DER`, `Amazon.com`, `USD`) even though the UK marketplace (`eu-west-1` / `A1F83G8C2ARO7P`) is configured in the backend environment.
  * `AMAZON_REFRESH_TOKEN_GUIDE.md`, `AMAZON_ORDERS_SANDBOX_PLAN.md`, `AMAZON_ORDER_CONSOLE_INTEGRATION_PLAN.md`, and `AMAZON_SETUP_CHECKLIST.md` documenting onboarding, token retrieval, and sandbox query steps.
  * Validation engine in `backend/app/amazon_client.py` checking credentials, executing token exchange, and querying sandbox.
  * Triage and issue classification endpoint `POST /api/amazon/draft/analyse` implemented and connected to the HCHAHAL Support Console frontend. The composer actions bar is fully channel-aware: Shopify threads retain standard reply sending; Amazon threads hide `Send Reply`, show a `Copy Draft` CTA, and show a Seller Central instruction note; future channels (eBay/TikTok/Email) show a connection error. No live Amazon sending or messaging APIs are active.
* **What is missing**: None (backend triage logic and frontend channel-aware composer controls are fully complete and verified).
* **Amazon Support Workflow Decision**:
  We will **NOT** build full auto-send or automatic customer replies. The workflow is strictly defined as follows:
  1. **Ingestion**: Import or receive a mock Amazon customer issue.
  2. **Analysis**: Classify the issue type and analyze the risk level.
  3. **Drafting**: Generate a suggested draft reply.
  4. **Console Sync**: Display the draft reply inside the HCHAHAL Support Console.
  5. **Review**: Human staff reviews, edits, and refines the draft.
  6. **Approval**: Human staff clicks Approve/Send only when confirmed safe.
  7. **Transmission (Future)**: Only later, after the Amazon SP-API connector is fully verified, approved messages may be sent through the Amazon Messaging API.
* **Strict Guardrails & Safety Rules**:
  * **No Automatic Amazon Sending**: Direct automated replies to customers are strictly prohibited. **No Amazon messages have been sent.**
  * **Human Approval Required**: No message can be sent to Amazon without manual agent verification and approval.
  * **No Messaging API was used**.
  * **Auto-send remains disabled**.
  * **No Buyer Data, Order Data, or Messaging APIs have been touched** (other than safe sandbox read-only metadata lookups).
  * **Buyer PII is strictly stripped/excluded** from response payloads (specifically `ShippingAddress`, `BuyerInfo`, and `BuyerTaxInformation`).
  * **Mandatory Review Lists**: High-risk, policy-sensitive cases must always be escalated and require human review (e.g. A-to-Z claims, refund disputes, damaged items, safety issues, negative feedback threats, warranty disputes).
  * **Connector Limits**: The Amazon API integration will start with connector health checks and safe order lookup queries only. Do not build Amazon message transmission capabilities yet.
* **Important Implementation Note**:
  * **Sandbox Mode**: Sandbox uses mock order IDs and fallback mapping for known sandbox test IDs (such as mapping `902-1845936-5435065` to `TEST_CASE_200` internally to match static sandbox rules). We have customized the returned order status to show both Shipped and Unshipped flows in the sandbox.
  * **Production Mode**: Production order lookup later must use real order IDs and continue to exclude buyer PII unless explicitly approved and compliant.
* **Recommended next action**: Design and build the frontend UI dashboard components (risk indicators, suggested drafts panel, and composer injector) to showcase these classification results inside the admin panel.




---

## 13. Troubleshooting Notes

### Issue 1: Supabase Connection Failure
* **Symptom**: `/health` or dashboard reports:
  `connection_failed: [Errno 8] nodename nor servname provided, or not known`
* **Root Cause**: Stale macOS DNS negative cache (`mDNSResponder`) preventing resolution of the newly unpaused Supabase project.
* **Resolution**: Run `sudo killall -HUP mDNSResponder` in macOS Terminal to clear DNS caching, then restart and test the FastAPI server.

### Issue 2: Port 8000 Already In Use
* **Symptom**: Running the startup command fails with:
  `[Errno 48] error while attempting to bind on address ('127.0.0.1', 8000): [errno 48] address already in use`
* **Root Cause**: An existing FastAPI/Uvicorn process is already running on port 8000.
* **Resolution**: Run `lsof -i :8000` to find the process ID and run `kill <PID>` to stop it.

