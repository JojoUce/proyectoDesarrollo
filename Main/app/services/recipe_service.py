import requests
import os
# Cargar las variables de entorno desde el archivo .env

class RecipeService:
    def __init__(self):
        # Cargar las variables de entorno directamente
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.url = os.getenv('GEMINI_API_URL')

    def fetch_recipes(self, ingredients):
        response = requests.post(self.url, 
                                 json={"ingredients": ingredients},
                                 headers={"Authorization": f"Bearer {self.api_key}"})
        return response.json()
