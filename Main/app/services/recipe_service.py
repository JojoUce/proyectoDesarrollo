class recipeService:
    def __init__(self):
        # No necesitamos ninguna API externa por ahora
        pass

    def fetch_recipes(self, ingredients):
        """ Método para obtener recetas basadas en ingredientes """

        # Aquí definimos recetas fijas para hacer pruebas
        recipes_db = [
            {"name": "Pasta con tomate", "ingredients": ["pasta", "tomate", "ajo", "aceite de oliva"]},
            {"name": "Ensalada de pollo", "ingredients": ["pollo", "lechuga", "tomate", "aceite de oliva"]},
            {"name": "Tortilla de patatas", "ingredients": ["huevo", "patatas", "aceite de oliva", "sal"]},
        ]
        
        matching_recipes = []

        # Recorremos las recetas y comprobamos si contienen todos los ingredientes dados
        for recipe in recipes_db:
            if all(ingredient in recipe["ingredients"] for ingredient in ingredients):
                matching_recipes.append(recipe)
        
        if not matching_recipes:
            return {"error": "No se encontraron recetas con los ingredientes proporcionados"}
        
        return matching_recipes
