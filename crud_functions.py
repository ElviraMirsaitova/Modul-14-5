import sqlite3

connection = sqlite3.connect("database.db")
cursor = connection.cursor()




def initiate_db():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    price INTEGER NOT NULL)''')
    cursor.execute('DELETE FROM Products')
    for i in range(1,5):
        cursor.execute("INSERT INTO Products (title, description, price) VALUES (?, ?, ?)",
                       (f'Продукт {i}', f'Combi {i}', i))

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users(
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    age INTEGER NOT NULL,
    balance INTEGER NOT NULL
    )
    ''')

    cursor.execute(" CREATE INDEX IF NOT EXISTS idx_email ON Users (email)")

    connection.commit()
    connection.close()

initiate_db()

def get_all_products():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute(" SELECT id, title, description, price FROM Products")
    products_db = cursor.fetchall()
    connection.commit()
    connection.close()
    return list(products_db)

def add_user(username, email, age):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, ?)",
                   (f'{username}', '{email}', '{age}', 1000))
    connection.commit()

def is_included(username):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    check_user = cursor.execute("SELECT username FROM Users WHERE username = ?", (username,))
    if check_user.fetchone() is None:
        return False
    else:
        return True
    connection.commit()
