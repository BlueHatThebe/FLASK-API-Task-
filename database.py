import sqlite3

def initialize_database():
    connection = sqlite3.connect('test_database.db')  # Use the same name as DATABASE in app.py
    cursor = connection.cursor()
    
    # Create the `users` table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullName TEXT NOT NULL,
        username TEXT NOT NULL UNIQUE
    )
    ''')
    
    connection.commit()
    connection.close()

if __name__ == '__main__':
    initialize_database()
