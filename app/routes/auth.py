from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
import bcrypt
import secrets
from datetime import datetime

from app.database import get_db
from app.models import User, RoleEnum, TempCode
from app.schemas.user_schemas import (
    UserCreate,
    UserLogin,
    TokenResponse,
    UserResponse,
    GoogleAuthRequest,
    CodeCreate,
    CodeResponse,
    CodeValidate,
    TOTPSetupResponse,
    TOTPVerifyRequest,
)
from app.auth.jwt_handler import create_access_token, JWT_EXPIRATION_HOURS
from app.auth.google_auth import verify_google_token
from app.auth.code_generator import (
    generate_six_digit_code,
    get_code_expiration_time,
    is_code_expired,
)
from app.auth.dependencies import get_current_active_user, get_gerente_user

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema.
    """
    existing_user = (
        db.query(User)
        .filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email o nombre de usuario ya está registrado",
        )

    password_bytes = user_data.password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode("utf-8")

    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=True,
        is_google_auth=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(
        data={"sub": str(new_user.id), "role": new_user.role.value}
    )

    expires_seconds = JWT_EXPIRATION_HOURS * 3600

    return TokenResponse(
        access_token=access_token,
        expires_in=expires_seconds,
        user=UserResponse.model_validate(new_user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Inicia sesión con email y contraseña.
    """
    user = db.query(User).filter(User.email == credentials.email).first()

    password_bytes = credentials.password.encode("utf-8")[:72]
    is_valid = False
    if user and user.hashed_password:
        is_valid = bcrypt.checkpw(
            password_bytes, user.hashed_password.encode("utf-8")
        )

    if not user or not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    if user.is_totp_enabled:
        if not credentials.totp_code:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Código 2FA requerido",
            )
        import pyotp

        totp = pyotp.TOTP(user.totp_secret)
        if not totp.verify(credentials.totp_code, valid_window=1):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Código 2FA inválido",
            )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Usuario desactivado"
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=JWT_EXPIRATION_HOURS * 3600,
        user=UserResponse.model_validate(user),
    )


@router.post("/token", response_model=TokenResponse)
async def login_swagger(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint nativo para que Swagger UI pueda inyectar el Bearer Token automáticamente.
    (El campo username de Swagger se usa como email).
    """
    user = db.query(User).filter(User.email == form_data.username).first()

    password_bytes = form_data.password.encode("utf-8")[:72]
    is_valid = False
    if user and user.hashed_password:
        is_valid = bcrypt.checkpw(
            password_bytes, user.hashed_password.encode("utf-8")
        )

    if not user or not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    # Si tu backend tiene TOTP, idealmente se maneja aquí. Por limitaciones de Swagger UI (No prompt for TOTP by default sin config extra), validamos básico o retornamos un scope requerido.
    # En este demo estricto, permitimos retornar token pero en UI de front forzamos 2fa endpoint independiente.
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Usuario desactivado"
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=JWT_EXPIRATION_HOURS * 3600,
        user=UserResponse.model_validate(user),
    )


@router.post("/google", response_model=TokenResponse)
async def google_login(google_data: GoogleAuthRequest, db: Session = Depends(get_db)):
    """
    Inicia sesión o registra con Google OAuth.
    """
    google_user_info = verify_google_token(google_data.token)

    if not google_user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de Google inválido"
        )

    email = google_user_info.get("email")
    full_name = google_user_info.get("name", "")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        username = email.split("@")[0]

        existing_username = db.query(User).filter(User.username == username).first()
        if existing_username:
            username = f"{username}_{int(datetime.now().timestamp())}"

        secure_password = secrets.token_urlsafe(32)
        
        new_user = User(
            email=email,
            username=username,
            hashed_password=bcrypt.hashpw(secure_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            full_name=full_name,
            role=RoleEnum.CHOFER,
            is_active=True,
            is_google_auth=True,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        user = new_user

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Usuario desactivado"
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=JWT_EXPIRATION_HOURS * 3600,
        user=UserResponse.model_validate(user),
    )


@router.post("/generate-code", response_model=CodeResponse)
async def generate_code(
    code_data: CodeCreate,
    current_user: User = Depends(get_gerente_user),
    db: Session = Depends(get_db),
):
    """
    Genera un código temporal de 6 dígitos.
    Solo el gerente puede generar códigos.
    """
    code = generate_six_digit_code()
    expires_at = get_code_expiration_time()

    temp_code = TempCode(
        code=code,
        purpose=code_data.purpose,
        created_by=current_user.id,
        expires_at=expires_at,
        is_used=False,
    )

    db.add(temp_code)
    db.commit()
    db.refresh(temp_code)

    return CodeResponse(code=temp_code.code, expires_at=temp_code.expires_at)


@router.post("/validate-code")
async def validate_code(
    code_data: CodeValidate, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Valida un código temporal de 6 dígitos. Protegido.
    """
    temp_code = db.query(TempCode).filter(TempCode.code == code_data.code).first()

    if not temp_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Código no encontrado"
        )

    if temp_code.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Código ya utilizado"
        )

    if is_code_expired(temp_code.expires_at):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Código expirado"
        )

    temp_code.is_used = True
    temp_code.used_at = datetime.utcnow()
    # Opcionalmente se podría agregar 'used_by=current_user.id' a la columna si existiera
    db.commit()

    return {"valid": True, "message": "Código válido verificado exitosamente"}


@router.post("/setup-2fa", response_model=TOTPSetupResponse)
async def setup_2fa(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Genera el secreto para Google Authenticator interactivo."""
    import pyotp

    if current_user.is_totp_enabled:
        current_user.is_totp_enabled = False
        current_user.totp_secret = None

    secret = pyotp.random_base32()
    current_user.totp_secret = secret
    db.commit()

    provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.email, issuer_name="LogiSecure"
    )

    return TOTPSetupResponse(provisioning_uri=provisioning_uri, secret=secret)


@router.post("/enable-2fa")
async def enable_2fa(
    req: TOTPVerifyRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Verifica y habilita el 2FA con el primer código."""
    import pyotp

    if not current_user.totp_secret:
        raise HTTPException(
            status_code=404, detail="Usuario no ha iniciado setup 2FA"
        )

    totp = pyotp.TOTP(current_user.totp_secret)
    if not totp.verify(req.code, valid_window=1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Código 2FA incorrecto"
        )

    current_user.is_totp_enabled = True
    db.commit()

    return {"message": "2FA habilitado correctamente"}


@router.post("/disable-2fa")
async def disable_2fa(
    req: TOTPVerifyRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Deshabilita el 2FA (requiere código actual para confirmar)."""
    import pyotp

    if not current_user.is_totp_enabled or not current_user.totp_secret:
        raise HTTPException(status_code=400, detail="2FA no está habilitado")

    totp = pyotp.TOTP(current_user.totp_secret)
    if not totp.verify(req.code, valid_window=1):
        raise HTTPException(status_code=400, detail="Código 2FA incorrecto")

    current_user.is_totp_enabled = False
    current_user.totp_secret = None
    db.commit()

    return {"message": "2FA deshabilitado correctamente"}


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene la información del usuario actual autenticado.
    """
    return UserResponse.model_validate(current_user)
