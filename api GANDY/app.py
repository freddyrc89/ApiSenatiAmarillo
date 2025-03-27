from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_migrate import Migrate  # Asegúrate de importar Migrate solo una vez
from dotenv import load_dotenv
import os

# Cargar las variables del archivo .env
load_dotenv()

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://u911718531_senati:S3nati123@srv1851.hstgr.io/u911718531_moviles20251'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desactivar el rastreo de modificaciones para ahorrar memoria
app.config['JWT_SECRET_KEY'] = 'rootgS3nati123'  # Cambiar esto por una clave más segura

# Inicializamos la base de datos y Flask-Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Ahora puedes seguir con la definición de las rutas y los modelos


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
    password =db.Column(db.String(50), nullable=True)
    
    def __repr__(self):
        return f"<Alumnos {self.nombre}>"

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
        hashed_password = generate_password_hash(password)

        # Crear un nuevo vigilante
        nuevo_vigilante = Vigilante(dni=dni, nombre=nombre, password=hashed_password)
        db.session.add(nuevo_vigilante)
        db.session.commit()

        return jsonify({"msg": "Vigilante registrado exitosamente"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500
    
    # Ruta para registrar un alumnos
    
@app.route('/register_alumnos', methods=['POST'])
def register_alumno():
    try:
        # Obtener datos desde la solicitud
        dni = request.json.get('dni', None)
        nombre = request.json.get('nombre', None)
        programa_estudios = request.json.get('programa_estudios', None)
        estado = request.json.get('estado', None)
        observaciones = request.json.get('observaciones', None)
        password = request.json.get('password', None)  # ✅ Cambio aquí

        # Verificar si todos los datos requeridos están presentes
        if not all([dni, nombre, programa_estudios, password]):
            return jsonify({"msg": "Faltan datos obligatorios"}), 400

        # Verificar si el alumno ya existe
        alumno = Alumno.query.filter_by(dni=dni).first()  
        if alumno:
            return jsonify({"msg": "El alumno con este DNI ya existe"}), 400

        # Encriptar la contraseña antes de guardarla
        hashed_password = generate_password_hash(password)

        # Crear un nuevo alumno
        nuevo_alumno = Alumno(
            dni=dni,
            nombre=nombre,
            programa_estudios=programa_estudios,
            estado=estado,
            observaciones=observaciones ,
            password=hashed_password  # ✅ Cambio aquí
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
    if not vigilante or not check_password_hash(vigilante.password, password):
        return jsonify({"msg": "Credenciales incorrectas"}), 401

    # Crear token JWT
    access_token = create_access_token(identity=vigilante.dni)
    return jsonify(access_token=access_token), 200

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
        "id": alumnos.id,
        "dni": alumnos.dni,
        "nombre": alumnos.nombre,
        "programa_estudios": alumnos.programa_estudios,
        "estado": alumnos.estado,
        "observaciones": alumnos.observaciones,
    } for alumnos in alumnos])

# Ruta para obtener todos los vigilantes
@app.route('/vigilantes', methods=['GET'])
@jwt_required()
def get_vigilantes():
    vigilantes = Vigilante.query.all()
    return jsonify([{
        "id": vigilante.id,
        "dni": vigilante.dni,
        "nombre": vigilante.nombre,
    } for vigilante in vigilantes])

if __name__ == '__main__':
    app.run(debug=True)
