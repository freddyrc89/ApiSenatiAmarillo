from flask_sqlalchemy import SQLAlchemy

# Crear una instancia de SQLAlchemy
db = SQLAlchemy()

# Modelo para la tabla 'alumnos'
class Alumno(db.Model):
    __tablename__ = 'alumnos'

    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(10), unique=True, nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    programa_estudios = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.Enum('A', 'D', name='estado_enum'), nullable=False)
    observaciones = db.Column(db.Text, nullable=True)
    password = db.Column(db.String(255), nullable=True)  # ✅ Cambio aquí

    def __repr__(self):
        return f"<Alumno {self.nombre}>"

# Modelo para la tabla 'vigilante'
class Vigilante(db.Model):
    __tablename__ = 'vigilante'

    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(10), nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Vigilante {self.nombre}>"