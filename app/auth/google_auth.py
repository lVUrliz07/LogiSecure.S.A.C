from typing import Optional
from google.oauth2 import id_token
from google.auth.transport import requests
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

google_oauth_config = {
    "client_id": GOOGLE_CLIENT_ID,
    "client_secret": GOOGLE_CLIENT_SECRET,
    "redirect_uri": GOOGLE_REDIRECT_URI,
}


def verify_google_token(token: str) -> Optional[dict]:
    """
    Verifica un token de Google OAuth.

    Args:
        token: Token de ID de Google a verificar

    Returns:
        Diccionario con la información del usuario o None si es inválido
    """
    try:
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), GOOGLE_CLIENT_ID
        )

        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            return None

        return idinfo

    except Exception:
        return None


def get_google_oauth_url() -> str:
    """
    Genera la URL de autorización de Google OAuth.

    Returns:
        URL de autorización de Google
    """
    from urllib.parse import urlencode

    base_url = "https://accounts.google.com/o/oauth2/v2/auth"

    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }

    return f"{base_url}?{urlencode(params)}"
