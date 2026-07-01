# Shopify Live Production Go-Live Checklist & Resource Guide

This guide establishes the checklist and validation procedures for publishing the HCHAHAL Support Console widget live on the primary Shopify theme.

---

## 1. Pre-Publish Validation Checklist

Before setting the duplicate theme as the live/published theme on Shopify, execute the following validation steps:

### [ ] Step A: Theme Duplication and Sandbox Testing
- Verify that testing was done entirely on a duplicate theme template first (e.g. `HCS Support Sandbox Theme`).
- Verify that CSS overlays, font face styling, and margins behave correctly on both desktop and mobile viewports.

### [ ] Step B: Retire Legacy System
- Confirm that the old Heroku chatbot script references (e.g., `<script src="https://hchahal-support-bot.herokuapp.com/..."></script>`) have been fully commented out or deleted from `layout/theme.liquid`.
- Verify that no duplicate chat widgets or floating action buttons render on the storefront.

### [ ] Step C: Production Railway Endpoint Configuration
- Confirm that the snippet `install-snippet.liquid` uses the production Railway base URL:
  `https://commerce-support-console-production.up.railway.app`
- Confirm that no `127.0.0.1:8000` or local dev URLs remain in the storefront assets.

### [ ] Step D: Admin Dashboard Security Token Rotation
- Rotate the `ADMIN_DASHBOARD_TOKEN` environment variable on the Railway console before launch.
- Confirm that the `/admin-dashboard.html` panel redirects requests without the new token.
- **CRITICAL**: Verify that the `ADMIN_DASHBOARD_TOKEN` is NEVER exposed or referenced inside customer-facing widgets or themes.

---

## 2. Emergency Rollback Plan

If unexpected crashes, styling breaks, or database connection pool issues occur after publish, follow these rollback guidelines:

1. **Revert Live Theme**:
   - In Shopify Admin, navigate to **Online Store** -> **Themes**.
   - Locate the previous backup theme (e.g. `Theme Backup - Pre Support Integration`).
   - Click **Actions** -> **Publish**. This immediately removes the widget script from the storefront for visitors.
2. **FastAPI Backend Offline Mode**:
   - If Supabase or Railway experiences downtime but the theme cannot be rolled back immediately, remove the `install-snippet.liquid` include statement from `layout/theme.liquid` directly in the theme code editor.

---

## 3. Real-Time Production Monitoring

### Railway Container Logs
Monitor container stdout logs in the Railway Dashboard:
- Look for `HTTP/1.1 500 Internal Server Error` on API endpoints `/api/chat` or `/api/agent-replies`.
- Ensure Supabase Connection Pool limits are not exceeded (keep logs clear of `Connection pool full` errors).

### Supabase Database Checks
Query tables regularly to monitor chatbot activity:
- `chat_logs`: Check that customer queries save with correct confidence values and matched sources. Filter by `store_id` and `session_id`.
- `agent_replies`: Verify that replies created by support agents in the dashboard console write with `status: "sent"`.

---

## 4. Server-Side Usage Limit Plan (Next Phase)

### Current Client-Side Limit
- Currently, the storefront widget uses a client-side visitor threshold of **5 questions** stored inside the browser's `sessionStorage` (under key `hbs_chat_question_count_{store_id}`).
- Once `sessionStorage` registers 5 requests, further queries are intercepted client-side.
- *Risk*: Tech-savvy visitors can easily bypass this by clearing `sessionStorage` or editing widget code locally.

### Proposed Server-Side Limit Design
To prevent API depletion and prevent spam or scraping abuse, we plan to implement a stronger server-side rate limit:

- **Database Inquiries**:
  No schema changes are required. The `chat_logs` table already tracks `session_id`, `created_at`, and `user_message`.
  We can query the count of logs matching `session_id` within the last 24 hours:
  ```sql
  SELECT count(*) FROM chat_logs WHERE session_id = :session_id AND created_at > now() - interval '24 hours';
  ```
- **Middleware Rate Limiting**:
  Add a FastAPI rate limit dependency on the `/api/chat` endpoint using a library like `slowapi` or custom IP tracking bucket to limit requests by client IP address (to prevent session key rotation abuse).
