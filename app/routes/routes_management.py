from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, Ruta, RoleEnum
from app.schemas.user_schemas import RutaCreate, RutaUpdate, RutaResponse
from app.auth.dependencies import get_current_user, get_dispatcher_or_gerente_user

router = APIRouter(prefix="/routes", tags=["Gestión de Rutas"])


@router.get("/", response_model=List[RutaResponse])
async def get_all_routes(
    current_user: User = Depends(get_dispatcher_or_gerente_user), db: Session = Depends(get_db)
):
    """
    Obtiene todas las rutas. Accesible para dispatcher y gerente.
    """
    rutas = db.query(Ruta).all()
    return [RutaResponse.model_validate(ruta) for ruta in rutas]


@router.get("/my-routes", response_model=List[RutaResponse])
async def get_my_routes(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Obtiene las rutas del chofer actual.
    """
    if current_user.role == RoleEnum.CHOFER:
        rutas = db.query(Ruta).filter(Ruta.chofer_id == current_user.id).all()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este endpoint es solo para choferes",
        )

    return [RutaResponse.model_validate(ruta) for ruta in rutas]


@router.get("/{ruta_id}", response_model=RutaResponse)
async def get_route(
    ruta_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtiene una ruta por su ID.
    """
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()

    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ruta no encontrada"
        )

    if current_user.role == RoleEnum.CHOFER and ruta.chofer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver esta ruta",
        )

    return RutaResponse.model_validate(ruta)


@router.post("/", response_model=RutaResponse)
async def create_route(
    ruta_data: RutaCreate,
    current_user: User = Depends(get_dispatcher_or_gerente_user),
    db: Session = Depends(get_db),
):
    """
    Crea una nueva ruta. Accesible para dispatcher y gerente.
    """
    chofer = (
        db.query(User)
        .filter(User.id == ruta_data.chofer_id, User.role == RoleEnum.CHOFER)
        .first()
    )

    if not chofer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chofer no encontrado"
        )

    new_ruta = Ruta(
        chofer_id=ruta_data.chofer_id,
        origen=ruta_data.origen,
        destino=ruta_data.destino,
        descripcion=ruta_data.descripcion,
        distancia_km=ruta_data.distancia_km,
        hora_salida=ruta_data.hora_salida,
        estado="pendiente",
    )

    db.add(new_ruta)
    db.commit()
    db.refresh(new_ruta)

    return RutaResponse.model_validate(new_ruta)


@router.put("/{ruta_id}", response_model=RutaResponse)
async def update_route(
    ruta_id: int,
    ruta_data: RutaUpdate,
    current_user: User = Depends(get_dispatcher_or_gerente_user),
    db: Session = Depends(get_db),
):
    """
    Actualiza una ruta. Accesible para dispatcher y gerente.
    """
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()

    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ruta no encontrada"
        )

    if ruta_data.origen is not None:
        ruta.origen = ruta_data.origen

    if ruta_data.destino is not None:
        ruta.destino = ruta_data.destino

    if ruta_data.descripcion is not None:
        ruta.descripcion = ruta_data.descripcion

    if ruta_data.estado is not None:
        ruta.estado = ruta_data.estado

    if ruta_data.distancia_km is not None:
        ruta.distancia_km = ruta_data.distancia_km

    if ruta_data.hora_salida is not None:
        ruta.hora_salida = ruta_data.hora_salida

    if ruta_data.hora_llegada is not None:
        ruta.hora_llegada = ruta_data.hora_llegada

    db.commit()
    db.refresh(ruta)

    return RutaResponse.model_validate(ruta)


@router.delete("/{ruta_id}")
async def delete_route(
    ruta_id: int,
    current_user: User = Depends(get_dispatcher_or_gerente_user),
    db: Session = Depends(get_db),
):
    """
    Elimina una ruta. Accesible para dispatcher y gerente.
    """
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()

    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ruta no encontrada"
        )

    db.delete(ruta)
    db.commit()

    return {"message": "Ruta eliminada exitosamente"}


@router.put("/{ruta_id}/status", response_model=RutaResponse)
async def update_route_status(
    ruta_id: int,
    estado: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Actualiza el estado de una ruta. El chofer puede actualizar su propia ruta.
    """
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()

    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ruta no encontrada"
        )

    if current_user.role == RoleEnum.CHOFER and ruta.chofer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar esta ruta",
        )

    if current_user.role == RoleEnum.CHOFER and estado not in [
        "en_progreso",
        "completada",
        "cancelada",
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado no válido para chofer",
        )

    ruta.estado = estado

    if estado == "completada":
        from datetime import datetime

        ruta.hora_llegada = datetime.utcnow()

    db.commit()
    db.refresh(ruta)

    return RutaResponse.model_validate(ruta)
