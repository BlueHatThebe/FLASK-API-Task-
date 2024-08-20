import os
import sqlite3
import mysql.connector
from flask import Flask, request, jsonify
from mysql.connector import Error
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

def get_db_connection():
    if os.getenv('TESTING'):
        return sqlite3.connect(':memory:')
    else:
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='rootSQL8',
            database='user_management'
        )

def create_schema(conn):
    cursor = conn.cursor()
    if os.getenv('TESTING'):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fullName TEXT NOT NULL,
                username TEXT NOT NULL
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fullName VARCHAR(255),
                username VARCHAR(255)
            )
        ''')
    conn.commit()
    cursor.close()

def initialize_db():
    conn = get_db_connection()
    create_schema(conn)
    conn.close()

@app.route('/add-user', methods=['POST'])
def add_user():
    data = request.json
    full_name = data.get('fullName')
    username = data.get('username')

    if not full_name or not username:
        return jsonify({'error': 'Both full name and username are required'}), 400

    try:
        conn = get_db_connection()
        create_schema(conn)  # Ensure schema is created for each connection
        cursor = conn.cursor()
        if os.getenv('TESTING'):
            cursor.execute('INSERT INTO users (fullName, username) VALUES (?, ?)', (full_name, username))
        else:
            cursor.execute('INSERT INTO users (fullName, username) VALUES (%s, %s)', (full_name, username))
        conn.commit()
        user_id = cursor.lastrowid
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'id': user_id, 'fullName': full_name, 'username': username}), 201

@app.route('/users', methods=['GET'])
def get_users():
    user_id = request.args.get('id')
    full_name = request.args.get('fullName')
    username = request.args.get('username')

    query = 'SELECT * FROM users WHERE 1=1'
    params = []

    if user_id:
        query += ' AND id = ?' if os.getenv('TESTING') else ' AND id = %s'
        params.append(user_id)
    if full_name:
        query += ' AND fullName LIKE ?' if os.getenv('TESTING') else ' AND fullName LIKE %s'
        params.append(f'%{full_name}%')
    if username:
        query += ' AND username LIKE ?' if os.getenv('TESTING') else ' AND username LIKE %s'
        params.append(f'%{username}%')

    try:
        conn = get_db_connection()
        create_schema(conn)  # Ensure schema is created for each connection
        cursor = conn.cursor(dictionary=True) if not os.getenv('TESTING') else conn.cursor()
        cursor.execute(query, params)
        users = cursor.fetchall()

        if not users:
            return jsonify([]), 404
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(users)

@app.route('/update-user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    new_full_name = data.get('fullName')
    new_username = data.get('username')

    if not new_full_name or not new_username:
        return jsonify({'error': 'Both new full name and new username are required'}), 400

    try:
        conn = get_db_connection()
        create_schema(conn)  # Ensure schema is created for each connection
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET fullName = ?, username = ? WHERE id = ?' if os.getenv('TESTING')
            else 'UPDATE users SET fullName = %s, username = %s WHERE id = %s',
            (new_full_name, new_username, user_id)
        )
        if cursor.rowcount == 0:
            return jsonify({'error': 'User not found'}), 404
        conn.commit()
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return '', 204

@app.route('/delete-user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        conn = get_db_connection()
        create_schema(conn)  # Ensure schema is created for each connection
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM users WHERE id = ?' if os.getenv('TESTING')
            else 'DELETE FROM users WHERE id = %s',
            (user_id,)
        )
        if cursor.rowcount == 0:
            return jsonify({'status': 'User not found'}), 404
        conn.commit()
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return '', 204

if __name__ == '__main__':
    initialize_db()
    app.run(debug=True)
