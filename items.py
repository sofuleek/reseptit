import db

def add_item(title, description, preparation_time, user_id):
    sql = """INSERT INTO items (title, description, preparation_time, user_id)
            VALUES (?, ?, ?, ?)"""
    db.execute(sql, [title, description, preparation_time, user_id])