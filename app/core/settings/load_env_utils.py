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
