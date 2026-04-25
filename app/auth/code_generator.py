import random
import string
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

CODE_EXPIRATION_MINUTES = int(os.getenv("CODE_EXPIRATION_MINUTES", "120"))


def generate_six_digit_code() -> str:
    """
    Genera un código aleatorio de 6 dígitos.

    Returns:
        Código de 6 dígitos como string
    """
    return "".join(random.choices(string.digits, k=6))


def generate_code_with_prefix(prefix: str = "") -> str:
    """
    Genera un código de 6 dígitos con prefijo opcional.

    Args:
        prefix: Prefijo opcional para el código

    Returns:
        Código con prefijo
    """
    code = generate_six_digit_code()
    if prefix:
        return f"{prefix}{code}"
    return code


def is_code_expired(expires_at: datetime) -> bool:
    """
    Verifica si un código ha expirado.

    Args:
        expires_at: Fecha de expiración del código

    Returns:
        True si el código ha expirado, False en caso contrario
    """
    return datetime.utcnow() > expires_at


def get_code_expiration_time() -> datetime:
    """
    Obtiene la fecha de expiración para un nuevo código.

    Returns:
        Fecha de expiración como objeto datetime
    """
    return datetime.utcnow() + timedelta(minutes=CODE_EXPIRATION_MINUTES)


def validate_code_format(code: str) -> bool:
    """
    Valida que un código tenga el formato correcto (6 dígitos).

    Args:
        code: Código a validar

    Returns:
        True si el formato es válido, False en caso contrario
    """
    return len(code) == 6 and code.isdigit()
