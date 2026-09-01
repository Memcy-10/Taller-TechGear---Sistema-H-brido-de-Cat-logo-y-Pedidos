"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from .views import (actualizar_carrito, agregar_al_carrito, carrito, catalogo, crear_orden,
                    editar_orden, eliminar_orden, ordenes, pagar_carrito,
                    quitar_del_carrito)

urlpatterns = [
    path('', catalogo, name='catalogo'),
    path('carrito/', carrito, name='carrito'),
    path('carrito/agregar/<str:producto_id>/', agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/actualizar/<str:producto_id>/', actualizar_carrito, name='actualizar_carrito'),
    path('carrito/quitar/<str:producto_id>/', quitar_del_carrito, name='quitar_del_carrito'),
    path('carrito/pagar/', pagar_carrito, name='pagar_carrito'),
    path('ordenes/', ordenes, name='ordenes'),
    path('ordenes/nueva/', crear_orden, name='crear_orden'),
    path('ordenes/<str:orden_id>/editar/', editar_orden, name='editar_orden'),
    path('ordenes/<str:orden_id>/eliminar/', eliminar_orden, name='eliminar_orden'),
    path('admin/', admin.site.urls),
]
