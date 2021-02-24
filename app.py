import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check username
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        mongo.db.users.insert_one({
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        })

        session["user"] = request.form.get("username").lower()
        flash("Register Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        """
        check username
        """
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            """
            ensure hashed password matches user input
            """
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(
                        request.form.get("username")))
                    return redirect(url_for(
                        "profile", username=session["user"]))
            else:
                """
                invalid password match
                """
                flash("Incorrect Username or Password")
                return redirect(url_for("login"))

        else:
            """
            username doesn't exist
            """
            flash("Incorrect Username or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/get_notes")
def get_notes():
    notes = mongo.db.notes.find()
    return render_template("notes.html", notes=notes)


@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_note", methods=["GET", "POST"])
def add_note():
    if request.method == "POST":
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        note = {
            "note_name": request.form.get("note_name"),
            "note_description": request.form.get("note_description"),
            "due_date": request.form.get("due_date"),
            "is_urgent": is_urgent,
            "created_by": session["user"]
        }
        mongo.db.notes.insert_one(note)
        flash("Note Noted!")
        return redirect(url_for("get_notes"))

    return render_template("add_notes.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
