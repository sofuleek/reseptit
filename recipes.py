import db

def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}

    for title, value in result:
        if title not in classes:
            classes[title] = []
        classes[title].append(value)

    return classes

def add_recipe(title, description, preparation_time, user_id, classes):
    sql = """INSERT INTO recipes (title, description, preparation_time, user_id)
            VALUES (?, ?, ?, ?)"""
    db.execute(sql, [title, description, preparation_time, user_id])

    recipe_id = db.last_insert_id()

    sql = "INSERT INTO recipe_classes (recipe_id, title, value) VALUES (?, ?, ?)"
    for class_title, class_value in classes:
        db.execute(sql, [recipe_id, class_title, class_value])

    return recipe_id

def add_comment(recipe_id, user_id, comment, grade):
    sql = """INSERT INTO comments (recipe_id, user_id, comment, grade)
            VALUES (?, ?, ?, ?)"""
    db.execute(sql, [recipe_id, user_id, comment, grade])

def get_comments(recipe_id):
    sql = """SELECT comments.comment, comments.grade, users.id user_id, users.username
             FROM comments, users
             WHERE comments.recipe_id = ? AND comments.user_id = users.id
             ORDER BY comments.id DESC"""
    return db.query(sql, [recipe_id])

def get_classes(recipe_id):
    sql = "SELECT title, value FROM recipe_classes WHERE recipe_id = ?"
    return db.query(sql, [recipe_id])

def get_recipes():
    sql = """SELECT recipes.id, recipes.title, recipes.preparation_time, users.id user_id, users.username, AVG(comments.grade) average_grade
             FROM recipes JOIN users ON recipes.user_id = users.id
                          LEFT JOIN comments ON recipes.id = comments.recipe_id
             GROUP BY recipes.id
             ORDER BY recipes.id DESC"""
    return db.query(sql)

def get_recipe(recipe_id):
    sql = """SELECT recipes.id,
                    recipes.title,
                    recipes.description,
                    recipes.preparation_time,
                    users.id user_id,
                    users.username
             FROM recipes, users
             WHERE recipes.user_id = users.id AND
                   recipes.id = ?"""
    result = db.query(sql, [recipe_id])
    return result[0] if result else None

def update_recipe(recipe_id, title, description, preparation_time, classes):
    sql = """UPDATE recipes SET title = ?,
                              description = ?,
                              preparation_time = ?
                          WHERE id = ?"""
    db.execute(sql, [title, description, preparation_time, recipe_id])

    sql = "DELETE FROM recipe_classes WHERE recipe_id = ?"
    db.execute(sql, [recipe_id])

    sql = "INSERT INTO recipe_classes (recipe_id, title, value) VALUES (?, ?, ?)"
    for class_title, class_value in classes:
        db.execute(sql, [recipe_id, class_title, class_value])

def remove_recipe(recipe_id):
    sql = "DELETE FROM recipe_classes WHERE recipe_id = ?"
    db.execute(sql, [recipe_id])

    sql = "DELETE FROM comments WHERE recipe_id = ?"
    db.execute(sql, [recipe_id])

    sql = "DELETE FROM recipes WHERE id = ?"
    db.execute(sql, [recipe_id])

def find_recipes(query):
    sql = """SELECT DISTINCT recipes.id, recipes.title
             FROM recipes
             LEFT JOIN recipe_classes ON recipes.id = recipe_classes.recipe_id
             WHERE recipes.title LIKE ? OR recipes.description LIKE ? OR recipe_classes.value LIKE ?
             ORDER BY recipes.id DESC"""

    like = "%" + query + "%"

    return db.query(sql, [like, like, like])

def get_average_grade(recipe_id):
    sql = """SELECT AVG(grade)
             FROM comments
             WHERE recipe_id = ?"""
    result = db.query(sql, [recipe_id])

    return result[0][0]