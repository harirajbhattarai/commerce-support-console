from typing import Optional
from fastapi import Header, Query, HTTPException
from app.config import settings

async def verify_admin_token(
    x_admin_token: Optional[str] = Header(None, alias="X-Admin-Token"),
    token: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None)
):
    expected_token = settings.ADMIN_DASHBOARD_TOKEN
    if not expected_token:
        return
        
    provided_token = x_admin_token or token
    if authorization and authorization.lower().startswith("bearer "):
        parts = authorization.split(" ")
        if len(parts) > 1:
            provided_token = parts[1]
            
    if provided_token != expected_token:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid or missing admin token.")
