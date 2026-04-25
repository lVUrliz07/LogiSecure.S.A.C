from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Float,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class RoleEnum(str, enum.Enum):
    """
    Enum para los roles de usuario en el sistema.
    """

    CHOFER = "CHOFER"
    DISPATCHER = "DISPATCHER"
    GERENTE = "GERENTE"


class User(Base):
    """
    Modelo de usuario del sistema.
    Representa a los empleados de la empresa de logística.
    """

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(RoleEnum), nullable=False, default=RoleEnum.CHOFER)
    is_active = Column(Boolean, default=True)
    is_google_auth = Column(Boolean, default=False)
    totp_secret = Column(String(32), nullable=True)
    is_totp_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    rutas = relationship("Ruta", back_populates="chofer", foreign_keys="Ruta.chofer_id")

    def __repr__(self):
        return f"<User {self.email} - {self.role.value}>"


class Ruta(Base):
    """
    Modelo de rutas de entrega.
    Representa las rutas asignadas a los choferes.
    """

    __tablename__ = "rutas"

    id = Column(Integer, primary_key=True, index=True)
    chofer_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    origen = Column(String(255), nullable=False)
    destino = Column(String(255), nullable=False)
    descripcion = Column(String(500))
    estado = Column(String(50), default="pendiente")
    distancia_km = Column(Float)
    hora_salida = Column(DateTime)
    hora_llegada = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chofer = relationship("User", back_populates="rutas", foreign_keys=[chofer_id])

    def __repr__(self):
        return f"<Ruta {self.id} - {self.origen} to {self.destino}>"


class TempCode(Base):
    """
    Modelo de códigos temporales de 6 dígitos.
    Generados por el gerente para autorizaciones especiales.
    """

    __tablename__ = "codigos_temporales"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(6), unique=True, index=True, nullable=False)
    purpose = Column(String(255))
    is_used = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<TempCode {self.code} - expires {self.expires_at}>"
