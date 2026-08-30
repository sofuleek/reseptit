import sqlite3
import secrets
from flask import Flask
from flask import abort, flash, redirect, render_template, request, session
import markupsafe
import config
import db
import recipes
import re
import users

app = Flask(__name__)
app.secret_key = config.secret_key

@app.before_request
def create_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if "csrf_token" not in session:
        abort(403)

    if "csrf_token" not in request.form:
        abort(403)

    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)


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
    return render_template("show_user.html", 
                           user=user, 
                           recipes=user_recipes
    )

@app.route("/find_recipe")
def find_recipe():
    query = request.args.get("query")
    if query:
        results = recipes.find_recipes(query)
    else:
        query = ""
        results = []
    return render_template("find_recipe.html", 
                           query=query, 
                           results=results
    )

@app.route("/recipe/<int:recipe_id>")
def show_recipe(recipe_id):
    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    classes = recipes.get_classes(recipe_id)
    comments = recipes.get_comments(recipe_id)
    average_grade = recipes.get_average_grade(recipe_id)
    return render_template("show_recipe.html", 
                           recipe=recipe, 
                           classes=classes, 
                           comments=comments, 
                           filled={}, 
                           average_grade=average_grade
    )

@app.route("/new_recipe")
def new_recipe():
    require_login()
    classes = recipes.get_all_classes()
    filled = {}

    return render_template("new_recipe.html", 
                           classes=classes, 
                           filled=filled
    )

@app.route("/create_comment", methods=["POST"])
def create_comment():
    require_login()
    check_csrf()

    recipe_id = request.form.get("recipe_id")
    grade = request.form["grade"]
    comment = request.form["comment"].strip()

    filled = {
        "grade": grade,
        "comment": comment
    }

    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)

    if not re.search("^(10|[1-9])$", grade):
        flash("VIRHE: arvosanan pitää olla 1-10")
        return render_template( "show_recipe.html", 
                                recipe=recipe, 
                                classes=recipes.get_classes(recipe_id), 
                                comments=recipes.get_comments(recipe_id), 
                                filled=filled 
        )

    if not comment:
        flash("VIRHE: kommentti ei voi olla tyhjä")
        return render_template( "show_recipe.html", 
                                recipe=recipe, 
                                classes=recipes.get_classes(recipe_id), 
                                comments=recipes.get_comments(recipe_id), 
                                filled=filled 
        )

    if len(comment) > 400:
        flash("VIRHE: kommentti ei voi olla yli 400 merkkiä pitkä")
        return render_template( "show_recipe.html", 
                                recipe=recipe, 
                                classes=recipes.get_classes(recipe_id), 
                                comments=recipes.get_comments(recipe_id), 
                                filled=filled 
        )

    user_id = session["user_id"]

    recipes.add_comment(recipe_id, user_id, comment, grade)

    return redirect("/recipe/" + str(recipe_id))

@app.route("/create_recipe", methods=["POST"])
def create_recipe():
    require_login()
    check_csrf()

    title = request.form["title"]
    description = request.form["description"]
    preparation_time = request.form["preparation_time"]

    filled = {
        "title": title,
        "description": description,
        "preparation_time": preparation_time
    }

    all_classes = recipes.get_all_classes()

    if not title:
        flash("VIRHE: otsikko ei voi olla tyhjä")
        return render_template("new_recipe.html", 
                               filled=filled, 
                               classes=all_classes
        )
    if len(title) > 50:
        flash("VIRHE: otsikko ei voi olla yli 50 merkkiä pitkä")
        return render_template("new_recipe.html", 
                               filled=filled, 
                               classes=all_classes
        )
    if not description:
        flash("VIRHE: kuvaus ei voi olla tyhjä")
        return render_template("new_recipe.html", 
                               filled=filled, 
                               classes=all_classes
        )
    if len(description) > 1000:
        flash("VIRHE: kuvaus ei voi olla yli 1000 merkkiä pitkä")
        return render_template("new_recipe.html", 
                               filled=filled, 
                               classes=all_classes
        )
    if not re.search("^[1-9][0-9]{0,2}$", preparation_time):
        flash("VIRHE: valmistusajan pitää olla 1-999 minuuttia")
        return render_template("new_recipe.html", 
                               filled=filled, 
                               classes=all_classes
        )
    user_id = session["user_id"]

    classes = []
    category = request.form.get("category")
    if category:
        if category not in all_classes["Ruoan tyyppi"]:
            flash("VIRHE: valittu ruoan tyyppi ei ole kelvollinen")
            return render_template("new_recipe.html", 
                                   filled=filled, 
                                   classes=all_classes
            )
        classes.append(("Ruoan tyyppi", category))

    diets = request.form.getlist("diet")
    for diet in diets:
        if diet not in all_classes["Ruokavalio"]:
            flash("VIRHE: valittu ruokavalio ei ole kelvollinen")
            return render_template("new_recipe.html", 
                                   filled=filled, 
                                   classes=all_classes
            )
        classes.append(("Ruokavalio", diet))

    recipe_id = recipes.add_recipe(title, description, preparation_time, user_id, classes)

    return redirect("/recipe/" + str(recipe_id))

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

    filled = {
        "title": recipe["title"],
        "description": recipe["description"],
        "preparation_time": recipe["preparation_time"]
    }

    return render_template("edit_recipe.html", 
                           recipe=recipe, 
                           classes=classes, 
                           all_classes=all_classes, 
                           filled=filled
    )


@app.route("/update_recipe", methods=["POST"])
def update_recipe():
    require_login()
    check_csrf()
    recipe_id = request.form["recipe_id"]
    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)

    title = request.form["title"]
    description = request.form["description"]
    preparation_time = request.form["preparation_time"]

    filled = { 
        "title": title,
        "description": description,
        "preparation_time": preparation_time
    }

    all_classes = recipes.get_all_classes()

    selected_classes = {
        "Ruoan tyyppi": [],
        "Ruokavalio": []
    }

    category = request.form.get("category")
    if category:
        selected_classes["Ruoan tyyppi"].append(category) 

    diets = request.form.getlist("diet") 
    for diet in diets:
        selected_classes["Ruokavalio"].append(diet)

    if not title:
        flash("VIRHE: otsikko ei voi olla tyhjä")
        return render_template("edit_recipe.html", 
                               recipe=recipe, 
                               filled=filled, 
                               classes=selected_classes, 
                               all_classes=all_classes
        )

    if len(title) > 50:
        flash("VIRHE: otsikko ei voi olla yli 50 merkkiä pitkä")
        return render_template("edit_recipe.html", 
                               recipe=recipe, 
                               filled=filled, 
                               classes=selected_classes, 
                               all_classes=all_classes
        )

    if not description:
        flash("VIRHE: kuvaus ei voi olla tyhjä")
        return render_template("edit_recipe.html", 
                               recipe=recipe, 
                               filled=filled, 
                               classes=selected_classes, 
                               all_classes=all_classes
        )

    if len(description) > 1000:
        flash("VIRHE: kuvaus ei voi olla yli 1000 merkkiä pitkä")
        return render_template("edit_recipe.html", 
                               recipe=recipe, 
                               filled=filled, 
                               classes=selected_classes, 
                               all_classes=all_classes
        )

    if not re.search("^[1-9][0-9]{0,2}$", preparation_time):
        flash("VIRHE: valmistusaika ei voi olla tyhjä ja sen pitää olla 1-999 minuuttia")
        return render_template("edit_recipe.html", 
                               recipe=recipe, 
                               filled=filled, 
                               classes=selected_classes, 
                               all_classes=all_classes
        )


    classes = []
    category = request.form.get("category")
    if category:
        if category not in all_classes["Ruoan tyyppi"]:
            flash("VIRHE: valittu ruoan tyyppi ei ole kelvollinen")
            return render_template("edit_recipe.html", 
                                   recipe=recipe, 
                                   filled=filled, 
                                   classes=selected_classes, 
                                   all_classes=all_classes
            )
        classes.append(("Ruoan tyyppi", category))

    diets = request.form.getlist("diet")
    for diet in diets:
        if diet not in all_classes["Ruokavalio"]:
            flash("VIRHE: valittu ruokavalio ei ole kelvollinen")
            return render_template("edit_recipe.html", 
                                   recipe=recipe, 
                                   filled=filled, 
                                   classes=selected_classes, 
                                   all_classes=all_classes
            )
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
        check_csrf()
        if "remove" in request.form:
            recipes.remove_recipe(recipe_id)
            return redirect("/")
        else:
            return redirect("/recipe/" + str(recipe_id))


@app.route("/register")
def register():
    return render_template("register.html", filled={})

@app.route("/create", methods=["POST"])
def create():
    check_csrf()
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    filled = { "username": username }

    if not username:
        flash("VIRHE: käyttäjänimi ei voi olla tyhjä")
        return render_template("register.html", filled=filled)

    if len(username) > 50:
        flash("VIRHE: käyttäjänimi ei voi olla yli 50 merkkiä pitkä")
        return render_template("register.html", filled=filled)

    if not password1:
        flash("VIRHE: salasana ei voi olla tyhjä")
        return render_template("register.html", filled=filled)

    if not password2:
        flash("VIRHE: kirjoita salasana uudestaan")
        return render_template("register.html", filled=filled)

    if password1 != password2:
        flash("VIRHE: salasanat eivät ole samat")
        return render_template("register.html", filled=filled)

    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        flash("VIRHE: tunnus on jo varattu")
        return render_template("register.html", filled=filled)

    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", next_page=request.referrer)

    if request.method == "POST":
        check_csrf()
        username = request.form["username"]
        password = request.form["password"]
        next_page = request.form["next_page"]

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            flash("VIRHE: väärä tunnus tai salasana")
            return render_template("login.html", next_page=next_page)

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")