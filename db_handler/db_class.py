import sqlite3


class UserDatabase:
    def __init__(self, db_name='C:/Users/dlancov/PycharmProjects/Bot_tg_twitch/db_handler/tg_auth.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_table(self, name_new_table, column):
        try:
            self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {name_new_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {column}
            )
            ''')
            self.conn.commit()
            print(f"Таблица {name_new_table} успешно создана.")
        except sqlite3.Error as e:
            print(f"Ошибка при создании таблицы: {e}")

    def full_request(self, request):
        self.cursor.execute(str(request))
        self.conn.commit()

    def add_record(self, tg_id_user, tg_login, table_name):
        try:
            self.cursor.execute(f'''
                    INSERT INTO {table_name} (tg_id_user, tg_login) VALUES (?, ?)
                    ''', (tg_id_user, tg_login))
            self.conn.commit()
        except sqlite3.IntegrityError:
            return False

    def delete_user(self,name_table, id_user):
        self.cursor.execute(f'''
        DELETE FROM {name_table}  WHERE tg_id_user = {id_user}
        ''')
        self.conn.commit()

    def delete_streamer(self, name_streamer, tg_id_user):
        # Приводим к нижнему регистру и проверяем тип входных данных
        if isinstance(name_streamer, (list, set)):
            name_streamer = [ns.lower() for ns in name_streamer]
        else:
            name_streamer = [name_streamer.lower()]

        try:
            # Создаем плейсхолдеры для SQL-запроса
            placeholders = ', '.join(['?'] * len(name_streamer))
            query = f'''
            DELETE FROM notif_stream WHERE name_streamer IN ({placeholders}) AND tg_id_user = ?
            '''

            # Выполняем запрос с параметрами
            self.cursor.execute(query, (*name_streamer, tg_id_user))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при удалении стримера: {e}")
            return False

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

    def get_streamers(self, id_user):
        self.cursor.execute('''
        SELECT * FROM notif_stream WHERE tg_id_user = ?
        ''', (id_user,))
        return self.cursor.fetchone()

    def get_name_streamers(self, id_user):
        self.cursor.execute('''
        SELECT name_streamer FROM notif_stream WHERE tg_id_user = ?
        ''', (id_user,))
        return self.cursor.fetchall()

    def get_id_tg_for_notif_distinct(self):
        self.cursor.execute('''
        SELECT DISTINCT tg_id_user FROM notif_stream;

        ''')
        return self.cursor.fetchall()

    def get_data_for_notif(self):
        self.cursor.execute('''
        SELECT tg_id_user, name_streamer FROM notif_stream
        ''')
        return self.cursor.fetchall()

    def get_all(self, table_name):
        self.cursor.execute(f'SELECT * FROM {table_name}')
        return self.cursor.fetchall()

    def drop_table(self, table_name):
        try:
            self.cursor.execute(f'''
            DROP TABLE IF EXISTS {table_name};
            ''')
            self.conn.commit()
            print(f"Таблица {table_name} успешно удалена.")
        except sqlite3.Error as e:
            print(f"Ошибка при удалении таблицы: {e}")

    def close(self):
        self.conn.close()

    def add_permission(self, tg_id_user):
        try:
            self.cursor.execute('''
            SELECT tg_id_user, tg_login FROM request_permission WHERE tg_id_user = ?
            ''', (tg_id_user,))
            user = self.cursor.fetchone()
            if user is None:
                return False
            tg_id_user, tg_login = user
            self.cursor.execute('''
            INSERT INTO users (tg_id_user, tg_login) VALUES (?, ?)
            ''', (tg_id_user, tg_login))
            self.cursor.execute('''
            DELETE FROM request_permission WHERE tg_id_user = ?
            ''', (tg_id_user,))
            self.conn.commit()
            print("Пользователь добавлен!")
            return True
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return False

    def add_streamer_for_notif(self, tg_id_user, name_streamer):
        name_streamer = name_streamer.lower()
        sql = '''INSERT INTO notif_stream (tg_id_user, name_streamer) 
                 VALUES (?, ?)'''
        try:
            self.cursor.execute(sql, (tg_id_user, name_streamer))
            self.conn.commit()
            print("Запись добавлена успешно.")
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении записи: {e}")
            return False

    def ban_user(self, tg_id_user):
        try:
            self.cursor.execute('''
            SELECT tg_id_user, tg_login FROM request_permission WHERE tg_id_user = ?
            ''', (tg_id_user,))
            user = self.cursor.fetchone()
            if user is None:
                return False
            tg_id_user, tg_login = user
            self.cursor.execute('''
            INSERT INTO user_ban_list (tg_id_user, tg_login) VALUES (?, ?)
            ''', (tg_id_user, tg_login))
            self.cursor.execute('''
            DELETE FROM request_permission WHERE tg_id_user = ?
            ''', (tg_id_user,))
            self.conn.commit()
            print("Пользователь заблокирован!")
            return True
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return False


if __name__ == '__main__':
    db = UserDatabase()

    while True:
        command = input("Введите команду (add, delete, update, get, get_all, \n"
                        "exit, create_table, drop_table, add_permission\n"
                        "get_streamers, add_for_notif, full_request, get_name_streamer, \n"
                        "get_data_for_notif, delete_streamer, delete_streamer,\n"
                        "get_id_tg_for_notif_distinct, ban_user): ")

        if command == 'add':
            table_name = input("Введите название таблицы: ")
            tg_id_user = int(input("Введите tg_id_user: "))
            tg_login = input("Введите tg_login: ")
            check = db.add_record(tg_id_user, tg_login, table_name)
            if check is True:
                print("Пользователь добавлен.")
            else:
                print("Ошибка: Такой пользователь уже есть.")

        elif command == 'delete':
            name_table = str(input("Введите имя таблицы: "))
            id_user = int(input("Введите id пользователя для удаления: "))
            db.delete_user(name_table, id_user)
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
            table_name = input('Введите название таблицы: ')
            users = db.get_all(table_name)
            for user in users:
                print(user)

        elif command == 'exit':
            db.close()
            break

        elif command == 'create_table':
            name_table = str(input("Введите название новой таблицы: "))
            quantity_column = int(input("Введите количество столбцов: "))
            columns_list = []
            for i in range(quantity_column):
                name_new_table = str(input(f"Введите название столбца {i + 1}: "))
                type_data = str(input("Введите тип данных для столбца: "))
                columns_list.append(f"{name_new_table} {type_data} NOT NULL UNIQUE")
            columns = ', '.join(columns_list)
            print(f"Создание таблицы с запросом: CREATE TABLE IF NOT EXISTS {name_table}"
                  f" (id INTEGER PRIMARY KEY AUTOINCREMENT, {columns})")
            db.create_table(name_table, columns)

        elif command == 'drop_table':
            table_name = input("Введите имя таблицы для удаления: ")
            db.drop_table(table_name)

        elif command == 'add_permission':
            id_record = int(input("Введите tg_id_user записи таблицы request_permission: "))
            db.add_permission(id_record)

        elif command == "full_request":
            request = input('Введите запрос: ')
            print(db.full_request(request))

        elif command == "add_for_notif":
            tg_id_user = int(input("Введите tg_id_user: "))
            name_streamer = (input("Введите name_streamer: "))
            db.add_streamer_for_notif(tg_id_user, name_streamer)

        elif command == "get_streamers":
            tg_id_user = input("Введите id_tg_user (или all для вывода всех): ")
            print(db.get_streamers(tg_id_user))

        elif command == "get_name_streamer":
            tg_id_user = input("Введите id_tg_user: ")
            print(db.get_name_streamers(tg_id_user))

        elif command == 'get_data_for_notif':
            print(db.get_data_for_notif())

        elif command == 'delete_streamer':
            name = (str(input("Введите name_streamer: ")))
            id = (int(input("Введите id юсера: ")))
            print(db.delete_streamer(name, id))

        elif command == 'get_id_tg_for_notif_distinct':
            print(db.get_id_tg_for_notif_distinct())

        elif command == 'ban_user':
            tg_id_user = int(input("Введите id_tg_user для переноса в бан лист: "))
            print(db.ban_user(tg_id_user))
        else:
            print("Неверная команда. Пожалуйста, попробуйте снова.")
