from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from app.services.knowledge_service import KnowledgeService
from app.auth import verify_admin_token

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

@router.get("/product/sku/{sku}", dependencies=[Depends(verify_admin_token)])
async def get_product_by_sku_endpoint(sku: str, store_id: Optional[str] = None):
    """
    Local debug route to retrieve a product by its SKU.
    """
    product = await KnowledgeService.get_product_by_sku(sku, store_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with SKU '{sku}' not found in local cache."
        )
    return product

@router.get("/product/asin/{asin}", dependencies=[Depends(verify_admin_token)])
async def get_product_by_asin_endpoint(asin: str, store_id: Optional[str] = None):
    """
    Local debug route to retrieve a product by its ASIN.
    """
    product = await KnowledgeService.get_product_by_asin(asin, store_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ASIN '{asin}' not found in local cache."
        )
    return product

@router.get("/search")
async def search_knowledge_endpoint(
    q: Optional[str] = Query(None, description="The query string to search for"),
    query: Optional[str] = Query(None, description="Fallback query string to search for"),
    product_type: Optional[str] = Query(None, description="Filter search by product type (e.g., hoverboard, diffuser)"),
    issue_type: Optional[str] = Query(None, description="Filter search by issue category code"),
    channel: Optional[str] = Query(None, description="Filter search by applies_to_channel target (e.g. shopify, amazon)"),
    store_id: Optional[str] = Query(None, description="Filter search by store ID environment")
):
    """
    Local debug route to search the local knowledge base (products, knowledge base, articles).
    """
    # 1. Prioritize q, fallback to query
    resolved_query = q or query
    
    # 2. Return friendly JSON error if neither is provided
    if not resolved_query:
        return {
            "ok": False,
            "reason": "missing_query",
            "message": "Provide q or query parameter."
        }
        
    result = await KnowledgeService.get_support_knowledge(
        query=resolved_query,
        product_type=product_type,
        issue_type=issue_type,
        channel=channel,
        store_id=store_id
    )
    return result
