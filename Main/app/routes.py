from flask import Flask, request, jsonify

def init_routes(app):
    @app.route('/ingredients', methods=['POST'])
    def get_recipes():
        data = request.json
        
        return jsonify({"message": "Recetas personalizadas generadas"})