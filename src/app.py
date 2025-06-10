import os
from flask import Flask, request, jsonify, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from api.utils import APIException, generate_sitemap
from api.models import db
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands

# Entorno de desarrollo o producción
ENV = "development" if os.getenv("FLASK_DEBUG") == "1" else "production"

# Ruta base para archivos estáticos si se usa React en modo producción
static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../dist')

# Inicializar la app Flask
app = Flask(__name__)
app.url_map.strict_slashes = False

# Configuración de la base de datos
db_url = os.getenv("DATABASE_URL")
if db_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar DB y migraciones
db.init_app(app)
MIGRATE = Migrate(app, db, compare_type=True)

# Configurar JWT
app.config["JWT_SECRET_KEY"] = os.getenv("FLASK_APP_KEY") or "super-secret-key"
jwt = JWTManager(app)

# Configurar CORS para permitir conexión desde frontend
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

# Configurar admin y comandos
setup_admin(app)
setup_commands(app)

# Registrar blueprint de la API
app.register_blueprint(api, url_prefix='/api')

# Manejador de errores personalizados
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Sitemap solo en modo desarrollo
@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# Servir archivos estáticos (modo producción)
@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0  # evita cache
    return response

# Correr la app
if __name__ == '__main__':
    PORT = int(os.environ.get("PORT", 3001))
    app.run(host="0.0.0.0", port=PORT, debug=True)
