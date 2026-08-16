import sqlite3
from flask import Flask
from flask import abort, redirect, render_template, request, session
import config
import db
import recipes
import re
import users

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

@app.route("/")
def index():
    all_recipes = recipes.get_recipes()
    return render_template("index.html", recipes=all_recipes)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    user_recipes = users.get_recipes(user_id)
    return render_template("show_user.html", user=user, recipes=user_recipes)

@app.route("/find_recipe")
def find_recipe():
    query = request.args.get("query")
    if query:
        results = recipes.find_recipes(query)
    else:
        query = ""
        results = []
    return render_template("find_recipe.html", query=query, results=results)

@app.route("/recipe/<int:recipe_id>")
def show_recipe(recipe_id):
    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    classes = recipes.get_classes(recipe_id)
    return render_template("show_recipe.html", recipe=recipe, classes=classes)

@app.route("/new_recipe")
def new_recipe():
    require_login()
    classes = recipes.get_all_classes()
    return render_template("new_recipe.html", classes=classes)

@app.route("/create_recipe", methods=["POST"])
def create_recipe():
    require_login()

    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    description = request.form["description"]
    if not description or len(description) > 1000:
        abort(403)
    preparation_time = request.form["preparation_time"]
    if not re.search("^[1-9][0-9]{0,3}$", preparation_time):
        abort(403)
    user_id = session["user_id"]

    classes = []
    category = request.form.get("category")
    if category:
        classes.append(("Ruoan tyyppi", category))
    diets = request.form.getlist("diet")
    for diet in diets:
        classes.append(("Ruokavalio", diet))

    recipes.add_recipe(title, description, preparation_time, user_id, classes)

    return redirect("/")

@app.route("/edit_recipe/<int:recipe_id>")
def edit_recipe(recipe_id):
    require_login()
    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)

    all_classes = recipes.get_all_classes()

    classes = {}
    for class_name in all_classes:
        classes[class_name] = []

    for entry in recipes.get_classes(recipe_id):
        classes[entry["title"]].append(entry["value"])

    return render_template("edit_recipe.html", recipe=recipe, classes=classes, all_classes=all_classes)


@app.route("/update_recipe", methods=["POST"])
def update_recipe():
    require_login()
    recipe_id = request.form["recipe_id"]
    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)

    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    description = request.form["description"]
    if not description or len(description) > 1000:
        abort(403)
    preparation_time = request.form["preparation_time"]
    if not re.search("^[1-9][0-9]{0,3}$", preparation_time):
        abort(403)

    classes = []
    category = request.form.get("category")
    if category:
        classes.append(("Ruoan tyyppi", category))
    diets = request.form.getlist("diet")
    for diet in diets:
        classes.append(("Ruokavalio", diet))

    recipes.update_recipe(recipe_id, title, description, preparation_time, classes)

    return redirect("/recipe/" + str(recipe_id))

@app.route("/remove_recipe/<int:recipe_id>", methods=["GET", "POST"])
def remove_recipe(recipe_id):
    require_login()
    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)
    
    if request.method == "GET":
        return render_template("remove_recipe.html", recipe=recipe)

    if request.method == "POST":
        if "remove" in request.form:
            recipes.remove_recipe(recipe_id)
            return redirect("/")
        else:
            return redirect("/recipe/" + str(recipe_id))


@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"

    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")