from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_jwt_extended import create_access_token
import os
import jwt
import datetime

# Cargar las variables del archivo .env
load_dotenv()

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://u911718531_senati:S3nati123@srv1851.hstgr.io/u911718531_moviles20251'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desactivar el rastreo de modificaciones para ahorrar memoria
app.config['SECRET_KEY'] = 'rootgS3nati123'  # Cambiar esto por una clave más segura

# Inicializamos la base de datos y Flask-Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Inicializar el JWTManager con la aplicación Flask
jwt = JWTManager(app)

# Modelo para la tabla Vigilante
class Vigilante(db.Model):
    __tablename__ = 'vigilante'
    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(50), nullable=False, unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f"<Vigilante {self.nombre}>"

# Modelo para la tabla Alumno
class Alumno(db.Model):
    __tablename__ = 'alumnos'
    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(50), nullable=False, unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    programa_estudios = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(50), nullable=True)
    observaciones = db.Column(db.String(200), nullable=True)
    password = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f"<Alumno {self.nombre}>"

# Ruta para registrar un vigilante
@app.route('/register_vigilante', methods=['POST'])
def register_vigilante():
    try:
        # Obtener datos desde la solicitud
        dni = request.json.get('dni', None)
        nombre = request.json.get('nombre', None)
        password = request.json.get('password', None)

        # Verificar si el vigilante ya existe
        vigilante = Vigilante.query.filter_by(dni=dni).first()
        if vigilante:
            return jsonify({"msg": "El vigilante con este DNI ya existe"}), 400

        # Encriptar la contraseña
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        # Crear un nuevo vigilante
        nuevo_vigilante = Vigilante(dni=dni, nombre=nombre, password=hashed_password)
        db.session.add(nuevo_vigilante)
        db.session.commit()

        return jsonify({"msg": "Vigilante registrado exitosamente"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500

# Ruta para registrar un alumno
@app.route('/register_alumnos', methods=['POST'])
def register_alumno():
    try:
        # Obtener datos desde la solicitud
        dni = request.json.get('dni', None)
        nombre = request.json.get('nombre', None)
        programa_estudios = request.json.get('programa_estudios', None)
        estado = request.json.get('estado', None)
        observaciones = request.json.get('observaciones', None)
        password = request.json.get('password', None)

        # Verificar si todos los datos requeridos están presentes
        if not all([dni, nombre, programa_estudios, password]):
            return jsonify({"msg": "Faltan datos obligatorios"}), 400

        # Verificar si el alumno ya existe
        alumno = Alumno.query.filter_by(dni=dni).first()
        if alumno:
            return jsonify({"msg": "El alumno con este DNI ya existe"}), 400

        # Encriptar la contraseña antes de guardarla
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        # Crear un nuevo alumno
        nuevo_alumno = Alumno(
            dni=dni,
            nombre=nombre,
            programa_estudios=programa_estudios,
            estado=estado,
            observaciones=observaciones,
            password=hashed_password
        )

        db.session.add(nuevo_alumno)
        db.session.commit()

        return jsonify({"msg": "Alumno registrado exitosamente"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500

# Ruta de inicio de sesión para vigilantes
@app.route('/login_vigilante', methods=['POST'])
def login_vigilante():
    dni = request.json.get('dni', None)
    password = request.json.get('password', None)

    # Buscar el vigilante por DNI
    vigilante = Vigilante.query.filter_by(dni=dni).first()

    if not vigilante:
        return jsonify({"msg": f"No se encontró el vigilante con DNI: {dni}"}), 404

    # Verificar la contraseña
    if not check_password_hash(vigilante.password, password):
        return jsonify({"msg": "Credenciales incorrectas"}), 401

    # Crear token JWT
    payload = {
        "dni": vigilante.dni,
        "password": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = create_access_token(identity=payload)

    return jsonify({"token": token}), 200

# Ruta de inicio de sesión para alumnos
@app.route('/login_alumnos', methods=['POST'])
def login_alumno():
    dni = request.json.get('dni', None)
    password = request.json.get('password', None)

    # Buscar el alumno por DNI
    alumno = Alumno.query.filter_by(dni=dni).first()

    if not alumno or not check_password_hash(alumno.password, password):
        return jsonify({"msg": "Credenciales incorrectas"}), 401

    # Crear token JWT
    payload = {
        "dni": alumno.dni,
        "password": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = create_access_token(identity=payload)

    return jsonify({"token": token}), 200

# Ruta protegida para acceder con JWT
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# Ruta para obtener todos los alumnos
@app.route('/alumnos', methods=['GET'])
@jwt_required()
def get_alumnos():
    alumnos = Alumno.query.all()
    return jsonify([{
        "id": alumno.id,
        "dni": alumno.dni,
        "nombre": alumno.nombre,
        "programa_estudios": alumno.programa_estudios,
        "estado": alumno.estado,
        "observaciones": alumno.observaciones,
    } for alumno in alumnos])

# Ruta para obtener todos los vigilantes
@app.route('/vigilantes', methods=['GET'])
@jwt_required()
def get_vigilantes():
    vigilantes = Vigilante.query.all()
    return jsonify([{
        "dni": vigilante.dni,
        "password": vigilante.password,
    } for vigilante in vigilantes])

if __name__ == '__main__':
    app.run(debug=True)









  #  scrypt:32768:8:1$cAFuIKgFD1A6KBZ9$5c799f200485ed4c










 # if not alumno or not check_password_hash(alumno.password, password):


  #if not alumno or not check_password_hash("1$cAFuIKgFD1A6KBZ9$5c799f200485ed4c", pas
