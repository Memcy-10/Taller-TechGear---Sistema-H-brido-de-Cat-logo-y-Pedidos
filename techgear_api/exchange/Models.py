from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, List, Union

UserRole = Literal["administrador", "empleado", "usuario"]


class UserBase(BaseModel):
    id: Optional[str] = Field(None, description="ID del usuario")
    nombre: str = Field(..., min_length=2, description="Nombre completo")
    email: str = Field(..., min_length=5, description="Correo electrónico")
    rol: UserRole = Field("usuario", description="Rol del usuario")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Contraseña")


class UserUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2)
    email: Optional[str] = Field(None, min_length=5)
    rol: Optional[UserRole] = None
    password: Optional[str] = Field(None, min_length=6)


class UserResponse(BaseModel):
    data: Optional[list[UserBase]] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserBase

# Modelos base para productos y ordenes
class ProductBase(BaseModel):
    id: Optional[str] = Field(None, description="ID del producto (ObjectId de MongoDB)")
    nombre: str = Field(..., description="Nombre del producto")
    descripcion: Optional[str] = Field(None, description="Descripción del producto")
    precio: float = Field(..., description="Precio del producto", gt=0)
    stock: int = Field(..., description="Cantidad disponible en stock")
    categoria: Optional[str] = Field(None, description="Categoría del producto")
    imagen: Optional[str] = Field(None, description="URL de la imagen del producto")

    @field_validator("precio")
    @classmethod
    def precio_max_dos_decimales(cls, v: float) -> float:
        if round(v, 2) != v:
            raise ValueError("El precio no puede tener más de 2 decimales")
        return v
class OrderBase(BaseModel):
    id: Optional[str] = Field(None, description="ID de la orden (ObjectId de MongoDB)")
    id_usuario: Union[int, str] = Field(..., description="ID del usuario que realizó la orden")
    nombre_usuario: str = Field(..., description="Nombre del usuario que realizó la orden")
    productos: List[ProductBase] = Field(..., description="Lista de productos en la orden")
    total: float = Field(..., description="Total de la orden", gt=0)
    fecha_orden: Optional[str] = Field(None, description="Fecha en que se realizó la orden")
    estado: Optional[str] = Field(None, description="Estado de la orden (pendiente, completada, cancelada, etc.)")

    @field_validator("total")
    @classmethod
    def total_max_dos_decimales(cls, v: float) -> float:
        if round(v, 2) != v:
            raise ValueError("El total no puede tener más de 2 decimales")
        return v

# Modelo creacion de productos y ordenes
class ProductCreate(ProductBase):
    pass
class OrderCreate(OrderBase):
    pass

# Modelo de actualizacion de productos y ordenes
class ProductUpdate(BaseModel):
    nombre: Optional[str] = Field(None, description="Nombre del producto")
    descripcion: Optional[str] = Field(None, description="Descripción del producto")
    precio: Optional[float] = Field(None, description="Precio del producto", gt=0)
    stock: Optional[int] = Field(None, description="Cantidad disponible en stock")
    categoria: Optional[str] = Field(None, description="Categoría del producto")
    imagen: Optional[str] = Field(None, description="URL de la imagen del producto")

    @field_validator("precio")
    @classmethod
    def precio_max_dos_decimales(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and round(v, 2) != v:
            raise ValueError("El precio no puede tener más de 2 decimales")
        return v
class OrderUpdate(BaseModel):
    id_usuario: Optional[Union[int, str]] = Field(None, description="ID del usuario que realizó la orden")
    nombre_usuario: Optional[str] = Field(None, description="Nombre del usuario que realizó la orden")
    productos: Optional[List[ProductBase]] = Field(None, description="Lista de productos en la orden")
    total: Optional[float] = Field(None, description="Total de la orden", gt=0)
    fecha_orden: Optional[str] = Field(None, description="Fecha en que se realizó la orden")
    estado: Optional[str] = Field(None, description="Estado de la orden (pendiente, completada, cancelada, etc.)")

    @field_validator("total")
    @classmethod
    def total_max_dos_decimales(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and round(v, 2) != v:
            raise ValueError("El total no puede tener más de 2 decimales")
        return v

# Modelo de respuesta para productos y ordenes
class ProductResponse(BaseModel):
    data: Optional[list[ProductBase]] = None
class OrderResponse(BaseModel):
    data: Optional[list[OrderBase]] = None