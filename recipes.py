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

def get_classes(recipe_id):
    sql = "SELECT title, value FROM recipe_classes WHERE recipe_id = ?"
    return db.query(sql, [recipe_id])

def get_recipes():
    sql = "SELECT id, title FROM recipes ORDER BY id DESC"
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

    sql = "DELETE FROM recipes WHERE id = ?"
    db.execute(sql, [recipe_id])

def find_recipes(query):
    sql = """SELECT id, title
             FROM recipes
             WHERE title LIKE ? OR description LIKE ?
             ORDER BY id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like])