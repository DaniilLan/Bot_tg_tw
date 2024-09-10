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
            UPDATE users SET tg_id_user = ? WHERE id = ?
            ''', (tg_id_user, id_user))

        if tg_login is not None:
            self.cursor.execute('''
            UPDATE users SET tg_login = ? WHERE id = ?
            ''', (tg_login, id_user))

        self.conn.commit()

    def get_user(self, id_user):
        self.cursor.execute('''
        SELECT * FROM users WHERE tg_id_user = ?
        ''', (id_user,))
        return self.cursor.fetchone()

    def get_all_users(self):
        self.cursor.execute('SELECT * FROM users')
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()


if __name__ == '__main__':
    db = UserDatabase()

    while True:
        command = input("Введите команду (add, delete, update, get, get_all, exit): ")

        if command == 'add':
            tg_id_user = int(input("Введите tg_id_user: "))
            tg_login = input("Введите tg_login: ")
            db.add_user(tg_id_user, tg_login)
            print("Пользователь добавлен.")

        elif command == 'delete':
            id_user = int(input("Введите id пользователя для удаления: "))
            db.delete_user(id_user)
            print("Пользователь удален.")

        elif command == 'update':
            id_user = int(input("Введите id пользователя для обновления: "))
            tg_id_user = input("Введите новый tg_id_user (или оставьте пустым для пропуска): ")
            tg_login = input("Введите новый tg_login (или оставьте пустым для пропуска): ")
            db.update_user(id_user,
                           int(tg_id_user) if tg_id_user else None,
                           tg_login if tg_login else None)
            print("Пользователь обновлен.")

        elif command == 'get':
            id_user = int(input("Введите id пользователя для получения: "))
            user = db.get_user(id_user)
            print(user)

        elif command == 'get_all':
            users = db.get_all_users()
            for user in users:
                print(user)

        elif command == 'exit':
            db.close()
            break

        else:
            print("Неверная команда. Пожалуйста, попробуйте снова.")
