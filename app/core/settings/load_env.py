import os
import json
import sys
from typing import Any, Optional

# Detect whether running under type checking or static analysis tools
RUNNING_TYPE_CHECK = any(
    keyword in " ".join(sys.argv).lower()
    for keyword in ("mypy", "type-check", "pylint")
)


def get_env_var(name: str, default_if_typecheck: str = "") -> str:
    """
    Get an environment variable, with an optional default value during type-checking.
    Raises ValueError if missing when not type-checking.
    """
    value = os.getenv(name)
    if value:
        return value

    if RUNNING_TYPE_CHECK:
        return default_if_typecheck

    raise ValueError(f"Missing required environment variable: {name}")


def load_json_env_var(name: str) -> Optional[dict[str, Any]]:
    """
    Try to parse an environment variable as JSON.
    Returns None if variable is not set.
    Raises ValueError if invalid JSON (unless type-checking).
    """
    raw_value = os.getenv(name)
    if not raw_value:
        return None

    try:
        return json.loads(raw_value)
    except json.JSONDecodeError as exc:
        if not RUNNING_TYPE_CHECK:
            raise ValueError(f"{name} must contain valid JSON") from exc
        return None


# Required Supabase environment variables
SUPABASE_PROJECT_URL = get_env_var("SUPABASE_PROJECT_URL", "")
SUPABASE_PUBLIC_KEY = get_env_var("SUPABASE_PUBLIC_KEY", "")
SUPABASE_SECRET_KEY = get_env_var("SUPABASE_SECRET_KEY", "")

# Optional ES256 JWK (JSON Web Key)
SUPABASE_ES256_PUBLIC_JWK = load_json_env_var("SUPABASE_ES256_PUBLIC_JWK")
