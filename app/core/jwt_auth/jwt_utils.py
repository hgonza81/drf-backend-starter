import json
import logging

import jwt
from django.conf import settings
from rest_framework import exceptions

logger = logging.getLogger(__name__)


def decode_supabase_jwt(token: str) -> dict:
    """
    Decode a Supabase JWT token using the appropriate algorithm.
    Supports HS256, ES256, and RS256.
    Returns the payload if valid, raises AuthenticationFailed otherwise.
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
        algorithm = unverified_header.get("alg")
        logger.debug("JWT algorithm detected: %s", algorithm)

        if algorithm == "HS256":
            return _decode_hs256(token)
        elif algorithm == "ES256":
            return _decode_es256(token)
        elif algorithm == "RS256":
            return _decode_rs256(token)
        else:
            raise exceptions.AuthenticationFailed(f"Unsupported algorithm: {algorithm}")

    except jwt.ExpiredSignatureError as exc:
        raise exceptions.AuthenticationFailed("Token has expired.") from exc
    except jwt.InvalidAudienceError as exc:
        raise exceptions.AuthenticationFailed("Invalid token audience.") from exc
    except jwt.InvalidTokenError as exc:
        raise exceptions.AuthenticationFailed("Invalid token.") from exc
    except Exception as exc:
        logger.exception("Unexpected error decoding Supabase JWT.")
        raise exceptions.AuthenticationFailed("Authentication failed.") from exc


def _decode_hs256(token: str) -> dict:
    logger.debug("Decoding HS256 token...")
    return jwt.decode(
        token,
        settings.SUPABASE["SECRET_KEY"],
        algorithms=["HS256"],
        audience="authenticated",
    )


def _decode_es256(token: str) -> dict:
    logger.debug("Decoding ES256 token...")
    jwk = settings.SUPABASE.get("ES256_PUBLIC_JWK")
    if not jwk:
        raise exceptions.AuthenticationFailed("ES256 public key not configured.")

    from jwt.algorithms import ECAlgorithm

    try:
        public_key = ECAlgorithm.from_jwk(json.dumps(jwk))
    except Exception as exc:
        raise exceptions.AuthenticationFailed("Invalid ES256 public key.") from exc

    return jwt.decode(
        token,
        public_key,
        algorithms=["ES256"],
        audience="authenticated",
    )


def _decode_rs256(token: str) -> dict:
    logger.debug("Decoding RS256 token via JWKS endpoint...")
    from jwt import PyJWKClient

    jwks_url = f"{settings.SUPABASE['PROJECT_URL']}/auth/v1/.well-known/jwks.json"
    jwks_client = PyJWKClient(jwks_url)
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience="authenticated",
    )
