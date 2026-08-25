import os

import httpx
from django.shortcuts import render


API_BASE_URL = os.getenv("TECHGEAR_API_URL", "http://127.0.0.1:8000")


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

    return render(
        request,
        "catalogo.html",
        {
            "productos": productos,
            "error": error,
        },
    )
