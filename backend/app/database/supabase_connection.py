from supabase import create_client, Client
from app.config import get_settings

settings = get_settings()

class SupabaseConnection:
    def __init__(self):
        self.client: Client | None = None

    def connect(self) -> Client | None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            return None
        if self.client is None:
            self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        return self.client

supabase_db = SupabaseConnection()
