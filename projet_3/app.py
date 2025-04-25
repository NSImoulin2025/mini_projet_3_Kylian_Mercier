from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import hashlib
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route("/")
def home():
    """
    Affiche la page d'accueil.
    Si une session utilisateur est active, elle est transmise au template.
    """
    return render_template("index.html", session=session)

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Gère l'authentification des utilisateurs.
    - En GET : affiche le formulaire de connexion.
    - En POST : vérifie les identifiants saisis, et connecte l'utilisateur si correct.
    """
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

    # Si méthode GET
    return render_template("login.html") 

@app.route("/secret")
def secret():
    """
    Page accessible uniquement aux utilisateurs connectés.
    Si l'utilisateur n'est pas authentifié, il est redirigé vers la page de connexion.
    """
    if "user" in session:
        return render_template("secret.html")
    else:
        return redirect(url_for("login"))  

@app.route("/logout")
def logout():
    """
    Déconnecte l'utilisateur en supprimant ses données de session,
    puis redirige vers la page d'accueil.
    """
    session.pop("user", None)  
    return redirect(url_for("home"))

def get_db_connection():
    """
    Crée et retourne une connexion à la base de données SQLite.
    Configure le curseur pour retourner des lignes accessibles par nom de colonne.
    """
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Gère l'enregistrement d'un nouvel utilisateur.
    - En GET : affiche le formulaire d'inscription.
    - En POST : crée un nouvel utilisateur avec un mot de passe haché.
    Empêche les doublons de noms d'utilisateur grâce à une contrainte d'intégrité.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Hachage du mot de passe
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
        # Ouvre une connexion à SQLite
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            return redirect(url_for("login"))  
        except sqlite3.IntegrityError:
            return "Nom d'utilisateur déjà pris !"

        conn.close()

    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)
