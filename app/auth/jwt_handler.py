from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from dotenv import load_dotenv
import os

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "8"))

if not JWT_SECRET:
    raise ValueError("JWT_SECRET es requerida. Configúrala en el archivo .env")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT con los datos proporcionados.

    Args:
        data: Diccionario con los datos a incluir en el token
        expires_delta: Tiempo de expiración opcional

    Returns:
        Token JWT codificado como string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica un token JWT.

    Args:
        token: Token JWT a decodificar

    Returns:
        Diccionario con los datos del token o None si es inválido
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def get_token_expiration() -> datetime:
    """
    Obtiene la fecha de expiración para un nuevo token.

    Returns:
        Fecha de expiración como objeto datetime
    """
    return datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
