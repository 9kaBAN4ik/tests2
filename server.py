import sqlite3

# Подключаемся к базе данных
conn = sqlite3.connect('data/database.db')
cursor = conn.cursor()

# Создаём таблицу lottery с указанными столбцами
cursor.execute('''
    CREATE TABLE IF NOT EXISTS lottery (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        ticket_price INTEGER NOT NULL DEFAULT 0,
        fund INTEGER NOT NULL CHECK(fund >= 0),
        referral_fund INTEGER NOT NULL DEFAULT 0,
        active INTEGER NOT NULL DEFAULT 0
    )
''')

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()
