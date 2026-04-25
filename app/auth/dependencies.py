from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, RoleEnum
from app.auth.jwt_handler import decode_access_token

# Definiendo la URL del token en Swagger (/auth/token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Verifica el token JWT en las cabeceras de autorización de la solicitud y obtiene el usuario."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
        
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Asegura que el usuario autenticado está activo."""
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Usuario inactivo")
    return current_user

def get_gerente_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Asegura que el usuario activo sea GERENTE."""
    if current_user.role != RoleEnum.GERENTE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el gerente puede acceder a este recurso"
        )
    return current_user

def get_dispatcher_or_gerente_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Asegura que el usuario activo sea DISPATCHER o GERENTE."""
    if current_user.role not in [RoleEnum.DISPATCHER, RoleEnum.GERENTE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a este recurso"
        )
    return current_user
