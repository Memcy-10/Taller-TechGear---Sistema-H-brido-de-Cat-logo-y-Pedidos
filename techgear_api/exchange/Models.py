from pydantic import BaseModel, Field
from typing import Optional, List

# Modelos base para productos y ordenes
class ProductBase(BaseModel):
    id: Optional[str] = Field(None, description="ID del producto (ObjectId de MongoDB)")
    nombre: str = Field(..., description="Nombre del producto")
    descripcion: Optional[str] = Field(None, description="Descripción del producto")
    precio: float = Field(..., description="Precio del producto", pattern=r'^\d+(\.\d{1,2})?$')
    stock: int = Field(..., description="Cantidad disponible en stock")
    categoria: Optional[str] = Field(None, description="Categoría del producto")
class OrderBase(BaseModel):
    id: Optional[str] = Field(None, description="ID de la orden (ObjectId de MongoDB)")
    id_usuario: int = Field(..., description="ID del usuario que realizó la orden")
    nombre_usuario: str = Field(..., description="Nombre del usuario que realizó la orden")
    productos: List[ProductBase] = Field(..., description="Lista de productos en la orden")
    total: float = Field(..., description="Total de la orden", pattern=r'^\d+(\.\d{1,2})?$')
    fecha_orden: Optional[str] = Field(None, description="Fecha en que se realizó la orden")
    estado: Optional[str] = Field(None, description="Estado de la orden (pendiente, completada, cancelada, etc.)")

# Modelo creacion de productos y ordenes
class ProductCreate(ProductBase):
    pass
class OrderCreate(OrderBase):
    pass

# Modelo de actualizacion de productos y ordenes
class ProductUpdate(BaseModel):
    nombre: Optional[str] = Field(None, description="Nombre del producto")
    descripcion: Optional[str] = Field(None, description="Descripción del producto")
    precio: Optional[float] = Field(None, description="Precio del producto", pattern=r'^\d+(\.\d{1,2})?$')
    stock: Optional[int] = Field(None, description="Cantidad disponible en stock")
    categoria: Optional[str] = Field(None, description="Categoría del producto")
class OrderUpdate(BaseModel):
    id_usuario: Optional[int] = Field(None, description="ID del usuario que realizó la orden")
    nombre_usuario: Optional[str] = Field(None, description="Nombre del usuario que realizó la orden")
    productos: Optional[List[ProductBase]] = Field(None, description="Lista de productos en la orden")
    total: Optional[float] = Field(None, description="Total de la orden", pattern=r'^\d+(\.\d{1,2})?$')
    fecha_orden: Optional[str] = Field(None, description="Fecha en que se realizó la orden")
    estado: Optional[str] = Field(None, description="Estado de la orden (pendiente, completada, cancelada, etc.)")

# Modelo de respuesta para productos y ordenes
class ProductResponse(BaseModel):
    data: Optional[list[ProductBase]] = None
class OrderResponse(BaseModel):
    data: Optional[list[OrderBase]] = None