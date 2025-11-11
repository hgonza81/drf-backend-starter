import os
import json

SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_PUBLIC_KEY = os.getenv("SUPABASE_PUBLIC_KEY")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")
SUPABASE_ES256_PUBLIC_JWK = os.getenv("SUPABASE_ES256_PUBLIC_JWK")

if (
    not SUPABASE_PROJECT_URL
    or not SUPABASE_PUBLIC_KEY
    or not SUPABASE_SECRET_KEY
    or not SUPABASE_ES256_PUBLIC_JWK
):
    raise ValueError("Missing required Supabase environment variables")

# Parse the JWK if provided
if SUPABASE_ES256_PUBLIC_JWK:
    try:
        SUPABASE_ES256_PUBLIC_JWK = json.loads(SUPABASE_ES256_PUBLIC_JWK)
    except json.JSONDecodeError:
        raise ValueError("SUPABASE_ES256_PUBLIC_JWK must be valid JSON")
