import os
import json
import base64
from decimal import Decimal

import httpx
from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import LoginForm, OrderForm, ProductForm, RegisterForm, UserForm


API_BASE_URL = os.getenv("TECHGEAR_API_URL", "http://127.0.0.1:8000")


def api_request(method, path, request, **kwargs):
    headers = kwargs.pop("headers", {})
    if request.session.get("access_token"):
        headers["Authorization"] = f"Bearer {request.session['access_token']}"
    return httpx.request(method, f"{API_BASE_URL.rstrip('/')}{path}", headers=headers, timeout=5.0, **kwargs)


def catalogo(request):
    """Obtiene los productos de la API y los entrega al catalogo."""
    productos = []
    error = None

    try:
        response = httpx.get(
            f"{API_BASE_URL.rstrip('/')}/productos",
            timeout=5.0,
        )
        response.raise_for_status()
        productos = response.json().get("data") or []
    except (httpx.HTTPError, ValueError, AttributeError):
        error = "No fue posible cargar el catalogo en este momento."
    cart_items, cart_total = obtener_items_carrito(request)

    return render(
        request,
        "catalogo.html",
        {
            "productos": productos,
            "error": error,
            "user": request.session.get("user"),
            "cart_count": sum(item["cantidad"] for item in request.session.get("carrito", [])),
            "cart_items": cart_items,
            "cart_total": cart_total,
        },
    )


def agregar_al_carrito(request, producto_id):
    if request.method != "POST":
        return redirect("catalogo")

    try:
        response = httpx.get(f"{API_BASE_URL.rstrip('/')}/productos/{producto_id}", timeout=5.0)
        response.raise_for_status()
        producto = response.json()
    except (httpx.HTTPError, ValueError):
        messages.error(request, "No fue posible agregar el producto al carrito.")
        return redirect("catalogo")

    carrito = request.session.get("carrito", [])
    item = next((item for item in carrito if item["id"] == producto["id"]), None)
    if item:
        if item["cantidad"] < producto["stock"]:
            item["cantidad"] += 1
        else:
            messages.warning(request, "No puedes agregar más unidades que las disponibles.")
    elif producto.get("stock", 0) > 0:
        carrito.append({"id": producto["id"], "cantidad": 1})
    else:
        messages.warning(request, "Este producto está agotado.")
    request.session["carrito"] = carrito
    request.session.modified = True
    return redirect("catalogo")


def actualizar_carrito(request, producto_id):
    if request.method != "POST":
        return redirect("carrito")
    try:
        cantidad = max(0, int(request.POST.get("cantidad", 0)))
    except (TypeError, ValueError):
        cantidad = 0
    carrito = request.session.get("carrito", [])
    if cantidad == 0:
        carrito = [item for item in carrito if item["id"] != producto_id]
    else:
        for item in carrito:
            if item["id"] == producto_id:
                item["cantidad"] = cantidad
                break
    request.session["carrito"] = carrito
    request.session.modified = True
    return redirect("catalogo" if request.POST.get("next") == "catalogo" else "carrito")


def quitar_del_carrito(request, producto_id):
    if request.method == "POST":
        request.session["carrito"] = [
            item for item in request.session.get("carrito", [])
            if item["id"] != producto_id
        ]
        request.session.modified = True
    return redirect("catalogo" if request.POST.get("next") == "catalogo" else "carrito")


def obtener_items_carrito(request):
    items = []
    total = Decimal("0")
    for item in request.session.get("carrito", []):
        try:
            response = httpx.get(f"{API_BASE_URL.rstrip('/')}/productos/{item['id']}", timeout=5.0)
            response.raise_for_status()
            producto = response.json()
        except (httpx.HTTPError, ValueError):
            continue
        cantidad = min(item["cantidad"], producto.get("stock", 0))
        if cantidad <= 0:
            continue
        producto["cantidad"] = cantidad
        producto["subtotal"] = Decimal(str(producto["precio"])) * cantidad
        total += producto["subtotal"]
        items.append(producto)
    return items, total


def carrito(request):
    items, total = obtener_items_carrito(request)
    return render(request, "carrito.html", {
        "items": items,
        "total": total,
        "user": request.session.get("user"),
        "cart_count": sum(item["cantidad"] for item in request.session.get("carrito", [])),
    })


def pagar_carrito(request):
    user = request.session.get("user")
    if not user:
        messages.info(request, "Inicia sesión para pagar tu carrito.")
        return redirect("login")
    if request.method != "POST":
        return redirect("carrito")

    items, total = obtener_items_carrito(request)
    if not items:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect("carrito")

    productos = [{
        key: producto[key]
        for key in ("id", "nombre", "descripcion", "precio", "stock", "categoria")
        if key in producto
    } for producto in items]
    payload = {
        "id_usuario": user["id"],
        "nombre_usuario": user["nombre"],
        "productos": productos,
        "total": float(total),
        "estado": "pendiente",
    }
    try:
        api_response = api_request("POST", "/ordenes", request, json=payload)
    except httpx.HTTPError:
        messages.error(request, "No fue posible procesar el pago.")
        return redirect("carrito")
    if not api_response.is_success:
        messages.error(request, api_response.json().get("detail", "No fue posible procesar el pago."))
        return redirect("carrito")
    request.session["carrito"] = []
    messages.success(request, "Orden creada correctamente.")
    return redirect("catalogo")


def login(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        response = httpx.post(f"{API_BASE_URL.rstrip('/')}/auth/login", json=form.cleaned_data, timeout=5.0)
        if response.is_success:
            data = response.json()
            request.session["access_token"] = data["access_token"]
            request.session["user"] = data["user"]
            return redirect("catalogo")
        form.add_error(None, response.json().get("detail", "No fue posible iniciar sesión."))
    return render(request, "form.html", {"form": form, "title": "Iniciar sesión", "submit": "Entrar", "auth_page": "login"})


def registro(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        response = httpx.post(f"{API_BASE_URL.rstrip('/')}/auth/registro", json=form.cleaned_data, timeout=5.0)
        if response.is_success:
            messages.success(request, "Cuenta creada. Ya puedes iniciar sesión.")
            return redirect("login")
        form.add_error(None, response.json().get("detail", "No fue posible crear la cuenta."))
    return render(request, "form.html", {"form": form, "title": "Crear cuenta", "submit": "Registrarme", "auth_page": "registro"})


def logout(request):
    if request.session.get("access_token"):
        try:
            api_request("POST", "/auth/logout", request)
        except httpx.HTTPError:
            pass
    request.session.flush()
    return redirect("catalogo")


def crear_producto(request):
    if request.session.get("user", {}).get("rol") not in {"administrador", "empleado"}:
        return redirect("login")
    form = ProductForm(request.POST or None)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
    if request.method == "POST" and form.is_valid():
        payload = {**form.cleaned_data, "precio": float(form.cleaned_data["precio"])}
        image = form.cleaned_data.get("imagen")
        if image:
            encoded_image = base64.b64encode(image.read()).decode("ascii")
            payload["imagen"] = f"data:{image.content_type};base64,{encoded_image}"
        else:
            payload["imagen"] = None
        response = api_request("POST", "/productos", request, json=payload)
        if response.is_success:
            return redirect("catalogo")
        form.add_error(None, response.json().get("detail", "No fue posible guardar el producto."))
    return render(request, "form.html", {"form": form, "title": "Nuevo producto", "submit": "Guardar producto"})


def crear_orden(request):
    user = request.session.get("user")
    if not user:
        return redirect("login")
    form = OrderForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            productos = json.loads(form.cleaned_data["productos"])
        except json.JSONDecodeError:
            form.add_error("productos", "Escribe una lista JSON válida.")
        else:
            payload = {"id_usuario": user["id"], "nombre_usuario": user["nombre"], "productos": productos, "total": float(form.cleaned_data["total"]), "estado": "pendiente"}
            response = api_request("POST", "/ordenes", request, json=payload)
            if response.is_success:
                return redirect("catalogo")
            form.add_error(None, response.json().get("detail", "No fue posible crear la orden."))
    return render(request, "form.html", {"form": form, "title": "Nueva orden", "submit": "Crear orden"})


def usuarios(request):
    if request.session.get("user", {}).get("rol") != "administrador":
        return redirect("login")
    response = api_request("GET", "/usuarios", request)
    usuarios_data = response.json().get("data", []) if response.is_success else []
    return render(request, "usuarios.html", {"usuarios": usuarios_data})


def crear_usuario(request):
    if request.session.get("user", {}).get("rol") != "administrador":
        return redirect("login")
    form = UserForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        response = api_request("POST", "/usuarios", request, json=form.cleaned_data)
        if response.is_success:
            return redirect("usuarios")
        form.add_error(None, response.json().get("detail", "No fue posible crear el usuario."))
    return render(request, "form.html", {"form": form, "title": "Nuevo usuario", "submit": "Crear usuario"})
