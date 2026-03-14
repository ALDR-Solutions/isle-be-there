from supabase import create_client, Client
from pydantic_settings import BaseSettings
from typing import Optional, Callable, Any
import time
import logging

logger = logging.getLogger(__name__)


class SupabaseSettings(BaseSettings):
    SUPABASE_URL: str = "https://udcbejeurwthcqxbctvw.supabase.co"
    SUPABASE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVkY2JlamV1cnd0aGNxeGJjdHZ3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzYxMzQ3NywiZXhwIjoyMDc5MTg5NDc3fQ.tPoVfIT26qrcfxv7mAZcTUK2yKJz2HNonePrphWtULU"    
    model_config = {"env_file": ".env", "extra": "ignore"}


class APIResponse:
    """Wrapper for Supabase v2 responses to maintain compatibility with v1 API."""
    def __init__(self, data, count=None):
        self.data = data
        self.count = count
        self.error = None


def execute_with_retry(operation, operation_name: str = "operation", max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Execute a Supabase operation with retry logic.
    Wraps for Supabase v2 compatibility.
    """
    current_delay = delay
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            result = operation()
            # Supabase v2 returns data directly, wrap it for compatibility
            if hasattr(result, 'data'):
                return APIResponse(data=result.data, count=result.count if hasattr(result, 'count') else None)
            else:
                return APIResponse(data=result)
        except Exception as e:
            last_exception = e
            
            if attempt < max_retries:
                logger.warning(f"Supabase {operation_name} failed (attempt {attempt + 1}/{max_retries + 1}): {str(e)}")
                time.sleep(current_delay)
                current_delay *= backoff
            else:
                logger.error(f"Supabase {operation_name} failed after {max_retries + 1} attempts: {str(e)}")
                raise last_exception if last_exception else Exception("Unknown error")

    raise last_exception if last_exception else Exception("Unknown error")


settings = SupabaseSettings()
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)