import logging
from typing import Optional, List, Dict, Any
from app.database import supabase_client

logger = logging.getLogger("uvicorn.error")

class KnowledgeService:
    @staticmethod
    async def get_product_by_sku(sku: str, store_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieves a product from the local Supabase 'products' table by its SKU.
        """
        if not supabase_client:
            logger.warning("Supabase client is not initialized in KnowledgeService.")
            return None
        try:
            query = supabase_client.table("products").select("*").eq("sku", sku)
            if store_id:
                query = query.eq("store_id", store_id)
            response = query.execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error in get_product_by_sku for SKU '{sku}': {e}")
            return None

    @staticmethod
    async def get_product_by_asin(asin: str, store_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieves a product from the local Supabase 'products' table by its ASIN.
        """
        if not supabase_client:
            logger.warning("Supabase client is not initialized in KnowledgeService.")
            return None
        try:
            query = supabase_client.table("products").select("*").eq("asin", asin)
            if store_id:
                query = query.eq("store_id", store_id)
            response = query.execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error in get_product_by_asin for ASIN '{asin}': {e}")
            return None

    @staticmethod
    async def get_knowledge_for_product(product_id: str, issue_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves structured diagnostic and policy knowledge entries for a product from
        the local 'product_knowledge' table, optionally filtered by issue category.
        """
        if not supabase_client:
            logger.warning("Supabase client is not initialized in KnowledgeService.")
            return []
        try:
            query = supabase_client.table("product_knowledge").select("*").eq("product_id", product_id)
            if issue_type:
                # Map high-level console issue types to database knowledge types
                mapped_types = []
                if issue_type == "faulty_product":
                    mapped_types = ["troubleshooting", "reset_guide", "usage"]
                elif issue_type == "battery_or_safety_issue":
                    mapped_types = ["battery", "safety", "charging"]
                elif issue_type == "return_request":
                    mapped_types = ["returns", "warranty"]
                elif issue_type == "cancellation_request":
                    mapped_types = ["cancellation"]
                elif issue_type == "delivery_status" or issue_type == "item_not_received":
                    mapped_types = ["delivery"]
                else:
                    mapped_types = [issue_type]
                query = query.in_("knowledge_type", mapped_types)
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error in get_knowledge_for_product for product '{product_id}': {e}")
            return []

    @staticmethod
    async def get_support_knowledge(
        query: str,
        product_type: Optional[str] = None,
        issue_type: Optional[str] = None,
        channel: Optional[str] = None,
        store_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Searches the local cache (products, product_knowledge, and support_articles)
        for support answers matching the query, product type, and channel.
        Returns a structured dictionary of results or an empty lookup response.
        """
        if not supabase_client:
            return {"success": False, "reason": "knowledge_not_found", "message": "Supabase client not initialized"}
        
        try:
            matched_products = []
            matched_knowledge = []
            matched_articles = []
            
            query_lower = query.lower()

            # 1. Attempt to resolve product_type and issue_type if not provided
            if not product_type:
                if any(w in query_lower for w in ["hoverboard", "scooter", "board", "segway", "charger", "battery"]):
                    product_type = "hoverboard"
                elif any(w in query_lower for w in ["diffuser", "mist", "aroma", "humidifier"]):
                    product_type = "diffuser"

            if not issue_type:
                if any(w in query_lower for w in ["smoke", "smell", "burn", "burning", "hot", "fire", "spark", "swelling", "dangerous", "unsafe"]):
                    issue_type = "battery"
                elif any(w in query_lower for w in ["reset", "calibrate", "calibration", "beeping"]):
                    issue_type = "reset_guide"
                elif any(w in query_lower for w in ["charging", "charge", "plug"]):
                    issue_type = "charging"
                elif any(w in query_lower for w in ["battery"]):
                    issue_type = "battery"

            # 2. Search products by type or title
            prod_query = supabase_client.table("products").select("*")
            if store_id:
                prod_query = prod_query.eq("store_id", store_id)
            if product_type:
                prod_query = prod_query.eq("product_type", product_type)
            else:
                # Fallback keyword match in product title
                # We extract first word of query as simple match search
                words = [w for w in query_lower.split() if len(w) > 3]
                if words:
                    prod_query = prod_query.ilike("product_title", f"%{words[0]}%")
            
            prod_resp = prod_query.execute()
            if prod_resp.data:
                matched_products = prod_resp.data
                # Fetch knowledge entries for all matching products
                for prod in matched_products:
                    kn_entries = await KnowledgeService.get_knowledge_for_product(prod["product_id"], issue_type)
                    for entry in kn_entries:
                        # Channel filtering guard
                        if channel and entry.get("applies_to_channel") not in ["all", channel]:
                            continue
                        matched_knowledge.append(entry)

            # 3. Search general support articles table by query keywords
            keywords = [w for w in query_lower.split() if len(w) > 3]
            if keywords:
                art_query = supabase_client.table("support_articles").select("*")
                if store_id:
                    art_query = art_query.eq("store_id", store_id)
                # Search using the first matched keyword for simplicity in standard SQL
                art_resp = art_query.ilike("content", f"%{keywords[0]}%").execute()
                if art_resp.data:
                    matched_articles = art_resp.data

            # 4. Check if any results were found
            if not matched_products and not matched_knowledge and not matched_articles:
                return {
                    "success": False,
                    "reason": "knowledge_not_found"
                }

            return {
                "success": True,
                "products": matched_products,
                "knowledge": matched_knowledge,
                "articles": matched_articles
            }
        except Exception as e:
            logger.error(f"Error executing get_support_knowledge for query '{query}': {e}")
            return {
                "success": False,
                "reason": "knowledge_not_found"
            }
