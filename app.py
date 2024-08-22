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
        if 'cursor' in locals():
            cursor.close()
        conn.close()

    return jsonify({'id': user_id, 'fullName': full_name, 'username': username}), 201

@app.route('/users', methods=['GET'])
def get_users():
    # Retrieve query parameters
    user_id = request.args.get('id')
    full_name = request.args.get('fullName')
    username = request.args.get('username')

    # Base query
    query = 'SELECT * FROM users'
    params = []
    placeholders = '%s'  # Default placeholder for MySQL

    if os.getenv('TESTING'):
        placeholders = '?'  # Placeholder for SQLite

    # Build the WHERE clause based on provided parameters
    conditions = []
    if user_id:
        conditions.append(f'id = {placeholders}')
        params.append(user_id)
    if full_name:
        conditions.append(f'fullName = {placeholders}')
        params.append(full_name)
    if username:
        conditions.append(f'username = {placeholders}')
        params.append(username)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    cursor = None
    try:
        conn = get_db_connection()
        create_schema(conn)  # Ensure schema is created for each connection

        if os.getenv('TESTING'):
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            users = [{'id': row[0], 'fullName': row[1], 'username': row[2]} for row in rows]
        else:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            users = cursor.fetchall()

        if not users:
            return jsonify([]), 404
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()

    return jsonify(users)  # Return the list of user objects as JSON

@app.route('/update-user', methods=['PUT'])
def update_user():
    # Retrieve parameters
    user_id = request.args.get('id')
    old_name = request.args.get('oldName')
    data = request.json
    new_full_name = data.get('fullName')
    new_username = data.get('username')

    if not new_full_name or not new_username:
        return jsonify({'error': 'New full name and new username are required'}), 400

    if not user_id and not old_name:
        return jsonify({'error': 'Either user ID or old name is required'}), 400

    try:
        conn = get_db_connection()
        create_schema(conn)  # Ensure schema is created for each connection
        cursor = conn.cursor()

        # Use correct placeholder based on database type
        if os.getenv('TESTING'):
            query = '''
                UPDATE users
                SET fullName = ?, username = ?
                WHERE id = ? OR fullName = ?
            '''
            params = (new_full_name, new_username, user_id, old_name)
        else:
            query = '''
                UPDATE users
                SET fullName = %s, username = %s
                WHERE id = %s OR fullName = %s
            '''
            params = (new_full_name, new_username, user_id, old_name)

        cursor.execute(query, params)

        # Check if the update was successful
        if cursor.rowcount == 0:
            return jsonify({'error': 'User not found or no changes made'}), 404

        conn.commit()
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()

    return '', 204  # No content to return

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
        if cursor is not None:
            cursor.close()
        conn.close()

    return '', 204

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    initialize_db()
    app.run(debug=True)
