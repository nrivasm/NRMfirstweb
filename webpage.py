
                                                    # Página web creada con Flask por NICOLÁS DE RIVAS
                                                    # Importamos todas las librerías que voy a usar, la función form me permite importar solo algunas partes
                                                    # de una librería por motivos de optimización
from flask import Flask, redirect, url_for, render_template, request, session, flash # Librería de página web
from flask_sqlalchemy import SQLAlchemy             # Base de datos utilizando SQLAlchemy basado en SQL
import bcrypt                                       # Librería de brypt para hashear contraseás y almacenarla de forma segura
import smtplib                                      # Librería para emails automatizados
                                                    # Iniciar las librerías y sus parámetros iniciales
app = Flask(__name__)
app.secret_key = "nderivasmorillo"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
port = 465
smtp_server = "smtp.gmail.com"
sender_email = "web.nicolas.noreply@gmail.com"
password = ""
                                                    # Creo la clase usuario con la que registraré todos los nuevos usuarios
class users(db.Model):                              # La clase sigue el modelo de archivo SQL - Los archivos SQL se pueden ver como excels
    _id = db.Column("id", db.Integer, primary_key=True) # Creamos una columna que contenga las ids (Int) de los usuarios ya que es obligatorio
    username = db.Column(db.String(100))            # Columna para nombres de usuario (String) y repetimos para las demás
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    role = db.Column(db.String(100))
    url = db.Column(db.String(100))

    def __init__(self, username, password, email, name, role, url): # Definimos como se tiene que inicializar esta clase
        self.username = username                    # Establecemos la variables de cada objeto al valor con el que se ha iniciado la clase
        self.password = password
        self.email = email
        self.name = name
        self.role = role
        self.url = url
        if username == "admin":
            self.role = "ADMIN"

class comments(db.Model):                           # Clase de los comentarios
    _id = db.Column("id", db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    content = db.Column(db.String(100))
    post_id = db.Column(db.Integer)

    def __init__(self, user_id, content, post_id):
        self.user_id = user_id
        self.content = content
        self.post_id = post_id

class posts(db.Model):                              #Clase de los posts
    _id = db.Column("id", db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    title = db.Column(db.String(100))
    theme = db.Column(db.String(100))
    content = db.Column(db.String(3000))

    def __init__(self, user_id, title, theme, content):
        self.user_id = user_id
        self.title = title
        self.theme = theme
        self.content = content

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
        else: # Si no exite
            if pwd == pwd_confirmation:             # Si la contraseña es igual a la confirmación
                usr = users(user, bcrypt.hashpw(pwd, bcrypt.gensalt()), "", "", "USER", "") # Creamos objeto de usuario con las siguientes variables
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
                session["id"] = found_user._id
                session["email"] = found_user.email
                session["user"] = found_user.username # Establecemos datos de la sesión
                session["name"] = found_user.name
                session["role"] = found_user.role
                session["url"] = found_user.url
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
    url = None
    if "user" in session:
        user = session["user"]
        if request.method == "POST":
            email = request.form["email"]
            name = request.form["real_name"]
            url = request.form["url"]
            session["name"] = name
            session["email"] = email
            session["url"] = url
            found_user = users.query.filter_by(username = user).first()
            found_user.email = email
            found_user.name = name
            found_user.url = url
            db.session.commit()
            message = """\
            Hola!

            Bienvenido a la web de Nico de Rivas, espero que disfrutes!"""

            try:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                    server.login(sender_email, password)
                    server.sendmail(sender_email, session["email"], message)
            except:
                print()
            flash("Nueva información guardada ✔️", "info")
        else:
            if "email" in session:
                email = session["email"]
            if "name" in session:
                name = session["name"]
            if "url" in session:
                url = session["url"]
        return render_template("user.html")
    else:
        return redirect(url_for("login"))

@app.route("/Historia/")
def historia():
    return render_template("historia.html")

@app.route("/Referencias/")
def referencias():
    return render_template("referencias.html")

@app.route("/Foro/",)
def foro():
    posts_to_display = []
    for i in posts.query.all():
        author = users.query.filter_by(_id = i.user_id).first()
        posting_info = [i.title, i.theme, author.username, i._id]
        posts_to_display.append(posting_info)
    return render_template("foro.html", info=posts_to_display.copy(), num=len(posts_to_display))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.route("/logout/")
def logout():
    last_user = session["user"]                         # guardamos el usuario con el que estábamos
    session.clear()                                     # Limpiamos la sesión
    session["url"] = ""
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

@app.route("/Archivo/")
def archivo():
    return render_template("archivo.html")

@app.route("/Nosotros/")
def nosotros():
    return render_template("nosotros.html")

@app.route("/<id>", methods=["POST", "GET"])
def posts_func(id):
    comment = []
    roles=[]
    ids=[]
    post = posts.query.filter_by(_id = id).first()
    poster = users.query.filter_by(_id = post.user_id).first()
    post_info = [post.title, post.theme, post.content, poster]
    for i in comments.query.all():
        user = users.query.filter_by(_id = i.user_id).first()
        comment_info = [user.username, user.url, i.content, user, i._id]
        if i.post_id == int(id):
            comment.append(comment_info)
            roles.append(user.role)
            ids.append(i._id)
    if request.method == "POST":
        if "user" in session:
            author_id = session["id"]
            content = request.form["cont"]
            post_id = id
            cmtn = comments(author_id, content, post_id)
            db.session.add(cmtn)
            db.session.commit()
            return redirect(url_for("posts_func", id=id))
        else:
            flash("Debes entrar a tu cuenta primero", "info")
            return redirect(url_for("login"))
    return render_template("posts.html", lista=comment.copy(), num=len(comment), rl=roles.copy(), post_display=post_info.copy(), identification=id, c_id=ids.copy())

@app.route("/<id>/del/", methods=["POST", "GET"])
def delete_comment(id):
    comment_to_delete = comments.query.filter_by(_id = id).first()
    author_cmt = users.query.filter_by(_id = comment_to_delete.user_id).first()
    if session["role"] == "ADMIN" or author_cmt.username == session["user"]:
        db.session.delete(comment_to_delete)
        db.session.commit()
        flash("Comentario borrado", "info")
        return redirect(url_for("foro"))

@app.route("/<id>/edit/", methods=["POST", "GET"])
def edit_post(id):
    post_to_edit = posts.query.filter_by(_id = id).first()
    if post_to_edit.user_id == session["id"]:
        title = post_to_edit.title
        theme = post_to_edit.theme
        content = post_to_edit.content
        if request.method == "POST":
            post_to_edit.title = request.form["Title"]
            post_to_edit.theme = request.form["Theme"]
            post_to_edit.content = request.form["content"]
            db.session.commit()
            return redirect(url_for("posts_func", id=id))
    return render_template("post.html", ti=title, th=theme, co=content)

@app.route("/<id>/elim/", methods=["POST", "GET"])
def delete_post(id):
    post_to_delete = posts.query.filter_by(_id = id).first()
    post_author = users.query.filter_by(_id = post_to_delete.user_id).first()
    if post_author._id == session["id"] or session["role"] == "ADMIN":
        db.session.delete(post_to_delete)
        for cmt in comments.query.filter_by(post_id = id).all():
            db.session.delete(cmt)
        db.session.commit()
        flash("Post borrado", "info")
        return redirect(url_for("foro"))

@app.route("/post/", methods=["POST", "GET"])
def post():
    if "user" in session:
        if request.method == "POST":
            ttl = request.form["Title"]
            tm = request.form["Theme"]
            cntnt = request.form["content"]
            pt = posts(session["id"], ttl, tm, cntnt)
            db.session.add(pt)
            db.session.commit()
            return redirect(url_for("foro"))
    else:
        flash("Tienes que entrar para crear un nuevo post", "info")
        return redirect(url_for("login"))
    return render_template("post.html", ti="", th="", co="")

if __name__ == "__main__":                              # Al iniciar la app
    db.create_all()                                     # Creamos las bases de datos
    app.run(debug=True)                                 # ejecutamos la app, debug = True para actualizar cambios automáticamente

# PARA LANZAR LA WEB A TU RED LOCAL
# Abres la CMD y escribes ipconfig el apartado Dirección IPv4 tendrá un número como 192.168.1.43
# añades host='*IPv4*' a los parámetros de app.run() y ya puedes acceder desde cualquier dispositivo conectado al mismo router
# EJEMPLO:
# app.run(debug=True, host='192.168.1.43')
