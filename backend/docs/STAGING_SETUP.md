# Staging Environment Setup Guide

Follow this guide to initialize and maintain the HCHAHAL Support Console Staging environment.

---

## 1. Setup Staging Service on Railway

1.  **Create Duplicate Service**:
    *   In the Railway Project Dashboard, clone the main `commerce-support-console` service and rename it to `commerce-support-staging`.
2.  **Configure Deployment Branch**:
    *   Set the deploy branch for `commerce-support-staging` to `staging`.
3.  **Define Environment Variables**:
    *   `APP_ENV`: `STAGING` (This triggers `STAGING` visual badges and attaches noindex indexing blockers).
    *   `PORT`: `8080` (or leave default).
    *   `ADMIN_DASHBOARD_TOKEN`: Generate a separate, secure token specifically for staging verification (e.g. `staging_secret_token_12345`). Do not reuse the production admin token.
    *   `SUPABASE_URL`: Points to your staging/test Supabase project instance url.
    *   `SUPABASE_SERVICE_ROLE_KEY`: Points to your staging/test Supabase service role key.
    *   `MINIMAX_API_KEY`: Set to the same MiniMax API key to test LLM answers, but keep database logs insulated on the staging tables.
    *   `MINIMAX_MODEL`: `abab6.5g-chat` (or staging model equivalent).

---

## 2. Supabase Staging Instance Configuration

Ensure the staging Supabase database schema has been successfully seeded with the knowledge pack:
1.  Initialize tables by applying `knowledge_brain_schema.sql` and `supabase_schema.sql`.
2.  Seed general articles and products by running `knowledge_pack_hoverboard_store_v1.sql`.
3.  Double-check database connectivity using the backend `/health` endpoint.

---

## 3. Shopify Duplicate/Test Theme Integration

To test storefront widget updates in the staging environment before publishing them to the live site:

1.  **Duplicate Storefront Theme**:
    *   In the Shopify Admin portal, navigate to **Online Store > Themes**.
    *   Click **Actions > Duplicate** on the current live theme to create a duplicate test theme (e.g. *"Staging QA Theme"*).
2.  **Modify API URL configuration**:
    *   Edit code on the duplicated theme.
    *   Open `assets/hoverboard-chat-widget.js` (or similar injected theme file).
    *   Set the backend API endpoint URL value to point to your Railway staging URL instead of the production backend:
        ```javascript
        const BACKEND_URL = "https://commerce-support-staging.up.railway.app/api/chat";
        ```
    *   Save changes.
3.  **Preview and QA test**:
    *   Click **Actions > Preview** on the duplicate theme.
    *   Interact with the chat widget. Verify that conversations and logs are successfully sent to the Staging Railway backend and Supabase test database, leaving the production data sources clean.
