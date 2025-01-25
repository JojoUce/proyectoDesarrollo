from app.models import UsuarioRestricciones, RestriccionesDieteticas, db

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
        
        # Filtrar las restricciones dietéticas del usuario
        ingredientes_restringidos = set()
        if usuario_id: # type: ignore
            restricciones_ids = [
                ur.restriccion_id
                for ur in UsuarioRestricciones.query.filter_by(usuario_id=usuario_id).all() # type: ignore
            ]
            restricciones = RestriccionesDieteticas.query.filter(RestriccionesDieteticas.id.in_(restricciones_ids)).all()
            ingredientes_restringidos = {r.nombre.lower() for r in restricciones}

        # Filtrar recetas basadas en las restricciones e ingredientes dados
        matching_recipes = []
        for recipe in recipes_db:
            if any(ingredient.lower() in ingredientes_restringidos for ingredient in recipe["ingredients"]):
                continue
            if all(ingredient in recipe["ingredients"] for ingredient in ingredients):
                matching_recipes.append(recipe)
        
        if not matching_recipes:
            return {"error": "No se encontraron recetas con los ingredientes proporcionados"}
        
        return matching_recipes
