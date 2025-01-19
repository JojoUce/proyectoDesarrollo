import requests
import os


class recipeService:
    def __init__(self):
        # Cargar las variables de entorno directamente
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.url = os.getenv('GEMINI_API_URL')

    def fetch_recipes(self, ingredients):
        try:
            response = requests.post(self.url, 
                                 json={"ingredients": ingredients},
                                 headers={"Authorization": f"Bearer {self.api_key}"})
            response.raise_forstatus()
            return response.json()
        except requests.exceptions.RequestException as rqst:
            return {"error":str(rqst)}    
