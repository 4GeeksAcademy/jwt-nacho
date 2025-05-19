"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from api.utils import APIException, generate_sitemap
from api.models import db
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands
from flask_cors import CORS
from api.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import JWTManager,create_access_token,jwt_required,get_jwt_identity

from datetime import timedelta

# from models import Person

ENV = "development" if os.getenv("FLASK_DEBUG") == "1" else "production"
static_file_dir = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '../public/')
app = Flask(__name__)
app.url_map.strict_slashes = False

CORS(app, supports_credentials=True, origins=["http://localhost:3000"])
jwt= JWTManager(app)
@jwt.unauthorized_loader
def unauthorized_callback(error):
    # Se llama cuando no se proporciona ningún token
    return jsonify({"msg": "Falta el encabezado Authorization"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    # Se llama cuando el token es inválido (ej. mal formado)
    return jsonify({"msg": f"Token inválido: {error}"}), 422

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    # Se llama cuando el token está expirado
    return jsonify({"msg": "El token ha expirado"}), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "El token ha sido revocado"}), 401

@jwt.needs_fresh_token_loader
def needs_fresh_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "Se requiere un token fresco"}), 401
app.config["JWT_SECRET_KEY"] = os.environ.get("FLASK_APP_KEY")
app.config["JWT_ALGORITHM"] = "HS256"
# database condiguration
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type=True)
db.init_app(app)

# add the admin
setup_admin(app)

# add the admin
setup_commands(app)

# Add all endpoints form the API with a "api" prefix
app.register_blueprint(api, url_prefix='/api')

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

@app.route('/signup',methods=['POST'])
def signup():
    body = request.get_json()
    hashed_password = generate_password_hash(body['password'])

    if not body['name'] or not body['lastName'] or not body['email'] or not body['password']:
        return jsonify({"message":"no body"}), 400    
    user= User(
        name=body.get("name"),
        lastName=body.get("lastName"),
        email=body.get("email"),
        password=hashed_password,
        is_active=True
    )
    try:
        db.session.add(user)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()  
        return jsonify({"msg": "El email ya está registrado"}), 409
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"message":"error"}), 400
    
    return jsonify({"message":"ok"}), 200

@app.route('/users',methods=['GET'])
def get_users():
    user= User.query.all()
    return jsonify([u.serialize() for u in user]), 200

@app.route("/login", methods=["POST"])
def login():
    body = request.get_json()
    if not body:
        return jsonify({"message":"no body"}), 400

    user = User.query.filter_by(email=body["email"]).first() or None
    if not user:
        return jsonify({"message":"user not found"}), 404

    if check_password_hash(user.password, body["password"]):
        access_token= create_access_token(identity=str(user.id))
        print("Token generado:", access_token)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"message":"wrong password"}), 401
    
@app.route('/protected', methods=['GET'])
@jwt_required() 
def protected():
    try:
        user_id =int(get_jwt_identity()) 
        print("Usuario ID:", user_id)
        user=User.query.filter_by(id=user_id).first()
        if not user_id:
            return jsonify({"msg": "Usuario no encontrado"}), 404
        return jsonify(user.serialize()), 200
    except Exception as e:
        import traceback
        traceback.print_exc()  # ⬅ para ver la traza del error completa
        return jsonify({"msg": f"Token inválido: {str(e)}"}), 401


# any other endpoint will try to serve it like a static file
@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0  # avoid cache memory
    return response


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)
