import sqlite3


class UserDatabase:
    def __init__(self, db_name='tg_auth.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id_user INTEGER NOT NULL,
            tg_login VARCHAR NOT NULL
        )
        ''')
        self.conn.commit()

    def add_user(self, tg_id_user, tg_login):
        self.cursor.execute('''
        INSERT INTO users (tg_id_user, tg_login) VALUES (?, ?)
        ''', (tg_id_user, tg_login))
        self.conn.commit()

    def delete_user(self, id_user):
        self.cursor.execute('''
        DELETE FROM users WHERE id = ?
        ''', (id_user,))
        self.conn.commit()

    def update_user(self, id_user, tg_id_user=None, tg_login=None):
        if tg_id_user is not None:
            self.cursor.execute('''
            UPDATE users SET name = ? WHERE id = ?
            ''', (tg_id_user, id_user))

        if tg_login is not None:
            self.cursor.execute('''
            UPDATE users SET age = ? WHERE id = ?
            ''', (tg_login, id_user))

        self.conn.commit()

    def get_user(self, id_user):
        self.cursor.execute('''
        SELECT * FROM users WHERE id = ?
        ''', (id_user,))
        return self.cursor.fetchone()

    def get_all_users(self):
        self.cursor.execute('SELECT * FROM users')
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()


# Пример использования класса
if __name__ == '__main__':
    db = UserDatabase()

    db.create_table()
