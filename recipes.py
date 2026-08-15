import db

def add_recipe(title, description, preparation_time, user_id):
    sql = """INSERT INTO recipes (title, description, preparation_time, user_id)
            VALUES (?, ?, ?, ?)"""
    db.execute(sql, [title, description, preparation_time, user_id])

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

def update_recipe(recipe_id, title, description, preparation_time):
    sql = """UPDATE recipes SET title = ?,
                              description = ?,
                              preparation_time = ?
                          WHERE id = ?"""
    db.execute(sql, [title, description, preparation_time, recipe_id])

def remove_recipe(recipe_id):
    sql = "DELETE FROM recipes WHERE id = ?"
    db.execute(sql, [recipe_id])

def find_recipes(query):
    sql = """SELECT id, title
             FROM recipes
             WHERE title LIKE ? OR description LIKE ?
             ORDER BY id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like])