from flask import Flask, request, jsonify
from app.services.recipe_service import recipeService


def init_routes(app):
    @app.route('/ingredients', methods=['POST'])
    
    def get_recipes():
        #Obtener los ingredientes
        data = request.json
        ingredients = data.get("ingredients")
        
        if not ingredients:
            return jsonify({"error": "No se ingresó "}), 400   
        
        #Instancia y obtención de recetas
        recipe_service = recipeService()
        recipe = recipe_service.fetch_recipes(ingredients)
        
        if "error" in recipes:
            return jsonify({"error": recipes["error"]}), 500
        
        return jsonify({"Recetas": recipes]})
       
        
        #return jsonify({"message": "Recetas personalizadas generadas"})
        
        