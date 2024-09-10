import sqlite3

with sqlite3.connect('date_base.db') as db:
    cursor = db.cursor()
    query = '''INSERT INTO expenses(id, id_tg_user) VALUES(1, 1022548979)'''
    cursor.execute(query)

