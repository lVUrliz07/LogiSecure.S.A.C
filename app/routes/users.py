from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import bcrypt

from app.database import get_db
from app.models import User, RoleEnum
from app.schemas.user_schemas import UserCreate, UserUpdate, UserResponse
from app.auth.dependencies import get_gerente_user, get_dispatcher_or_gerente_user

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    current_user: User = Depends(get_dispatcher_or_gerente_user),
    db: Session = Depends(get_db),
):
    """
    Obtiene todos los usuarios. El gerente y el despachador pueden acceder para gestionar la flota.
    """
    users = db.query(User).all()
    return [UserResponse.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_gerente_user),
    db: Session = Depends(get_db),
):
    """
    Obtiene un usuario por su ID.
    """

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    return UserResponse.model_validate(user)


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_gerente_user),
    db: Session = Depends(get_db),
):
    """
    Crea un nuevo usuario. Solo el gerente puede crear usuarios.
    """

    existing_user = (
        db.query(User)
        .filter((User.email == user_data.email) | (User.username == user_data.username))
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

    return UserResponse.model_validate(new_user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_gerente_user),
    db: Session = Depends(get_db),
):
    """
    Actualiza un usuario. Solo el gerente puede actualizar usuarios.
    """

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    if user_data.email is not None:
        existing = (
            db.query(User)
            .filter(User.email == user_data.email, User.id != user_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está en uso",
            )
        user.email = user_data.email

    if user_data.username is not None:
        existing = (
            db.query(User)
            .filter(User.username == user_data.username, User.id != user_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso",
            )
        user.username = user_data.username

    if user_data.full_name is not None:
        user.full_name = user_data.full_name

    if user_data.role is not None:
        user.role = user_data.role

    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    if user_data.password is not None:
        password_bytes = user_data.password.encode("utf-8")[:72]
        salt = bcrypt.gensalt()
        user.hashed_password = bcrypt.hashpw(password_bytes, salt).decode("utf-8")

    db.commit()
    db.refresh(user)

    return UserResponse.model_validate(user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_gerente_user),
    db: Session = Depends(get_db),
):
    """
    Elimina (desactiva) un usuario. Solo el gerente puede eliminar usuarios.
    """

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    user.is_active = False
    db.commit()

    return {"message": "Usuario desactivado exitosamente"}


@router.get("/drivers/list", response_model=List[UserResponse])
async def get_all_drivers(
    current_user: User = Depends(get_dispatcher_or_gerente_user), db: Session = Depends(get_db)
):
    """
    Obtiene todos los choferes. Accesible para dispatcher y gerente.
    """

    drivers = db.query(User).filter(User.role == RoleEnum.CHOFER).all()
    return [UserResponse.model_validate(driver) for driver in drivers]
