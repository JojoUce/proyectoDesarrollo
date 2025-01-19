import requests
from app.config import Config

class RecipeService:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.url = Config.GEMINI_API_URL

    def fetch_recipes(self, ingredients):
        response = requests.post(self.url, 
                                 json={"ingredients": ingredients},
                                 headers={"Authorization": f"Bearer {self.api_key}"})
        return response.json()
