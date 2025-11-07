from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from sqlalchemy import select  # Necesario para las consultas GET modernas
from flask_bcrypt import Bcrypt

# ==============================================
# 1. CARGA DE VARIABLES DE ENTORNO
# Carga las variables desde el archivo .env (solo para desarrollo local)
load_dotenv()
# ==============================================

app = Flask(__name__)

# --- 2. CONFIGURACIÓN DE CONEXIÓN ---
DB_USER = os.environ.get("MYSQLUSER")
DB_PASS = os.environ.get("MYSQLPASSWORD")
DB_HOST = os.environ.get("MYSQLHOST")
DB_PORT = os.environ.get("MYSQLPORT")
DB_NAME = os.environ.get("MYSQLDATABASE")

# Construye la URI de conexión
app.config['SQLALCHEMY_DATABASE_URI'] = \
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)  # Inicializa Bcrypt para hashing de contraseñas


# --- 3. DEFINICIÓN DEL MODELO ---
class User(db.Model):
    # Nombre de la tabla en tu base de datos de Railway
    __tablename__ = 'usuario'

    # Mapeo de columnas
    id_usuario = db.Column(db.Integer, primary_key=True)
    nom_1 = db.Column(db.String(50), nullable=False)
    nom_2 = db.Column(db.String(50))
    app_1 = db.Column(db.String(50), nullable=False)
    app_2 = db.Column(db.String(50))
    correo = db.Column(db.String(120), unique=True, nullable=False)  # Aumentado a 120 por seguridad
    contraseña = db.Column(db.String(255), nullable=False)  # Longitud larga para el hash de Bcrypt

    def to_dict(self):
        """Método para serializar el objeto a diccionario/JSON"""
        return {
            "id": self.id_usuario,
            "nombre1": self.nom_1,
            "nombre2": self.nom_2,
            "apellido1": self.app_1,
            "apellido2": self.app_2,
            "correo": self.correo,
            # NOTA: La contraseña (hash) NUNCA se devuelve
        }


# ======================================================
# RUTAS DE LA API
# ======================================================

@app.route('/')
def root():
    return jsonify("Hello World")


# RUTA GET: Obtener un usuario por ID
@app.route("/users/<int:id_user>")
def get_user(id_user):
    # Consulta la DB por la columna id_usuario
    stmt = select(User).filter_by(id_usuario=id_user)
    user = db.session.execute(stmt).scalar_one_or_none()

    if user is None:
        return jsonify({"error": f"Usuario con ID {id_user} no encontrado"}), 404

    user_data = user.to_dict()

    # Mantiene la lógica del query param
    query = request.args.get("query")
    if query:
        user_data["query"] = query

    return jsonify(user_data), 200


# RUTA POST: Crear un nuevo usuario
@app.route("/users/", methods=["POST"])
def create_user():
    data = request.get_json()

    # 1. Validar campos obligatorios
    required_fields = ['nom_1', 'app_1', 'correo', 'contraseña']
    if any(field not in data for field in required_fields):
        return jsonify({"error": "Faltan campos obligatorios: nom_1, app_1, correo, contraseña"}), 400

    try:
        # 2. Hashear la contraseña por seguridad
        hashed_password = bcrypt.generate_password_hash(data["contraseña"]).decode('utf-8')

        # 3. Crear el nuevo objeto para guardar
        new_user = User(
            nom_1=data["nom_1"],
            nom_2=data.get("nom_2"),
            app_1=data["app_1"],
            app_2=data.get("app_2"),
            correo=data["correo"],
            contraseña=hashed_password  # Guarda el hash
        )

        # 4. Guardar en la base de datos
        db.session.add(new_user)
        db.session.commit()

        # 5. Devolver la respuesta exitosa (omitiendo la contraseña)
        return jsonify(new_user.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error al crear el usuario. ¿El correo ya existe?", "detalle": str(e)}), 500


if __name__ == '__main__':
    # NECESARIO: Inicializar el contexto de la aplicación para SQLAlchemy
    with app.app_context():
        # Crea las tablas si no existen (útil para la primera vez)
        db.create_all()

    app.run(debug=True)
