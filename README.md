# TechGear

TechGear es una demo de e-commerce en Python con dos componentes principales:

- una API REST en FastAPI para gestionar productos, usuarios y órdenes
- una aplicación web en Django para consumir la API y mostrar el catálogo, carrito, usuarios y flujo de órdenes

## Requisitos

- Python 3.13
- MongoDB accesible con la variable de entorno MONGODB_URL
- Paquetes listados en los archivos requirements.txt de cada proyecto

## Estructura del proyecto

- techgear_api/: API FastAPI con modelos y endpoints
- techgear_web/: aplicación Django con interfaz web
- venv313/: entorno virtual del proyecto

## Instalación

1. Activar el entorno virtual:
   ```bash
   .\venv313\Scripts\Activate.ps1
   ```
2. Instalar dependencias de la API:
   ```bash
   cd techgear_api
   pip install -r requirements.txt
   ```
3. Instalar dependencias de la web:
   ```bash
   cd ../techgear_web
   pip install -r requirements.txt
   ```
4. Configurar la conexión a MongoDB en un .env dentro de techgear_api con:
   ```env
   MONGODB_URL=mongodb://localhost:27017
   ```

## Ejecutar la API

```bash
cd techgear_api\app
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API queda disponible en:
- http://127.0.0.1:8000/docs

## Ejecutar la web

```bash
cd techgear_web
python manage.py runserver 8001
```

La aplicación queda en:
- http://127.0.0.1:8001/

## Funcionalidades

### Catálogo
- Visualización de productos desde la API
- Agregar productos al carrito
- Validación de stock al agregar cantidades

### Carrito
- Ver productos seleccionados
- Modificar cantidades
- Eliminar elementos
- Confirmar pedido para crear una orden

### CRUD de órdenes
- Listar todas las órdenes
- Crear nueva orden
- Editar orden existente
- Eliminar orden
- Manejo de errores cuando la API no responde
- Validación cuando un producto no tiene stock disponible

### Usuarios
- Login
- Registro y gestión de usuarios
- Vista de administración con rol de administrador

## Manejo de excepciones

La implementación contempla escenarios como:

- API caída o no disponible
- Timeout de conexión con la API
- respuestas vacías o inválidas del backend
- productos sin stock al intentar crear o actualizar una orden
- errores al intentar editar o eliminar órdenes inexistentes

En la capa web esto se refleja con mensajes en pantalla y validaciones del formulario.

## Flujo completo revisado

1. El usuario entra al catálogo.
2. Agrega productos al carrito.
3. El carrito valida stock y cantidades.
4. Cuando confirma la compra, crea la orden con la API.
5. El administrador puede ver todas las órdenes desde el panel de ordenes.
6. Desde esa vista puede editar o eliminar una orden.
7. Si la API falla, la web muestra un mensaje claro y no rompe la experiencia.

## Nota de la demo

Esta es una prueba funcional sin seguridad avanzada. Para la demostración, el CRUD de órdenes y la web se ejecutan sin exigir autenticación adicional.

## Links del aplicativo

## Frontend
vercel: https://taller-tech-gear-sistema-h-brido-de.vercel.app

## Backend
render: https://taller-techgear-sistema-h-brido-de-cat.onrender.com/