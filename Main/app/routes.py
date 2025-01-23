from flask import Blueprint, jsonify, request
from app.services.recipe_service import recipeService

main = Blueprint('main', __name__)

def init_routes(app):
    @app.route('/ingredients', methods=['POST'])
    def get_recipes():
        # Obtener los ingredientes
        data = request.json
        ingredients = data.get("ingredients")
        
        if not ingredients:
            return jsonify({"error": "No se ingresó ingredientes"}), 400   

        # Instanciar el servicio y obtener las recetas
        recipe_service = recipeService()
        recipe = recipe_service.fetch_recipes(ingredients)
        
        if "error" in recipe:
            return jsonify({"error": recipe["error"]}), 500
        
        return jsonify({"Recetas": recipe})
