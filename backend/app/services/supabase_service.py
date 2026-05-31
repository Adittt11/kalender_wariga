from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_KEY

def get_supabase():
    if not SUPABASE_URL:
        raise ValueError("SUPABASE_URL belum diisi di file .env")

    if not SUPABASE_KEY:
        raise ValueError("SUPABASE_KEY belum diisi di file .env")

    return create_client(SUPABASE_URL, SUPABASE_KEY)
