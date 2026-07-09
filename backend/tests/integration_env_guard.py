import pytest
from urllib.parse import urlparse
from app.config import settings

# This is the single version-controlled source of truth for the staging environment identity.
# It prevents self-approval where a local environment file could redefine the approved target.
APPROVED_STAGING_PROJECT_REF = "njppfsyfqsqwkuxkkjaq"

def verify_staging_environment():
    """
    Central guard for write-capable integration tests.
    Ensures that tests only run against the explicitly approved staging Supabase project.
    """
    url = settings.SUPABASE_URL
    if not url or "placeholder" in url:
        pytest.skip("Refusing to run write-capable integration tests against a non-approved staging Supabase target. (URL missing or placeholder)")
        
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            pytest.skip("Refusing to run write-capable integration tests against a non-approved staging Supabase target. (Malformed URL)")
    except Exception:
        pytest.skip("Refusing to run write-capable integration tests against a non-approved staging Supabase target. (Malformed URL)")
        
    # Extract project ref from hostname (e.g., abcdefg.supabase.co -> abcdefg)
    project_ref = hostname.split(".")[0]
    
    # Production project reference is dztfwxehqbyubneeflyy
    if project_ref == "dztfwxehqbyubneeflyy":
        pytest.skip("Refusing to run write-capable integration tests against a non-approved staging Supabase target. (Production detected)")
        
    if project_ref != APPROVED_STAGING_PROJECT_REF:
        pytest.skip(f"Refusing to run write-capable integration tests against a non-approved staging Supabase target. Found: {project_ref}, Expected: {APPROVED_STAGING_PROJECT_REF}")

