import sqlite3

def validate_user(mobile, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE mobile = ? AND password = ?", (mobile, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def connect_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        name TEXT,
        mobile TEXT PRIMARY KEY,
        password TEXT,
        hint TEXT
    )''')
    conn.commit()
    conn.close()

def register_user(name, mobile, password, hint):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (name, mobile, password, hint))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(mobile, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE mobile=? AND password=?", (mobile, password))
    result = cursor.fetchone()
    conn.close()
    return result

def get_password_by_mobile(mobile):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE mobile=?", (mobile,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
