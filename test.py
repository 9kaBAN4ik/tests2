import sqlite3
from config import DB_PATH

def clear_partners_table():
    try:
        conn = sqlite3.connect(DB_PATH)
        print(f"Connected to database: {DB_PATH}")
        cursor = conn.cursor()

        # Удаляем все записи из таблицы partners
        cursor.execute("DELETE FROM partners;")
        print("Records deleted from partners table.")

        # Сбрасываем автоинкремент (если используется)
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='partners';")
        print("Auto-increment reset.")

        conn.commit()
        print("Changes committed.")
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()
        print("Connection closed.")

clear_partners_table()