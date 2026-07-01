# Architecture Decision: Master Commerce Brain Abstraction & Local Support Cache

This document outlines the architectural decision to decouple the HCHAHAL Support Console's draft reply engine from the local database storage models, establishing a future-proof integration path with the company-wide **Master Commerce Brain**.

---

## 1. Context & Objectives

*   **Master Commerce Brain**: The upcoming, unified company-wide database and search index that acts as the final source of truth for products, stock, safety sheets, and global policies.
*   **Support Console Local Cache**: The database tables (`products` and `product_knowledge`) created in our local Supabase instance are designated strictly as a **temporary support knowledge cache / prototype** to enable developer testing of draft reply generation.
*   **Decoupling Objective**: The reply draft generator and triage engine must not directly query local tables. Instead, all lookups must route through an abstraction layer. This allows us to hot-swap the backend data provider to the Master Commerce Brain later without altering the draft logic.

---

## 2. Abstraction Layer Design: `knowledge_service.py`

We will implement a central service module to act as the query adapter:
*   **Module Path**: `backend/app/services/knowledge_service.py`
*   **Responsibility**: Encapsulate all database lookups for policy documents, product definitions, and troubleshooting rules.
*   **Current State**: Under the hood, this service queries the local Supabase `products` and `product_knowledge` tables.
*   **Future State**: Can be refactored to consume the Master Commerce Brain REST or gRPC APIs with zero changes to the calling API routers.

### Planned Service Interface (Skeleton Outline)

```python
from typing import Optional, List, Dict, Any

class KnowledgeService:
    @staticmethod
    async def get_product_knowledge(
        store_id: str,
        sku: Optional[str] = None,
        asin: Optional[str] = None,
        channel: str = "shopify"
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves structured product details and troubleshooting guides.
        Searches local 'products' and 'product_knowledge' tables.
        """
        pass

    @staticmethod
    async def get_policy_knowledge(
        store_id: str,
        category: str,
        channel: str = "all"
    ) -> List[Dict[str, Any]]:
        """
        Retrieves policy guidelines (e.g., returns_policy, delivery_policy)
        from either 'support_articles' or 'product_knowledge'.
        """
        pass
```

---

## 3. Data Seeding & Scale Rules

*   **No Bulk Seeding**: To prevent database clutter and avoid maintaining duplicate catalog entries, do not load large sets of product catalogs into the local Supabase cache.
*   **Minimal Verification Records**: Only seed small, human-reviewed test records (such as one hoverboard and one aroma diffuser product) to validate conditional triage rules during prototype testing.

---

## 4. Safety Guardrails & Compliance

*   **No Live Connections**: Under no circumstances will this console connect to live Amazon production environments or credentials.
*   **No Messaging API**: Direct integration with the Amazon Seller Central Solicitations/Messaging API is prohibited.
*   **No Auto-Reply**: The reply composer remains strictly human-in-the-loop. Suggested drafts are generated locally, require manual revision, and must be copied and pasted to Seller Central manually.
