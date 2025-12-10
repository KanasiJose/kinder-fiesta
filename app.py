import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from config import Config
from models import db, Salon, Comentario

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

ADMIN_PASSWORD = "admin123"  # contraseña 

# Crear BD si no existe
with app.app_context():
    db.create_all()
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

@app.route("/")
def index():
    salones = Salon.query.filter_by(aprobado=True).all()
    return render_template("index.html", salones=salones)

@app.route("/salon/<int:salon_id>", methods=["GET", "POST"])
def salon_detail(salon_id):
    salon = Salon.query.get_or_404(salon_id)
    if request.method == "POST":
        nombre = request.form["nombre"]
        comentario = request.form["comentario"]
        calificacion = int(request.form["calificacion"])
        nuevo_comentario = Comentario(
            nombre_usuario=nombre,
            texto=comentario,
            calificacion=calificacion,
            salon=salon
        )
        db.session.add(nuevo_comentario)
        db.session.commit()
        flash("Comentario agregado con éxito.", "success")
        return redirect(url_for("salon_detail", salon_id=salon_id))
    return render_template("salon_detail.html", salon=salon)

@app.route("/add_salon", methods=["GET", "POST"])
def add_salon():
    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        contacto = request.form["contacto"]
        ubicacion = request.form["ubicacion"]

        file = request.files["imagen"]
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        nuevo_salon = Salon(
            nombre=nombre,
            descripcion=descripcion,
            contacto=contacto,
            ubicacion=ubicacion,
            imagen=filename,
            aprobado=False
        )
        db.session.add(nuevo_salon)
        db.session.commit()
        flash("Salón enviado para aprobación.", "info")
        return redirect(url_for("index"))
    return render_template("add_salon.html")

@app.route("/login_admin", methods=["GET", "POST"])
def login_admin():
    if request.method == "POST":
        password = request.form["password"]
        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("panel_admin"))
        else:
            flash("Contraseña incorrecta", "danger")
    return render_template("login_admin.html")

@app.route("/panel_admin")
def panel_admin():
    if not session.get("admin"):
        return redirect(url_for("login_admin"))
    salones = Salon.query.all()
    return render_template("panel_admin.html", salones=salones)

@app.route("/aprobar/<int:salon_id>")
def aprobar_salon(salon_id):
    if not session.get("admin"):
        return redirect(url_for("login_admin"))
    salon = Salon.query.get_or_404(salon_id)
    salon.aprobado = True
    db.session.commit()
    flash("Salón aprobado correctamente.", "success")
    return redirect(url_for("panel_admin"))

# 🗑️ Nueva ruta para eliminar salones
@app.route("/eliminar/<int:salon_id>", methods=["POST", "GET"])
def eliminar_salon(salon_id):
    if not session.get("admin"):
        return redirect(url_for("login_admin"))
    
    salon = Salon.query.get_or_404(salon_id)

    # Eliminar comentarios relacionados
    for comentario in salon.comentarios:
        db.session.delete(comentario)

    # Eliminar imagen del servidor (si existe)
    if salon.imagen:
        ruta_imagen = os.path.join(app.config["UPLOAD_FOLDER"], salon.imagen)
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

    # Eliminar el salón
    db.session.delete(salon)
    db.session.commit()
    flash("Salón eliminado correctamente.", "success")
    return redirect(url_for("panel_admin"))

@app.route('/favicon.ico')
def favicon():
    return '', 204


if __name__ == "__main__":
    app.run(debug=True)
