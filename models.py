from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Salon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    imagen = db.Column(db.String(200), nullable=True)
    contacto = db.Column(db.String(100), nullable=True)
    ubicacion = db.Column(db.String(200), nullable=True)
    aprobado = db.Column(db.Boolean, default=False)

    comentarios = db.relationship("Comentario", backref="salon", lazy=True)

class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(100), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    calificacion = db.Column(db.Integer, nullable=False)
    salon_id = db.Column(db.Integer, db.ForeignKey("salon.id"), nullable=False)
