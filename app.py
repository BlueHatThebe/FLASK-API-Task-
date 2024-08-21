import os
import sqlite3
import mysql.connector
from flask import Flask, request, jsonify, send_from_directory
from mysql.connector import Error
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

def get_db_connection():
    if os.getenv('TESTING'):
        return sqlite3.connect('sqlite.db')
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

@app.route("/", defaults={"filename":""})
@app.route("/<path:filename>")
def home(filename):
    if not filename:
        filename = "index.html"
    return send_from_directory(os.getcwd(), filename), 200

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
        query = 'INSERT INTO users (fullName, username) VALUES (%s, %s)' if not os.getenv('TESTING') else 'INSERT INTO users (fullName, username) VALUES (?, ?)'
        cursor.execute(query, (full_name, username))
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
    try:
        conn = get_db_connection()
        create_schema(conn)  # Ensure schema is created for each connection
        cursor = conn.cursor(dictionary=True) if not os.getenv('TESTING') else conn.cursor()
        full_name = request.args.get('fullName')
        user_id = request.args.get('id')

        if full_name:
            query = 'SELECT * FROM users WHERE fullName = %s' if not os.getenv('TESTING') else 'SELECT * FROM users WHERE fullName = ?'
            cursor.execute(query, (full_name,))
        elif user_id:
            query = 'SELECT * FROM users WHERE id = %s' if not os.getenv('TESTING') else 'SELECT * FROM users WHERE id = ?'
            cursor.execute(query, (user_id,))
        else:
            query = 'SELECT * FROM users'
            cursor.execute(query)
        
        users = cursor.fetchall()
        if not users:
            return jsonify([]), 404
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(users)

@app.route('/update-user-by-username', methods=['PUT'])
def update_user_by_username():
    old_username = request.args.get('oldUsername')
    data = request.json
    new_full_name = data.get('fullName')
    new_username = data.get('username')

    if not old_username or not new_full_name or not new_username:
        return jsonify({'error': 'Old username, new full name, and new username are required'}), 400

    try:
        conn = get_db_connection()
        create_schema(conn)  # Ensure schema is created for each connection
        cursor = conn.cursor()

        query = '''
            UPDATE users
            SET fullName = %s, username = %s
            WHERE username = %s
        ''' if not os.getenv('TESTING') else '''
            UPDATE users
            SET fullName = ?, username = ?
            WHERE username = ?
        '''
        cursor.execute(query, (new_full_name, new_username, old_username))
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'User with the old username not found'}), 404

        conn.commit()
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return '', 204

@app.route('/update-user/<int:user_id>', methods=['PUT'])
def update_user_by_id(user_id):
    data = request.json
    new_full_name = data.get('fullName')
    new_username = data.get('username')

    if not new_full_name or not new_username:
        return jsonify({'error': 'Both new full name and new username are required'}), 400

    try:
        conn = get_db_connection()
        create_schema(conn)  # Ensure schema is created for each connection
        cursor = conn.cursor()

        query = '''
            UPDATE users
            SET fullName = %s, username = %s
            WHERE id = %s
        ''' if not os.getenv('TESTING') else '''
            UPDATE users
            SET fullName = ?, username = ?
            WHERE id = ?
        '''
        cursor.execute(query, (new_full_name, new_username, user_id))
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'User not found'}), 404

        conn.commit()
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return '', 204

@app.route('/delete-user', methods=['DELETE'])
def delete_user():
    user_id = request.args.get('id')
    username = request.args.get('username')

    if not user_id and not username:
        return jsonify({'error': 'Either user ID or username is required'}), 400

    try:
        conn = get_db_connection()
        create_schema(conn)  # Ensure schema is created for each connection
        cursor = conn.cursor()
        if user_id:
            query = 'DELETE FROM users WHERE id = %s' if not os.getenv('TESTING') else 'DELETE FROM users WHERE id = ?'
            cursor.execute(query, (user_id,))
        elif username:
            query = 'DELETE FROM users WHERE username = %s' if not os.getenv('TESTING') else 'DELETE FROM users WHERE username = ?'
            cursor.execute(query, (username,))
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
