# HCHAHAL Support Console - Live Deployment Readiness Plan

This document maps out the architectural transitions, configuration requirements, and security checklists necessary to migrate the FastAPI support backend and storefront chat widgets from a local dev server to a cloud hosting environment.

---

## 1. Local Development vs. Target Live Setup

| Component | Local Dev Setup | Target Live Setup |
| :--- | :--- | :--- |
| **Backend Host** | Local host (`127.0.0.1:8000` via Uvicorn reload) | Cloud PaaS container (public HTTPS endpoint) |
| **Database** | Supabase Sandbox project | Supabase Production/Staging isolated schema |
| **CORS Origins** | Wildcard `*` | Restricted whitelist (Shopify store domains + local dev) |
| **Admin Route** | Unauthenticated `/admin-dashboard.html` | Authenticated (Basic Auth / OAuth) admin panel |
| **Widget Integration** | Hardcoded `http://127.0.0.1:8000` origin | Dynamic pathing / configured public HTTPS gateway |

---

## 2. Cloud Hosting Strategy & Options

### Recommendation: Railway or Render (First Choice)
*   **Why**: These platforms are optimized for FastAPI deployments, support automatic SSL certificates, handle continuous deployment via GitHub triggers, and manage environment configuration files out of the box.
*   **Pricing**: Minimal resource requirement; standard CPU/RAM tier is sufficient for REST polling MVP.
*   **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` (binding to `0.0.0.0` is required for cloud load balancers to route traffic to the container).

### Why NOT AWS (EC2/ECS) yet
*   **Complexity**: Configuring AWS VPCs, ALB routing, IAM roles, and Certificate Manager involves significant administrative overhead for an MVP prototype.
*   **Velocity**: Render and Railway allow 5-minute deployments without manual infrastructure maintenance.

---

## 3. Environment Variables (Required Secrets & Configuration)

Configure these variables inside your hosting provider's settings dashboard (never commit them to VCS):

```bash
# FastAPI settings
PORT=8000
HOST=0.0.0.0

# CORS Whitelist (Comma-separated values)
# Include your local test environments and production store URLs
ALLOWED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:5173,http://localhost:5173,https://hoverboardstore.co.uk,https://www.hoverboardstore.co.uk

# Supabase Production Database settings
SUPABASE_URL=https://your-live-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-live-supabase-service-role-key

# Amazon SP-API Configuration (Keep completely isolated to Sandbox mode)
AMAZON_LWA_CLIENT_ID=amzn1.application-oa2-client.your-client-id
AMAZON_LWA_CLIENT_SECRET=your-lwa-client-secret
AMAZON_LWA_REFRESH_TOKEN=Atzr|your-lwa-refresh-token
AMAZON_REGION=eu-west-1
AMAZON_MARKETPLACE_ID=A1F83G8C2ARO7P
```

---

## 4. Production Security & Safeguards

> [!CAUTION]
> **Admin Dashboard Protection**: In local dev, `/admin-dashboard.html` is accessible directly by visiting the URL. In production, this HTML path must be protected. You must implement FastAPI middleware (e.g. HTTP Basic Authentication) or a login gateway before deploying publicly.

### Database Environment Protection
*   Do not reuse your local development Supabase database for production testing.
*   Ensure that the `agent_replies` table exists on the target database schema to prevent REST polling failures.

---

## 5. Shopify Integration URL Updates

When deploying the storefront widget live, update the hardcoded host references:
1.  **Widget Script**: In [widget.js](file:///Volumes/XTREM/BITLEAF-SYTEM/50-59%20SYSTEMS/52%20AI%20Agents/GOOGLE_I_O_2026/ANTIGRAVITY_AGENT/frontend/widget.js#L6) and [hoverboard-chat-widget.js](file:///Volumes/XTREM/BITLEAF-SYTEM/50-59%20SYSTEMS/52%20AI%20Agents/GOOGLE_I_O_2026/ANTIGRAVITY_AGENT/frontend/shopify-widget/hoverboard-chat-widget.js#L10), change `http://127.0.0.1:8000` to the public HTTPS URL of your cloud server (e.g., `https://hchahal-console.up.railway.app`).
2.  **Shopify Liquid snippet**: In [install-snippet.liquid](file:///Volumes/XTREM/BITLEAF-SYTEM/50-59%20SYSTEMS/52%20AI%20Agents/GOOGLE_I_O_2026/ANTIGRAVITY_AGENT/frontend/shopify-widget/install-snippet.liquid#L11), change `apiHost` variable to the public URL.

---

## 6. Pre-Flight Production Health Checklist

Before signing off on active routing:
- [ ] `/health` endpoint returns `"status": "healthy"` and `"database": "connected"`.
- [ ] `/api/knowledge/search?q=hoverboard` is active and retrieves cached knowledge.
- [ ] `agent_replies` table exists and is writable (prevents storefront widget 500 errors).
- [ ] Admin panel access is protected by authentication challenges.
- [ ] SP-API Amazon connections resolve only against sandbox endpoints (strictly read-only).
- [ ] Amazon composer controls show draft-only workflows; live message sending remains blocked.

---

## 7. Rollback Plan

If the live deployment fails or causes storefront script errors:
1.  **PaaS Rollback**: Trigger a Git rollback in Railway or Render to redeploy the previous stable build.
2.  **Liquid Snippet Bypass**: In the Shopify admin theme editor, comment out or remove the `{% include 'install-snippet' %}` tag from `theme.liquid` to instantly restore normal storefront functionality.
