from __future__ import annotations

from supabase import Client, create_client

from app.core.config import get_settings


import httpx
from supabase.client import ClientOptions

_shared_httpx_client = httpx.Client(timeout=15.0)

def get_supabase() -> Client:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_secret_key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SECRET_KEY must be set in backend/.env"
        )
    
    options = ClientOptions(postgrest_client_timeout=15, storage_client_timeout=15)
    options.httpx_client = _shared_httpx_client
    
    return create_client(settings.supabase_url, settings.supabase_secret_key, options=options)
