from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.user_schemas import SensitiveDataResponse
from app.auth.dependencies import get_gerente_user, get_dispatcher_or_gerente_user
from app.models import TempCode, User

router = APIRouter(prefix="/gerente", tags=["Datos Sensibles"])


@router.get("/sensitive-data", response_model=SensitiveDataResponse)
async def get_sensitive_data(
    current_user: User = Depends(get_gerente_user), db: Session = Depends(get_db)
):
    """
    Obtiene información confidencial del sistema.
    Solo el gerente puede acceder.
    """
    return SensitiveDataResponse(
        costo_real=25000.50,
        margen_ganancia=35.5,
        clientes_vip=[
            "Amazon Logistics",
            "Walmart Distribution",
            "FedEx Strategic",
            "DHL Premium",
        ],
        combustible_extra_en_ruta=True,
        notas_confidenciales="Información clasificada. Margen de ganancia por ruta: 15-40%. Costos operativos: combustible, mantenimiento, salarios. Bonificación por combustible extra disponible mediante código temporal.",
    )


@router.get("/stats")
async def get_gerente_stats(
    current_user: User = Depends(get_dispatcher_or_gerente_user), db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas del sistema. Solo el gerente puede acceder.
    """
    from app.models import User, Ruta, RoleEnum

    total_choferes = db.query(User).filter(User.role == RoleEnum.CHOFER).count()
    total_dispatchers = db.query(User).filter(User.role == RoleEnum.DISPATCHER).count()
    total_rutas = db.query(Ruta).count()
    rutas_activas = db.query(Ruta).filter(Ruta.estado == "en_progreso").count()
    rutas_completadas = db.query(Ruta).filter(Ruta.estado == "completada").count()

    codigos_activos = db.query(TempCode).filter(TempCode.is_used == False).count()

    return {
        "total_choferes": total_choferes,
        "total_dispatchers": total_dispatchers,
        "total_rutas": total_rutas,
        "rutas_activas": rutas_activas,
        "rutas_completadas": rutas_completadas,
        "codigos_activos": codigos_activos,
    }


@router.get("/codes")
async def get_active_codes(
    current_user: User = Depends(get_gerente_user), db: Session = Depends(get_db)
):
    """
    Obtiene los códigos temporales activos. Solo el gerente puede acceder.
    """
    from datetime import datetime

    codigos = (
        db.query(TempCode)
        .filter(TempCode.is_used == False, TempCode.expires_at > datetime.utcnow())
        .all()
    )

    return {
        "codes": [
            {"code": c.code, "purpose": c.purpose, "expires_at": c.expires_at}
            for c in codigos
        ]
    }
