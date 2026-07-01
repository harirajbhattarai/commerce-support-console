import logging
from typing import Dict, Any, List
from app.config import settings

logger = logging.getLogger("uvicorn.error")

AMAZON_CONFIG_KEYS = [
    "AMAZON_LWA_CLIENT_ID",
    "AMAZON_LWA_CLIENT_SECRET",
    "AMAZON_LWA_REFRESH_TOKEN",
    "AMAZON_REGION",
    "AMAZON_MARKETPLACE_ID"
]


def is_valid_value(value: str) -> bool:
    """Check if the variable is set and is not a placeholder/example value."""
    if not value or value.strip() == "":
        return False
    
    val_lower = value.lower()
    placeholders = ["placeholder", "example", "your-", "amzn1.application-oa2-client.your"]
    for p in placeholders:
        if p in val_lower:
            return False
            
    return True

def get_amazon_config_status() -> Dict[str, Any]:
    """
    Validates Amazon SP-API configuration parameters without exposing secret keys.
    Returns diagnostic health dictionary.
    """
    missing_vars: List[str] = []
    
    for key in AMAZON_CONFIG_KEYS:
        val = getattr(settings, key, "")
        if not is_valid_value(val):
            missing_vars.append(key)
            
    configured = len(missing_vars) == 0
    mode = "ready_for_sp_api_test" if configured else "not_connected"
    
    return {
        "configured": configured,
        "missing_env_vars": missing_vars,
        "mode": mode
    }

async def get_lwa_access_token() -> Dict[str, Any]:
    """
    Exchanges the AMAZON_LWA_REFRESH_TOKEN for a temporary access token from Amazon LWA.
    Returns a dictionary indicating success or failure, along with safe metadata.
    """
    import httpx
    
    # 1. First, check if configured
    status = get_amazon_config_status()
    if not status["configured"]:
        return {
            "success": False,
            "error": "Connector not fully configured",
            "missing_env_vars": status["missing_env_vars"]
        }
    
    url = "https://api.amazon.com/auth/o2/token"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": settings.AMAZON_LWA_REFRESH_TOKEN,
        "client_id": settings.AMAZON_LWA_CLIENT_ID,
        "client_secret": settings.AMAZON_LWA_CLIENT_SECRET
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload, timeout=10.0)
            
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            expires_in = data.get("expires_in")
            if access_token:
                return {
                    "success": True,
                    "access_token_received": True,
                    "expires_in": expires_in,
                    "access_token": access_token
                }
            else:
                return {
                    "success": False,
                    "error": "No access_token found in response body"
                }
        else:
            # Safe error logging without exposing credentials
            logger.error(f"LWA token exchange failed with status code {response.status_code}: {response.text}")
            return {
                "success": False,
                "error": f"LWA server returned status code {response.status_code}"
            }
            
    except Exception as e:
        logger.error(f"Exception during LWA token exchange: {str(e)}")
        return {
            "success": False,
            "error": f"Connection exception: {str(e)}"
        }

async def get_sandbox_marketplaces() -> Dict[str, Any]:
    """
    Exchanges LWA refresh token and calls the read-only SP-API sandbox endpoint:
    GET /sellers/v1/marketplaceParticipations
    Returns sanitized data without exposing tokens or secrets.
    """
    import httpx
    
    # 1. Fetch access token first
    token_res = await get_lwa_access_token()
    if not token_res.get("success"):
        return {
            "success": False,
            "token_exchange": "failed",
            "error": token_res.get("error")
        }
    
    access_token = token_res.get("access_token")
    
    # 2. Map region to sandbox base URL
    region = getattr(settings, "AMAZON_REGION", "eu-west-1")
    reg_lower = region.lower().strip()
    
    if reg_lower in ["us-east-1", "us-east-2"]:
        base_url = "https://sandbox.sellingpartnerapi-na.amazon.com"
    elif reg_lower in ["us-west-2"]:
        base_url = "https://sandbox.sellingpartnerapi-fe.amazon.com"
    else:
        base_url = "https://sandbox.sellingpartnerapi-eu.amazon.com"
        
    url = f"{base_url}/sellers/v1/marketplaceParticipations"
    headers = {
        "x-amz-access-token": access_token,
        "Accept": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=15.0)
            
        if response.status_code == 200:
            data = response.json()
            # Sanitize the marketplace list
            raw_list = data.get("payload", [])
            sanitized_marketplaces = []
            
            for item in raw_list:
                marketplace = item.get("marketplace", {})
                participation = item.get("participation", {})
                sanitized_marketplaces.append({
                    "marketplace_id": marketplace.get("id"),
                    "country_code": marketplace.get("countryCode"),
                    "name": marketplace.get("name"),
                    "default_currency_code": marketplace.get("defaultCurrencyCode"),
                    "is_participating": participation.get("isParticipating")
                })
                
            return {
                "success": True,
                "sp_api_call": "success",
                "marketplace_count": len(sanitized_marketplaces),
                "marketplaces": sanitized_marketplaces
            }
        else:
            logger.error(f"SP-API sandbox call failed with status code {response.status_code}: {response.text}")
            return {
                "success": False,
                "sp_api_call": "failed",
                "error": f"SP-API server returned status code {response.status_code}"
            }
            
    except Exception as e:
        logger.error(f"Exception during SP-API sandbox call: {str(e)}")
        return {
            "success": False,
            "sp_api_call": "failed",
            "error": f"Connection exception: {str(e)}"
        }


async def get_sandbox_orders(marketplace_ids: List[str] = None, created_after: str = None) -> Dict[str, Any]:
    """
    Exchanges LWA refresh token and calls the Orders API sandbox endpoint:
    GET /orders/v0/orders
    Sanitizes response to strictly exclude ShippingAddress, BuyerInfo, and BuyerTaxInformation.
    """
    import httpx
    
    # 1. Fetch access token first
    token_res = await get_lwa_access_token()
    if not token_res.get("success"):
        return {
            "success": False,
            "token_exchange": "failed",
            "error": token_res.get("error")
        }
    
    access_token = token_res.get("access_token")
    
    # 2. Map region to sandbox base URL
    region = getattr(settings, "AMAZON_REGION", "eu-west-1")
    reg_lower = region.lower().strip()
    
    if reg_lower in ["us-east-1", "us-east-2"]:
        base_url = "https://sandbox.sellingpartnerapi-na.amazon.com"
    elif reg_lower in ["us-west-2"]:
        base_url = "https://sandbox.sellingpartnerapi-fe.amazon.com"
    else:
        base_url = "https://sandbox.sellingpartnerapi-eu.amazon.com"
        
    url = f"{base_url}/orders/v0/orders"
    
    # 3. Handle query parameters
    if not marketplace_ids:
        # ATVPDKIKX0DER is the standard sandbox test marketplace ID
        marketplace_ids = ["ATVPDKIKX0DER"]
        
    if not created_after:
        # TEST_CASE_200 is the standard sandbox test case identifier
        created_after = "TEST_CASE_200"
        
    params = {
        "MarketplaceIds": ",".join(marketplace_ids),
        "CreatedAfter": created_after
    }
    
    headers = {
        "x-amz-access-token": access_token,
        "Accept": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params, timeout=15.0)
            
        if response.status_code == 200:
            data = response.json()
            payload = data.get("payload", {})
            orders_list = payload.get("Orders", [])
            
            sanitized_orders = []
            for order in orders_list:
                # Keep only safe metadata fields.
                # Explicitly omit ShippingAddress, BuyerInfo, BuyerTaxInformation
                sanitized_orders.append({
                    "amazon_order_id": order.get("AmazonOrderId"),
                    "purchase_date": order.get("PurchaseDate"),
                    "last_update_date": order.get("LastUpdateDate"),
                    "order_status": order.get("OrderStatus"),
                    "fulfillment_channel": order.get("FulfillmentChannel"),
                    "sales_channel": order.get("SalesChannel"),
                    "order_type": order.get("OrderType"),
                    "number_of_items_shipped": order.get("NumberOfItemsShipped"),
                    "number_of_items_unshipped": order.get("NumberOfItemsUnshipped")
                })
                
            return {
                "success": True,
                "sp_api_call": "success",
                "token_exchange": "success",
                "order_count": len(sanitized_orders),
                "orders": sanitized_orders
            }
        else:
            logger.error(f"SP-API Orders sandbox call failed with status code {response.status_code}: {response.text}")
            return {
                "success": False,
                "sp_api_call": "failed",
                "token_exchange": "success",
                "error": f"SP-API server returned status code {response.status_code}"
            }
            
    except Exception as e:
        logger.error(f"Exception during SP-API Orders sandbox call: {str(e)}")
        return {
            "success": False,
            "sp_api_call": "failed",
            "token_exchange": "success",
            "error": f"Connection exception: {str(e)}"
        }


async def get_sandbox_order(order_id: str) -> Dict[str, Any]:
    """
    Exchanges LWA refresh token and calls the Orders API sandbox endpoint:
    GET /orders/v0/orders/{orderId}
    Sanitizes response to strictly exclude ShippingAddress, BuyerInfo, and BuyerTaxInformation.
    """
    import httpx
    
    # 1. Fetch access token first
    token_res = await get_lwa_access_token()
    if not token_res.get("success"):
        return {
            "success": False,
            "token_exchange": "failed",
            "error": token_res.get("error")
        }
    
    access_token = token_res.get("access_token")
    
    # 2. Map region to sandbox base URL
    region = getattr(settings, "AMAZON_REGION", "eu-west-1")
    reg_lower = region.lower().strip()
    
    if reg_lower in ["us-east-1", "us-east-2"]:
        base_url = "https://sandbox.sellingpartnerapi-na.amazon.com"
    elif reg_lower in ["us-west-2"]:
        base_url = "https://sandbox.sellingpartnerapi-fe.amazon.com"
    else:
        base_url = "https://sandbox.sellingpartnerapi-eu.amazon.com"
        
    # Map mock order IDs to the required sandbox test case ID "TEST_CASE_200"
    sandbox_order_id = order_id
    if order_id in ["902-1845936-5435065", "902-8745147-1934268"]:
        sandbox_order_id = "TEST_CASE_200"
        
    url = f"{base_url}/orders/v0/orders/{sandbox_order_id}"
    headers = {
        "x-amz-access-token": access_token,
        "Accept": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=15.0)
            
        if response.status_code == 200:
            data = response.json()
            order = data.get("payload", {})
            
            # Map mock status/fields to show both Shipped and Unshipped behaviors in the sandbox
            custom_status = order.get("OrderStatus")
            custom_fulfillment = order.get("FulfillmentChannel")
            custom_shipped = order.get("NumberOfItemsShipped")
            custom_unshipped = order.get("NumberOfItemsUnshipped")
            
            if order_id == "902-8745147-1934268":
                custom_status = "Shipped"
                custom_fulfillment = "AFN"
                custom_shipped = 1
                custom_unshipped = 0
            elif order_id == "902-1845936-5435065":
                custom_status = "Unshipped"
                custom_fulfillment = "MFN"
                custom_shipped = 0
                custom_unshipped = 1

            # Sanitize order fields - explicitly exclude ShippingAddress, BuyerInfo, BuyerTaxInformation
            sanitized_order = {
                "amazon_order_id": order_id,
                "order_status": custom_status,
                "purchase_date": order.get("PurchaseDate"),
                "last_update_date": order.get("LastUpdateDate"),
                "fulfillment_channel": custom_fulfillment,
                "sales_channel": order.get("SalesChannel"),
                "order_type": order.get("OrderType"),
                "number_of_items_shipped": custom_shipped,
                "number_of_items_unshipped": custom_unshipped
            }
            
            return {
                "success": True,
                "sp_api_call": "success",
                "token_exchange": "success",
                "order": sanitized_order
            }
        else:
            logger.error(f"SP-API Order lookup sandbox call failed with status code {response.status_code}: {response.text}")
            return {
                "success": False,
                "sp_api_call": "failed",
                "token_exchange": "success",
                "error": f"SP-API server returned status code {response.status_code}"
            }
            
    except Exception as e:
        logger.error(f"Exception during SP-API Order lookup sandbox call: {str(e)}")
        return {
            "success": False,
            "sp_api_call": "failed",
            "token_exchange": "success",
            "error": f"Connection exception: {str(e)}"
        }




