from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from bson import ObjectId
from bson.errors import InvalidId
import os

from exchange.Models import (
    ProductBase, ProductCreate, ProductUpdate, ProductResponse,
    OrderBase, OrderCreate, OrderUpdate, OrderResponse,
)

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")
MONGODB_url = os.getenv("MONGODB_URL")

client = AsyncIOMotorClient(MONGODB_url)
db = client.maicolmontoyac2007_db_user
products_collection = db["Productos"]
orders_collection = db["Ordenes"]

app = FastAPI(
    title="TechGear API",
    description="API de productos y órdenes",
    version="1.0.0",
)


def doc_to_model(doc: dict) -> dict:
    """Convierte el _id de Mongo (ObjectId) en id (str) para que encaje con los modelos Pydantic."""
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc


def parse_object_id(id_str: str) -> ObjectId:
    """Valida y convierte un string a ObjectId, o lanza 400 si es inválido."""
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=400, detail="ID inválido")


# ============================================================
# PRODUCTOS
# ============================================================

@app.get(
    "/productos",
    response_model=ProductResponse,
    tags=["Productos"],
    operation_id="listar_productos",
    summary="Listar todos los productos",
)
async def listar_productos():
    productos = await products_collection.find().to_list(length=None)
    return {"data": [doc_to_model(p) for p in productos]}


@app.get(
    "/productos/buscar",
    response_model=ProductResponse,
    tags=["Productos"],
    operation_id="buscar_productos_por_nombre",
    summary="Buscar productos por nombre",
)
async def buscar_productos_por_nombre(nombre: str):
    productos = await products_collection.find(
        {"nombre": {"$regex": nombre, "$options": "i"}}
    ).to_list(length=None)
    return {"data": [doc_to_model(p) for p in productos]}


@app.get(
    "/productos/{producto_id}",
    response_model=ProductBase,
    tags=["Productos"],
    operation_id="obtener_producto_por_id",
    summary="Obtener un producto por su ID",
)
async def obtener_producto_por_id(producto_id: str):
    oid = parse_object_id(producto_id)
    producto = await products_collection.find_one({"_id": oid})
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return doc_to_model(producto)


@app.post(
    "/productos",
    response_model=ProductBase,
    status_code=201,
    tags=["Productos"],
    operation_id="crear_producto",
    summary="Crear un nuevo producto",
)
async def crear_producto(producto: ProductCreate):
    doc = producto.model_dump(exclude={"id"})
    result = await products_collection.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc


@app.put(
    "/productos/{producto_id}",
    response_model=ProductBase,
    tags=["Productos"],
    operation_id="actualizar_producto",
    summary="Actualizar un producto existente",
)
async def actualizar_producto(producto_id: str, cambios: ProductUpdate):
    oid = parse_object_id(producto_id)
    datos = {k: v for k, v in cambios.model_dump().items() if v is not None}

    if not datos:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")

    resultado = await products_collection.update_one({"_id": oid}, {"$set": datos})
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    producto = await products_collection.find_one({"_id": oid})
    return doc_to_model(producto)


@app.delete(
    "/productos/{producto_id}",
    tags=["Productos"],
    operation_id="eliminar_producto",
    summary="Eliminar un producto",
)
async def eliminar_producto(producto_id: str):
    oid = parse_object_id(producto_id)
    resultado = await products_collection.delete_one({"_id": oid})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"mensaje": "Producto eliminado correctamente"}


# ============================================================
# ÓRDENES
# ============================================================

@app.get(
    "/ordenes",
    response_model=OrderResponse,
    tags=["Ordenes"],
    operation_id="listar_ordenes",
    summary="Listar todas las órdenes",
)
async def listar_ordenes():
    ordenes = await orders_collection.find().to_list(length=None)
    return {"data": [doc_to_model(o) for o in ordenes]}


@app.get(
    "/ordenes/usuario/{id_usuario}",
    response_model=OrderResponse,
    tags=["Ordenes"],
    operation_id="buscar_ordenes_por_id_usuario",
    summary="Buscar órdenes por ID de usuario",
)
async def buscar_ordenes_por_id_usuario(id_usuario: int):
    ordenes = await orders_collection.find({"id_usuario": id_usuario}).to_list(length=None)
    return {"data": [doc_to_model(o) for o in ordenes]}


@app.get(
    "/ordenes/nombre/{nombre_usuario}",
    response_model=OrderResponse,
    tags=["Ordenes"],
    operation_id="buscar_ordenes_por_nombre_usuario",
    summary="Buscar órdenes por nombre de usuario",
)
async def buscar_ordenes_por_nombre_usuario(nombre_usuario: str):
    ordenes = await orders_collection.find(
        {"nombre_usuario": {"$regex": nombre_usuario, "$options": "i"}}
    ).to_list(length=None)
    return {"data": [doc_to_model(o) for o in ordenes]}


@app.get(
    "/ordenes/{orden_id}",
    response_model=OrderBase,
    tags=["Ordenes"],
    operation_id="obtener_orden_por_id",
    summary="Obtener una orden por su ID",
)
async def obtener_orden_por_id(orden_id: str):
    oid = parse_object_id(orden_id)
    orden = await orders_collection.find_one({"_id": oid})
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return doc_to_model(orden)


@app.post(
    "/ordenes",
    response_model=OrderBase,
    status_code=201,
    tags=["Ordenes"],
    operation_id="crear_orden",
    summary="Crear una nueva orden",
)
async def crear_orden(orden: OrderCreate):
    doc = orden.model_dump(exclude={"id"})
    result = await orders_collection.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc


@app.put(
    "/ordenes/{orden_id}",
    response_model=OrderBase,
    tags=["Ordenes"],
    operation_id="actualizar_orden",
    summary="Actualizar una orden existente",
)
async def actualizar_orden(orden_id: str, cambios: OrderUpdate):
    oid = parse_object_id(orden_id)
    datos = {k: v for k, v in cambios.model_dump().items() if v is not None}

    if not datos:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")

    resultado = await orders_collection.update_one({"_id": oid}, {"$set": datos})
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    orden = await orders_collection.find_one({"_id": oid})
    return doc_to_model(orden)


@app.delete(
    "/ordenes/{orden_id}",
    tags=["Ordenes"],
    operation_id="eliminar_orden",
    summary="Eliminar una orden",
)
async def eliminar_orden(orden_id: str):
    oid = parse_object_id(orden_id)
    resultado = await orders_collection.delete_one({"_id": oid})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return {"mensaje": "Orden eliminada correctamente"}