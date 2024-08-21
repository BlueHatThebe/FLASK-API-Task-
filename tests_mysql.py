import unittest
import json
from app import app, get_db_connection, create_schema

class UserManagementTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Create and initialize the in-memory database schema
        with self.app.application.app_context():
            conn = get_db_connection()
            create_schema(conn)
            conn.close()

    def _add_test_user(self, full_name='Test User', username='testuser'):
        response = self.app.post('/add-user',
                                 data=json.dumps({'fullName': full_name, 'username': username}),
                                 content_type='application/json')
        return response  # Return the response object

    def test_add_user(self):
        response = self._add_test_user('John Doe', 'johndoe')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)
        self.assertEqual(data['fullName'], 'John Doe')
        self.assertEqual(data['username'], 'johndoe')

    def test_get_users(self):
        # Adding a user first
        user_data = self._add_test_user('Jane Doe', 'janedoe')
        user_id = json.loads(user_data.data)['id']

        # Query by full name
        response = self.app.get('/users', query_string={'fullName': 'Jane Doe'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 0)  # Check that some users are returned
        self.assertTrue(any(user['fullName'] == 'Jane Doe' and user['username'] == 'janedoe' for user in data))

        # Query by user ID
        response = self.app.get(f'/users?id={user_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['fullName'], 'Jane Doe')
        self.assertEqual(data[0]['username'], 'janedoe')

    def test_update_user(self):
        # Adding a user first
        user_data = self._add_test_user('Jane Doe', 'janedoe')
        user_id = json.loads(user_data.data)['id']
        response = self.app.put(f'/update-user/{user_id}',
                                data=json.dumps({'fullName': 'Jane Smith', 'username': 'janesmith'}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 204)

        # Verify update
        response = self.app.get(f'/users?id={user_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['fullName'], 'Jane Smith')
        self.assertEqual(data[0]['username'], 'janesmith')

    def test_delete_user(self):
        # Adding a user first
        user_data = self._add_test_user('Jane Doe', 'janedoe')
        user_id = json.loads(user_data.data)['id']
        response = self.app.delete(f'/delete-user?id={user_id}')
        self.assertEqual(response.status_code, 204)

        # Verify deletion
        response = self.app.get(f'/users?id={user_id}')
        self.assertEqual(response.status_code, 404)

    def test_add_user_missing_data(self):
        response = self.app.post('/add-user',
                                 data=json.dumps({'fullName': 'John Doe'}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Both full name and username are required')

    def test_update_user_not_found(self):
        response = self.app.put('/update-user/999',
                                data=json.dumps({'fullName': 'Jane Smith', 'username': 'janesmith'}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'User not found')

    def test_delete_user_not_found(self):
        response = self.app.delete('/delete-user?id=999')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data, {'status': 'User not found'})

if __name__ == '__main__':
    unittest.main()
