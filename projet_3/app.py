from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import hashlib
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route("/")
def home():
     return render_template("index.html", session=session)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Connexion à la base de données
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # Récupérer le mot de passe hashé depuis la base
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user:
            # Hachage du mot de passe entré et comparaison
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if hashed_password == user[0]:  
                session["user"] = username
                return redirect(url_for("secret"))
            else:
                return "Mot de passe incorrect !"
        else:
            return "Utilisateur introuvable !"

    return render_template("login.html") # Si méthode GET

@app.route("/secret")
def secret():
    print("Session actuelle :", session)  # Vérification
    if "user" in session:
        return render_template("secret.html")
    else:
        return redirect(url_for("login"))  # Redirige vers /login si l'utilisateur n'est pas connecté

@app.route("/logout")
def logout():
    session.pop("user", None)  # Supprime l'utilisateur de la session
    return redirect(url_for("home"))

# Connexion à la base de données
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Hachage du mot de passe
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            return redirect(url_for("login"))  # Redirection vers la connexion après inscription
        except sqlite3.IntegrityError:
            return "Nom d'utilisateur déjà pris !"

        conn.close()

    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)