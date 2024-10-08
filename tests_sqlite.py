import unittest
import json
import os
from app import app, get_db_connection, create_schema

class UserManagementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()
        cls.app.testing = True
        cls.conn = get_db_connection()
        create_schema(cls.conn)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def setUp(self):
        self.conn = get_db_connection()
        create_schema(self.conn)
        self.cursor = self.conn.cursor()
        # Clear users table before each test
        if not os.getenv('TESTING'):
            self.cursor.execute('DELETE FROM users')
            self.conn.commit()

    def tearDown(self):
        self.cursor.close()
        self.conn.close()

    def test_add_user(self):
        response = self.app.post('/add-user', json={'fullName': 'John Doe', 'username': 'jdoe'})
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)  # Ensure 'id' is present in the response
        self.assertEqual(data['fullName'], 'John Doe')
        self.assertEqual(data['username'], 'jdoe')

    def test_get_users(self):
        # Add a user to the database
        self.app.post('/add-user', json={'fullName': 'Jane Doe', 'username': 'janedoe'})
        response = self.app.get('/users', query_string={'fullName': 'Jane Doe'})
        self.assertEqual(response.status_code, 200)
        users = json.loads(response.data)
        self.assertEqual(len(users), 1)  # Ensure only 1 user is returned

    def test_update_user(self):
        # Add a user first
        user_response = self.app.post('/add-user', json={'fullName': 'Jane Doe', 'username': 'janedoe'})
        self.assertEqual(user_response.status_code, 201)
        user_data = json.loads(user_response.data)
        user_id = user_data['id']

        # Update the user
        response = self.app.put('/update-user', query_string={'id': user_id, 'oldName': 'Jane Doe'}, json={'fullName': 'Jane Smith', 'username': 'janesmith'})
        self.assertEqual(response.status_code, 204)

        # Verify the user was updated
        response = self.app.get('/users', query_string={'id': user_id})
        self.assertEqual(response.status_code, 200)
        users = json.loads(response.data)
        self.assertEqual(len(users), 1)  # Ensure only 1 user is returned
        updated_user = users[0]  # Get the first (and only) user
        self.assertEqual(updated_user['fullName'], 'Jane Smith')
        self.assertEqual(updated_user['username'], 'janesmith')

    def test_delete_user(self):
        # Add a user first
        user_response = self.app.post('/add-user', json={'fullName': 'John Doe', 'username': 'jdoe'})
        self.assertEqual(user_response.status_code, 201)
        user_data = json.loads(user_response.data)
        user_id = user_data['id']

        # Delete the user
        response = self.app.delete('/delete-user', query_string={'id': user_id})
        self.assertEqual(response.status_code, 204)

        # Verify the user was deleted
        response = self.app.get('/users', query_string={'id': user_id})
        self.assertEqual(response.status_code, 404)  # Should return 404 if user was deleted

    def test_delete_user_by_username(self):
        # Add a user first
        user_response = self.app.post('/add-user', json={'fullName': 'Jane Doe', 'username': 'janedoe'})
        self.assertEqual(user_response.status_code, 201)

        # Delete the user by username
        response = self.app.delete('/delete-user', query_string={'username': 'janedoe'})
        self.assertEqual(response.status_code, 204)

        # Verify the user was deleted
        response = self.app.get('/users', query_string={'username': 'janedoe'})
        self.assertEqual(response.status_code, 404)  # Should return 404 if user was deleted

if __name__ == '__main__':
    unittest.main()
