# Commerce Support Console: Roadmap Status

This file tracks the operational readiness of all messaging channels, integrations, and architectural modules.

---

## 1. Shopify Integration (Active / Dev Ready)
*   **Customer Widget**: Live polling interface on theme duplicate, client-side 5-question limit active. Connected to production Railway API host, with offline status warnings removed and fallback support emails configured.
*   **Automatic Handlers**: Keyword/RAG matching for local knowledge bases, MiniMax AI Support Brain active.
*   **Takeover Mechanics**: Human takeover triggers, auto-escalation keywords, live polling for agent replies.
*   **Archive & Delete Controls**: Check constraint bypass archiving, permanent cascading deletion across child tables (`reply_drafts`, `staff_notes`, `agent_replies`) and logs.
*   **Staff UX**: Needs Agent renamed, count badges, two-column filter pills grid.

---

## 2. AI Support Brain Integration (Active)
*   **Heuristics Intent Classifier**: 15 distinct intent patterns.
*   **Safety Routing**: Forced agent escalation for fire/smoke hazards, legal threats, billing, tracking, and complaints.
*   **MiniMax LLM Layer**: System prompt constructs custom responses using knowledge contexts and turn history.
*   **Rules Fallback**: Seamless local search failsafe on connection failure or missing environment keys.
*   **Serialization Pipeline**: Encoded JSON metadata packed in `matched_source` field, zero-ddl schema compatible.
*   **Knowledge Packs**: Seeding pack containing UKCA & CE safety certification, private land safety rules, warranty and returns policy contexts.

---

## 3. Future Channel Roadmaps (Locked / Planned)

### Amazon SP-API Integrations
*   **Sandbox (Dev/Test)**: Connection structures defined.
*   **Live Channel**: Locked. Planned SP-API standard seller messaging sync, order retrieval templates.

### eBay & TikTok Shop
*   **Status**: Coming Soon.
*   **Goals**: API hookups for merchant notifications, chat synchronization.

### Email Escalations & Alerts
*   **Status**: Blueprint drafted (`EMAIL_ESCALATION_PLAN.md`).
*   **Goals**: Automatic ticket alerts utilizing the Resend API when needs_escalation is flagged.

### Media Ingestion
*   **Status**: Blueprint drafted (`ATTACHMENT_UPLOAD_PLAN.md`).
*   **Goals**: Support ticket evidence uploading targeting Supabase Storage.

### Shopify Order Lookup API
*   **Status**: Locked (Placeholder visible).
*   **Goals**: Secure customer verification, guest verification levels, billing postcode lookups, automated order status replies.
