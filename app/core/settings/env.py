import os
import json
import sys

# Detect type-checking or static analysis
RUNNING_TYPE_CHECK = any(
    keyword in " ".join(sys.argv) for keyword in ("mypy", "type-check", "pylint")
)


def get_env_var(name: str, default_if_typecheck: str = "") -> str:
    """Helper to get environment variables with optional dummy defaults during type checking."""
    value = os.getenv(name, default_if_typecheck if RUNNING_TYPE_CHECK else "")
    if not value and not RUNNING_TYPE_CHECK:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


# Required Supabase variables
SUPABASE_PROJECT_URL = get_env_var(
    "SUPABASE_PROJECT_URL", "https://example.supabase.co"
)
SUPABASE_PUBLIC_KEY = get_env_var("SUPABASE_PUBLIC_KEY", "dummy_public_key")
SUPABASE_SECRET_KEY = get_env_var("SUPABASE_SECRET_KEY", "dummy_secret_key")

# Optional ES256 JWK parsing
SUPABASE_ES256_PUBLIC_JWK: dict | None = None
raw_jwk = os.getenv("SUPABASE_ES256_PUBLIC_JWK")

if raw_jwk:
    try:
        SUPABASE_ES256_PUBLIC_JWK = json.loads(raw_jwk)
    except json.JSONDecodeError as exc:
        if not RUNNING_TYPE_CHECK:
            raise ValueError("SUPABASE_ES256_PUBLIC_JWK must be valid JSON") from exc
