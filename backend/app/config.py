import os
import pathlib
from dotenv import load_dotenv

# Locate the .env file in the backend directory (one level up from app/)
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# Load environment variables from the specific path
load_dotenv(dotenv_path=ENV_PATH)

class Settings:
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = os.getenv("HOST", "127.0.0.1")
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "")
    ADMIN_DASHBOARD_TOKEN: str = os.getenv("ADMIN_DASHBOARD_TOKEN", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # Amazon SP-API Configuration
    AMAZON_LWA_CLIENT_ID: str = os.getenv("AMAZON_LWA_CLIENT_ID", "")
    AMAZON_LWA_CLIENT_SECRET: str = os.getenv("AMAZON_LWA_CLIENT_SECRET", "")
    AMAZON_LWA_REFRESH_TOKEN: str = os.getenv("AMAZON_LWA_REFRESH_TOKEN", "")
    AMAZON_AWS_ACCESS_KEY: str = os.getenv("AMAZON_AWS_ACCESS_KEY", "")
    AMAZON_AWS_SECRET_KEY: str = os.getenv("AMAZON_AWS_SECRET_KEY", "")
    AMAZON_ROLE_ARN: str = os.getenv("AMAZON_ROLE_ARN", "")
    AMAZON_REGION: str = os.getenv("AMAZON_REGION", "")
    AMAZON_MARKETPLACE_ID: str = os.getenv("AMAZON_MARKETPLACE_ID", "")
    
    # MiniMax Configuration
    MINIMAX_API_KEY: str = os.getenv("MINIMAX_API_KEY", "")
    MINIMAX_MODEL: str = os.getenv("MINIMAX_MODEL", "MiniMax-M2.7")
    MINIMAX_CONNECT_TIMEOUT: float = float(os.getenv("MINIMAX_CONNECT_TIMEOUT_SECONDS", "3.0"))
    MINIMAX_READ_TIMEOUT: float = float(os.getenv("MINIMAX_READ_TIMEOUT_SECONDS", "15.0"))
    ENVIRONMENT: str = os.getenv("APP_ENV", "PRODUCTION")


# Instantiate settings to be imported by other backend modules
settings = Settings()

# Safe startup logs
url_set = bool(settings.SUPABASE_URL and "placeholder" not in settings.SUPABASE_URL and settings.SUPABASE_URL != "")
key_set = bool(settings.SUPABASE_SERVICE_ROLE_KEY and "placeholder" not in settings.SUPABASE_SERVICE_ROLE_KEY and settings.SUPABASE_SERVICE_ROLE_KEY != "")

print(f"--- Environment Configuration ---")
print(f"Loading .env from: {ENV_PATH}")
print(f"SUPABASE_URL configured: {url_set}")
print(f"SUPABASE_SERVICE_ROLE_KEY configured: {key_set}")
print(f"----------------------------------")
# Trigger hot reload comment

