import logging
from typing import Optional
from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger("uvicorn.error")

supabase_client: Optional[Client] = None

# Check if keys are set and not placeholders
url_valid = settings.SUPABASE_URL and "placeholder" not in settings.SUPABASE_URL and settings.SUPABASE_URL != ""
key_valid = settings.SUPABASE_SERVICE_ROLE_KEY and "placeholder" not in settings.SUPABASE_SERVICE_ROLE_KEY and settings.SUPABASE_SERVICE_ROLE_KEY != ""

if url_valid and key_valid:
    try:
        supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        logger.info("Supabase client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
else:
    logger.warning(
        "Supabase credentials are not configured or are placeholders. "
        "Chat logging to Supabase will be bypassed, and the bot will run in offline/fallback mode."
    )
