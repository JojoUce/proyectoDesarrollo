
# pip install python-dotenv google-generativeai
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Cargar las variables desde el archivo .env
load_dotenv("API_KEY.env")

# Obtener la API Key desde las variables de entorno
api_key = os.getenv("API_KEY")

# Verificar si la API_KEY se cargó correctamente
if not api_key:
    raise ValueError("La API_KEY no se encontró en el archivo .env")

# Configurar la API Key
genai.configure(api_key=api_key)

# Modelo generativo
model_name = "gemini-2.0-flash-exp"

# Función para obtener recetas basadas en productos
def receta(productos):
    try:
        # Llamada al modelo con los productos como entrada
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            f"Teniendo en cuenta la siguiente lista de elementos: {productos}, recomienda recetas de cocina que puedan hacerse con los productos, no hace falta usar todos. Las recetas no deben requerir elementos adicionales a los de la lista, junto al nombre de cada receta coloca el tiempo estimado que tardaría en cocinarse. No uses productos que no estén en la lista a menos que sean productos muy fáciles de conseguir."
        )
        return response.text
    except Exception as e:
        return f"Error al generar la receta: {str(e)}"

# Lista de productos en el refrigerador
productos = [
    "Leche", "Yogur", "Queso cheddar", "Pechuga de pollo", "Tomates",
    "Zanahorias", "Espinacas", "Jugo de naranja", "Mantequilla", "Huevos",
    "Papas", "Aguacates", "Salsa de soya", "Pimientos rojos", "Cebollas",
    "Pasta", "Crema de leche", "Frambuesas", "Manzanas", "Pepinos",
    "Pan de molde", "Tocino", "Salsa barbacoa", "Lechuga", "Jamón",
    "Guisantes congelados", "Pechuga de pavo", "Aceite de oliva", "Mostaza",
    "Limones", "Cilantro fresco", "Ajo"
]

# Generar las recetas
resultado = receta(productos)

# Mostrar el resultado
print(f"\nRecetas sugeridas:\n{resultado}")
