# Página web creada con Flask por NICOLÁS DE RIVAS
# Importamos todas las librerías que voy a usar, la función form me permite importar solo algunas partes
# de una librería por motivos de optimización
from flask import Flask, redirect, url_for, render_template, request, session, flash # Librería de página web
from flask_sqlalchemy import SQLAlchemy # Base de datos utilizando SQLAlchemy basado en SQL
import bcrypt # Librería de brypt para hashear contraseás y almacenarla de forma segura

# Iniciar las librerías y sus parámetros iniciales
app = Flask(__name__)
app.secret_key = "nderivasmorillo"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class users(db.Model):
	_id = db.Column("id", db.Integer, primary_key=True)
	username = db.Column(db.String(100))
	name = db.Column(db.String(100))
	email = db.Column(db.String(100))
	password = db.Column(db.String(100))
	role = db.Column(db.String(100))

	def __init__(self, username, password, email, name, role):
		self.username = username
		self.password = password
		self.email = email
		self.name = name
		self.role = role
		if self.username == "admin":
			self.role = "ADMIN"

@app.route("/")
def home():
	return render_template("index.html")

@app.route("/view/")
def view():
	if "role" in session:
		if session["role"] == "ADMIN":
			return render_template("view.html", values=users.query.all())
		else:
			return redirect(url_for("login"))
	else:
		return redirect(url_for("login"))

@app.route("/register/", methods=["POST", "GET"])
def register():
	if request.method == "POST":
		user = request.form["nm"]
		pwd = request.form["pw"].encode("utf-8")
		pwd_confirmation = request.form["pwconf"].encode("utf-8")
		if users.query.filter_by(username = user).first() != None:
			flash("Ese usuario ya exite", "info")
			return redirect(url_for("login"))
		else:
			if pwd == pwd_confirmation:
				usr = users(user, bcrypt.hashpw(pwd, bcrypt.gensalt()), "", "", "USER")
				db.session.add(usr)
				db.session.commit()
				return redirect(url_for("user"))
			else:
				flash("Wrong confirmation", "info")
				return render_template("register.html")
	else:
		if "user" in session:
			return redirect(url_for("user"))
		return render_template("register.html")

@app.route("/login/", methods=["POST", "GET"])
def login():
	if request.method == "POST":
		user = request.form["nm"]
		pwd = request.form["pw"].encode("utf-8")

		found_user = users.query.filter_by(username = user).first()

		if found_user != None:
			if bcrypt.checkpw(pwd, found_user.password):
				session["email"] = found_user.email
				session["user"] = found_user.username
				session["name"] = found_user.name
				session["role"] = found_user.role
				flash("Has entrado como " + session["user"].title(), "info")
				return redirect(url_for("user"))
			else:
				flash("Nombre o contraseña incorrecta", "info")
				return redirect(url_for("login"))
		else:
			flash("Nombre o contraseña incorrecta", "info")
			return redirect(url_for("login"))
	else:
		if "user" in session:
			return redirect(url_for("user"))
		return render_template("login.html")

@app.route("/user/", methods=["POST", "GET"])
def user():
	email = None
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
			flash("Nueva información guardada", "info")
		else:
			if "email" in session:
				email = session["email"]
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
	last_user = session["user"]
	session.clear()
	flash(last_user.title() + " ha salido", "info")
	return redirect(url_for("home"))

@app.route("/admin/", methods = ["POST", "GET"])
def admin():
	if request.method == "POST":
		user_to_delete = request.form["ur"]
		user_to_ascend = request.form["ua"]
		object_ascend = users.query.filter_by(username = user_to_ascend).first()
		object_delete = users.query.filter_by(username = user_to_delete).first()
		if object_ascend != None:
			if object_ascend.role == "ADMIN":
				flash(user_to_ascend + " ya es administrador", "info")
			else:
				object_ascend.role = "ADMIN"
				db.session.commit()
				flash(user_to_ascend + " ahora es administrador", "info")
		if object_delete != None:
			if object_delete.role == "ADMIN":
				flash("No puedes eliminar administradores", "info")
			else:
				db.session.delete(object_delete)
				db.session.commit()
				flash(user_to_delete + "	 eliminado", "info")
	return render_template("admin.html")

if __name__ == "__main__":
	db.create_all()
	app.run(debug=True)
	
