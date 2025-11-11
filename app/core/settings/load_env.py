import json
import os


def get_env_var(name: str) -> str:
    """
    Get an environment variable.
    Raises ValueError if the variable is missing.
    """
    value = os.getenv(name)
    if value:
        return value
    raise ValueError(f"Missing required environment variable: {name}")


def load_json_env_var(name: str) -> dict | None:
    """
    Try to parse an environment variable as JSON.
    Returns None if variable is not set.
    Raises ValueError if invalid JSON.
    """
    raw_value = os.getenv(name)
    if not raw_value:
        return None

    try:
        return json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{name} must contain valid JSON") from exc


# Required Supabase environment variables
SUPABASE_ES256_PUBLIC_JWK = load_json_env_var("SUPABASE_ES256_PUBLIC_JWK")
SUPABASE_PROJECT_URL = get_env_var("SUPABASE_PROJECT_URL")
SUPABASE_PUBLIC_KEY = get_env_var("SUPABASE_PUBLIC_KEY")
SUPABASE_SECRET_KEY = get_env_var("SUPABASE_SECRET_KEY")
