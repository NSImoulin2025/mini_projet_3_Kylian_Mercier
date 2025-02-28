from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "1234":
            return "Connexion réussie !"
        else:
            return "Identifiants incorrects !"

    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)
