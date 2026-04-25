from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class RoleEnum(str, Enum):
    CHOFER = "CHOFER"
    DISPATCHER = "DISPATCHER"
    GERENTE = "GERENTE"


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=1, max_length=255)
    role: RoleEnum = RoleEnum.CHOFER


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    role: RoleEnum
    is_active: bool
    is_google_auth: bool
    is_totp_enabled: bool = False
    created_at: datetime


    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    totp_code: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class GoogleAuthRequest(BaseModel):
    token: str


class CodeCreate(BaseModel):
    purpose: Optional[str] = Field(None, max_length=255)


class CodeResponse(BaseModel):
    code: str
    expires_at: datetime

    class Config:
        from_attributes = True


class CodeValidate(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)


class TOTPSetupResponse(BaseModel):
    provisioning_uri: str
    secret: str


class TOTPVerifyRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)


class RutaCreate(BaseModel):
    chofer_id: int
    origen: str = Field(..., min_length=1, max_length=255)
    destino: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = Field(None, max_length=500)
    distancia_km: Optional[float] = Field(None, ge=0)
    hora_salida: Optional[datetime] = None


class RutaUpdate(BaseModel):
    origen: Optional[str] = Field(None, min_length=1, max_length=255)
    destino: Optional[str] = Field(None, min_length=1, max_length=255)
    descripcion: Optional[str] = Field(None, max_length=500)
    estado: Optional[str] = Field(None, max_length=50)
    distancia_km: Optional[float] = Field(None, ge=0)
    hora_salida: Optional[datetime] = None
    hora_llegada: Optional[datetime] = None


class RutaResponse(BaseModel):
    id: int
    chofer_id: int
    origen: str
    destino: str
    descripcion: Optional[str]
    estado: str
    distancia_km: Optional[float]
    hora_salida: Optional[datetime]
    hora_llegada: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class SensitiveDataResponse(BaseModel):
    costo_real: float
    margen_ganancia: float
    clientes_vip: list[str]
    combustible_extra_en_ruta: bool
    notas_confidenciales: str
