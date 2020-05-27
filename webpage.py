
                                                    # Página web creada con Flask por NICOLÁS DE RIVAS
                                                    # Importamos todas las librerías que voy a usar, la función form me permite importar solo algunas partes
                                                    # de una librería por motivos de optimización
from flask import Flask, redirect, url_for, render_template, request, session, flash # Librería de página web
from flask_sqlalchemy import SQLAlchemy             # Base de datos utilizando SQLAlchemy basado en SQL
import bcrypt                                       # Librería de brypt para hashear contraseás y almacenarla de forma segura
import smtplib, ssl
import git

                                                    # Iniciar las librerías y sus parámetros iniciales
app = Flask(__name__)
app.secret_key = "nderivasmorillo"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
port = 465
smtp_server = "smtp.gmail.com"
sender_email = "web.nicolas.noreply@gmail.com"
password = "20030326Nico."

                                                    # Creo la clase usuario con la que registraré todos los nuevos usuarios
class users(db.Model):                              # La clase sigue el modelo de archivo SQL - Los archivos SQL se pueden ver como excels
    _id = db.Column("id", db.Integer, primary_key=True) # Creamos una columna que contenga las ids (Int) de los usuarios ya que es obligatorio
    username = db.Column(db.String(100))            # Columna para nombres de usuario (String) y repetimos para las demás
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    role = db.Column(db.String(100))

    def __init__(self, username, password, email, name, role): # Definimos como se tiene que inicializar esta clase
        self.username = username                    # Establecemos la variables de cada objeto al valor con el que se ha iniciado la clase
        self.password = password
        self.email = email
        self.name = name
        self.role = role

@app.route('/update_server', methods=['POST'])
    def webhook():
        if request.method == 'POST':
            repo = git.Repo('path/to/git_repo')
            origin = repo.remotes.origin
            origin.pull()
            return 'Updated PythonAnywhere successfully', 200
        else:
            return 'Wrong event type', 400
        
@app.route("/")                                     # http://host/ hará lo siguiente
def home():                                         # función que se va a ejecutar
    return render_template("index.html")            #Renderizamos archivo HTML

@app.route("/register/", methods=["POST", "GET"])   # En la ruta /register/ establecemos los métodos de POST y GET, Post sucede cuando el servidor recive información y Get cuando la manda
def register():
    if request.method == "POST":                    # Cuando el servidor reciba información del formulario HTML (register.html)
        user = request.form["nm"]                   # Coge información de nombre de usuario
        pwd = request.form["pw"].encode("utf-8")    # Para la contraseña y su información coge la información y la pasa a bytes con utf-8
        pwd_confirmation = request.form["pwconf"].encode("utf-8") # Hacemos esto ya que solo se pueden hashear bytes y no strings
        if users.query.filter_by(username = user).first() != None: # Buscamos en el archivo SQL por el nombre y comprobamos si existe
            flash("Ese usuario ya exite ❌", "info")   # Si existe mandamos un mensaje "flash" (temporal) al ususario diciendole que ese usuario ya exite
            return redirect(url_for("login"))       # le redirigimos a la página de login
        else: # SI no exite
            if pwd == pwd_confirmation:             # Si la contraseña es igual a la confirmación
                usr = users(user, bcrypt.hashpw(pwd, bcrypt.gensalt()), "", "", "USER") # Creamos objeto de usuario con las siguientes variables
                                                    # bcrypt.hashpw(pw, salt) hashea nuestra contraseña
                db.session.add(usr)                 # Añadimos el nuevo usuario "usr" a la base de datos
                db.session.commit()                 # Confirmamos los cambios en la base de datos
                return redirect(url_for("user"))    # redirigimos a la mágina de user
            else:                                   # Si la contraseña no es igual a la confirmación
                flash("Confirmación incorrecta ❌", "info")
                return render_template("register.html")
    else:
        if "user" in session:                       # Si el usuario ya está en la sesión
            return redirect(url_for("user"))
        return render_template("register.html")

@app.route("/login/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["nm"]
        pwd = request.form["pw"].encode("utf-8")

        found_user = users.query.filter_by(username = user).first()

        if found_user != None:
            if bcrypt.checkpw(pwd, found_user.password): # Comprobamos si el hash almacenado pertenee a la contraseña
                session["email"] = found_user.email
                session["user"] = found_user.username # Establecemos datos de la sesión
                session["name"] = found_user.name
                session["role"] = found_user.role
                flash("Has entrado como " + session["user"].title() + " ✔️", "info")
                return redirect(url_for("user"))
            else:
                flash("Nombre o contraseña incorrecta ❌", "info")
                return redirect(url_for("login"))
        else:
            flash("Nombre o contraseña incorrecta ❌", "info")
            return redirect(url_for("login"))
    else:
        if "user" in session:
            return redirect(url_for("user"))
        return render_template("login.html")

@app.route("/user/", methods=["POST", "GET"])
def user():
    email = None
    name = None
    if "user" in session:
        user = session["user"]
        if request.method == "POST":
            email = request.form["email"]
            name = request.form["real_name"]
            session["name"] = name
            session["email"] = email
            found_user = users.query.filter_by(username = user).first()
            found_user.email = email
            found_user.name = name
            db.session.commit()
            message = """\
            Hola!

            Bienvenido a la web de Nico de Rivas, espero que disfrutes!"""

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, session["email"], message)
            flash("Nueva información guardada ✔️", "info")
        else:
            if "email" in session:
                email = session["email"]
                name = session["name"]
        return render_template("user.html")
    else:
        return redirect(url_for("login"))

@app.route("/Historia/")
def historia():
    return render_template("historia.html")

@app.route("/Referencias/")
def referencias():
    return render_template("referencias.html")

@app.route("/Pruebas/")
def pruebas():
    return render_template("pruebas.html")

@app.route("/logout/")
def logout():
    last_user = session["user"]                         # guardamos el usuario con el que estábamos
    session.clear()                                     # Limpiamos la sesión
    flash(last_user.title() + " ha salido ✔️", "info")
    return redirect(url_for("home"))

@app.route("/admin/", methods = ["POST", "GET"])
def admin():
    if "role" in session:                               # Si la sesión tiene la variable "role" (Para evitar gente metiendose sin cueta)
        if session["role"] == "ADMIN":
            if request.method == "POST":
                user_to_delete = request.form["ur"]
                user_to_ascend = request.form["ua"]
                object_ascend = users.query.filter_by(username = user_to_ascend).first()
                object_delete = users.query.filter_by(username = user_to_delete).first()
                if object_ascend != None:
                    if object_ascend.role == "ADMIN":
                        flash(user_to_ascend + " ya es administrador ❌", "info")
                    else:
                        object_ascend.role = "ADMIN"
                        db.session.commit()
                        flash(user_to_ascend + " ahora es administrador ✔️", "info")
                if object_delete != None:
                    if object_delete.role == "ADMIN":
                        flash("No puedes eliminar administradores ❌", "info")
                    else:
                        db.session.delete(object_delete)# Borrar objeto de la base de datos
                        db.session.commit()
                        flash(user_to_delete + " eliminado ✔️", "info")
            return render_template("admin.html", values=users.query.all())
        else:
            return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))
    return render_template("admin.html")

if __name__ == "__main__":                              # Al iniciar la app
    db.create_all()                                     # Creamos las bases de datos
    app.run(debug=True)                                 # ejecutamos la app, debug = True para actualizar cambios automáticamente

# PARA LANZAR LA WEB A TU RED LOCAL
# Abres la CMD y escribes ipconfig el apartado Dirección IPv4 tendrá un número como 192.168.1.43
# añades host='*IPv4*' a los parámetros de app.run() y ya puedes acceder desde cualquier dispositivo conectado al mismo router
# EJEMPLO:
# app.run(debug=True, host='192.168.1.43')
