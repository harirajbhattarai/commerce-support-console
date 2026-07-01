# Shopify Storefront Chatbot Widget - Live Integration Plan

This document details the configuration parameters, endpoint restrictions, and visitor usage controls required to link the embedded Shopify storefront widget to your production Railway backend.

---

## 1. Production API Routing Configuration

The storefront chat widget connects to the FastAPI backend dynamically via the global `window.HBS_CHAT_CONFIG` parameters:

*   **Production API URL**: `https://commerce-support-console-production.up.railway.app`
*   **Local Dev API URL**: `http://127.0.0.1:8000`

### Integration Code Snippet
In [install-snippet.liquid](file:///Volumes/XTREM/BITLEAF-SYTEM/50-59%20SYSTEMS/52%20AI%20Agents/GOOGLE_I_O_2026/ANTIGRAVITY_AGENT/frontend/shopify-widget/install-snippet.liquid#L9-L13):
```html
<script>
  window.HBS_CHAT_CONFIG = {
    storeId: "hoverboard_store", // Options: 'hoverboard_store', 'hcs_gadgets', 'aroma_haven'
    // To test locally, set this to: "http://127.0.0.1:8000"
    apiHost: "https://commerce-support-console-production.up.railway.app"
  };
</script>
```

---

## 2. API Endpoint Protection Guidelines

To prevent credentials or token leakage, the storefront widget **must only interact with public endpoints**:

| Method | Endpoint | Description | Auth Status |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/chat` | Receives visitor queries and returns assistant replies | **Public** |
| **GET** | `/api/agent-replies/{session_id}` | Polls for replies posted by the support representative | **Public** |
| **GET** | `/api/knowledge/search` | Search tool for matching policy database articles | **Public** |
| **GET** | `/health` | Server status and database health check | **Public** |

> [!CAUTION]
> **No Secrets Expose**: Never expose `ADMIN_DASHBOARD_TOKEN` or private database credentials to the storefront HTML or frontend Liquid snippet. The widget only calls endpoints that do not check tokens.

---

## 3. Client-Side Visitor Usage-Limit Plan

To prevent API resource depletion and keep chatbot usage free, a client-side visitor usage threshold is active in the widget script:

*   **Session Tracking**: The widget tracks messages in the browser's `sessionStorage` under the key `hbs_chat_question_count_{storeId}`.
*   **Usage Threshold**: Visitors are restricted to **5 free questions** per active session.
*   **Bypass Interception**: Once the threshold is met, the widget intercepts form submission, blocks the API fetch call, and renders a message in the chat bubble:
    > *"You have reached the maximum number of free support questions (5) for this session. Please contact support via email if you need further help."*

---

## 4. Production Verification Steps

Before declaring the live widget active on your Shopify theme:
1.  **CORS Whitelist Check**: Verify that your Shopify domain (e.g. `https://hoverboardstore.co.uk`) is listed inside the backend `ALLOWED_ORIGINS` environment variable.
2.  **API Fetch Probe**: Open your store's console and verify that `/api/chat` returns an answer with a `conversation_id` without CORS block warnings.
3.  **Authentication Guard**: Verify that visits to `https://commerce-support-console-production.up.railway.app/admin-dashboard.html` throw a `403 Forbidden` unless the correct token parameter is supplied.
