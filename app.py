from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Database connection
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'rootSQL8',  
    'database': 'user_management'
}

# Create a MySQL connection
def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise

@app.route('/add-user', methods=['POST'])
def add_user():
    data = request.json
    full_name = data.get('fullName')
    username = data.get('username')

    if not full_name or not username:
        return jsonify({'error': 'Both full name and username are required'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (fullName, username) VALUES (%s, %s)', (full_name, username))
        conn.commit()
        user_id = cursor.lastrowid
    except Error as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to add user'}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'id': user_id, 'fullName': full_name, 'username': username})

@app.route('/users', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
    except Error as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to retrieve users'}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(users)

@app.route('/update-user', methods=['POST'])
def update_user():
    data = request.json
    user_id = data.get('id')
    full_name = data.get('fullName')
    username = data.get('username')

    if not user_id or not full_name or not username:
        return jsonify({'error': 'ID, full name, and username are required'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET fullName = %s, username = %s WHERE id = %s', (full_name, username, user_id))
        if cursor.rowcount == 0:
            return jsonify({'error': 'User not found'}), 404
        conn.commit()
    except Error as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to update user'}), 500
    finally:
        cursor.close()
        conn.close()

    return '', 204

@app.route('/delete-user', methods=['POST'])
def delete_user():
    data = request.json
    user_id = data.get('id')

    if not user_id:
        return jsonify({'error': 'ID is required'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        if cursor.rowcount == 0:
            return jsonify({'error': 'User not found'}), 404
        conn.commit()
    except Error as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to delete user'}), 500
    finally:
        cursor.close()
        conn.close()

    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
