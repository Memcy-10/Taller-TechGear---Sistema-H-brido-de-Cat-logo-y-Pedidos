from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from bson import ObjectId
from bson.errors import InvalidId
from hashlib import pbkdf2_hmac
import secrets
import os

from exchange.Models import (
    ProductBase, ProductCreate, ProductUpdate, ProductResponse,
    OrderBase, OrderCreate, OrderUpdate, OrderResponse,
    UserBase, UserCreate, UserUpdate, UserResponse, LoginRequest, LoginResponse,
)

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")
MONGODB_url = os.getenv("MONGODB_URL")

client = AsyncIOMotorClient(MONGODB_url)
db = client.maicolmontoyac2007_db_user
products_collection = db["Productos"]
orders_collection = db["Ordenes"]
users_collection = db["Usuarios"]
security = HTTPBearer(auto_error=False)

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


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
    return f"{salt.hex()}${digest.hex()}"


def password_matches(password: str, stored_password: str) -> bool:
    try:
        salt_hex, digest_hex = stored_password.split("$", 1)
        expected = pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 120_000)
        return secrets.compare_digest(expected.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def public_user(user: dict) -> dict:
    user = dict(user)
    user.pop("password_hash", None)
    return doc_to_model(user)


async def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticación requerida")
    user = await users_collection.find_one({"token": credentials.credentials})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    return user


def require_roles(*roles: str):
    async def dependency(user: dict = Depends(current_user)):
        if user.get("rol") not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para esta acción")
        return user
    return dependency


# ============================================================
# USUARIOS Y AUTENTICACIÓN
# ============================================================

@app.post("/auth/registro", response_model=UserBase, status_code=201, tags=["Autenticación"])
async def registrar_usuario(usuario: UserCreate):
    email = usuario.email.lower().strip()
    if await users_collection.find_one({"email": email}):
        raise HTTPException(status_code=409, detail="El correo ya está registrado")
    doc = usuario.model_dump(exclude={"id", "password"})
    doc.update({"email": email, "password_hash": hash_password(usuario.password)})
    result = await users_collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    return public_user(doc)


@app.post("/auth/login", response_model=LoginResponse, tags=["Autenticación"])
async def iniciar_sesion(datos: LoginRequest):
    user = await users_collection.find_one({"email": datos.email.lower().strip()})
    if not user or not password_matches(datos.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    token = secrets.token_urlsafe(32)
    await users_collection.update_one({"_id": user["_id"]}, {"$set": {"token": token}})
    return {"access_token": token, "user": public_user(user)}


@app.post("/auth/logout", tags=["Autenticación"])
async def cerrar_sesion(user: dict = Depends(current_user)):
    await users_collection.update_one({"_id": user["_id"]}, {"$unset": {"token": ""}})
    return {"mensaje": "Sesión cerrada"}


@app.get("/usuarios", response_model=UserResponse, tags=["Usuarios"])
async def listar_usuarios(user: dict = Depends(require_roles("administrador"))):
    usuarios = await users_collection.find().to_list(length=None)
    return {"data": [public_user(usuario) for usuario in usuarios]}


@app.post("/usuarios", response_model=UserBase, status_code=201, tags=["Usuarios"])
async def crear_usuario(usuario: UserCreate, user: dict = Depends(require_roles("administrador"))):
    email = usuario.email.lower().strip()
    if await users_collection.find_one({"email": email}):
        raise HTTPException(status_code=409, detail="El correo ya está registrado")
    doc = usuario.model_dump(exclude={"id", "password"})
    doc.update({"email": email, "password_hash": hash_password(usuario.password)})
    result = await users_collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    return public_user(doc)


@app.put("/usuarios/{usuario_id}", response_model=UserBase, tags=["Usuarios"])
async def actualizar_usuario(usuario_id: str, cambios: UserUpdate, user: dict = Depends(require_roles("administrador"))):
    oid = parse_object_id(usuario_id)
    datos = {k: v for k, v in cambios.model_dump(exclude={"password"}).items() if v is not None}
    if cambios.password:
        datos["password_hash"] = hash_password(cambios.password)
    if cambios.email:
        datos["email"] = cambios.email.lower().strip()
    if not datos:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")
    result = await users_collection.update_one({"_id": oid}, {"$set": datos})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return public_user(await users_collection.find_one({"_id": oid}))


@app.delete("/usuarios/{usuario_id}", tags=["Usuarios"])
async def eliminar_usuario(usuario_id: str, user: dict = Depends(require_roles("administrador"))):
    result = await users_collection.delete_one({"_id": parse_object_id(usuario_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"mensaje": "Usuario eliminado"}


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
async def crear_producto(producto: ProductCreate, user: dict = Depends(require_roles("administrador", "empleado"))):
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
async def actualizar_producto(producto_id: str, cambios: ProductUpdate, user: dict = Depends(require_roles("administrador"))):
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
async def eliminar_producto(producto_id: str, user: dict = Depends(require_roles("administrador"))):
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
    for producto in orden.productos:
        if producto.stock is None or producto.stock <= 0:
            raise HTTPException(status_code=400, detail=f"El producto '{producto.nombre}' no tiene stock disponible.")
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

    if cambios.productos is not None:
        for producto in cambios.productos:
            if producto.stock is None or producto.stock <= 0:
                raise HTTPException(status_code=400, detail=f"El producto '{producto.nombre}' no tiene stock disponible.")

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