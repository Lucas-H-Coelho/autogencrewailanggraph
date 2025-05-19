# Endpoints RESTful
# Atualmente, os endpoints estão em app.py para simplicidade.
# Em uma aplicação maior, eles poderiam ser movidos para cá usando Blueprints do Flask.

def init_api(app):
    # Exemplo de como registrar um Blueprint se os endpoints fossem movidos:
    # from .routes import api_blueprint
    # app.register_blueprint(api_blueprint, url_prefix='/api')
    print("Módulo API inicializado (endpoints em app.py)")
