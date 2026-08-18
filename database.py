import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
MONGODB_url = os.getenv("MONGODB_url")
client = AsyncIOMotorClient(MONGODB_url)
db = client.maicolmontoyac2007_db_user
collection = db["Servidor Maicol M"]

async def test_connection():
    try:
        await client.admin.command('ping')
        print("Conexión exitosa a la base de datos MongoDB")

        # Generar documentos de prueba
        doctest = [
            {"nombre": "Mesa de prueba", "valor": 10,"color": "rojo"},
            {"nombre": "Documento 2", "valor": 20,"color": "azul"},
            {"nombre": "Documento 3", "valor": 30,"color": "verde"}
        ]

        # Guardado de datos
        result = await collection.insert_many(doctest)
        print(f"Documentos insertados")

        # Busqueda de datos
        documents = await collection.find().to_list(length=100)
        print("Documentos encontrados:")
        for doc in documents:
            print(f"Nombre: {doc['nombre']}, Valor: {doc['valor']}, Color: {doc['color']}")

    except Exception as e:
        print(f"Error al conectar a la base de datos MongoDB: {e}")

if __name__ == "__main__":
    # ejecutar prueba coneccion
    asyncio.run(test_connection())