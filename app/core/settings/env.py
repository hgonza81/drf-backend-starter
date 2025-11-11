import os

SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_PUBLIC_KEY = os.getenv("SUPABASE_PUBLIC_KEY")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

if not SUPABASE_PROJECT_URL or not SUPABASE_PUBLIC_KEY or not SUPABASE_SECRET_KEY:
    raise ValueError("Missing required Supabase environment variables")
