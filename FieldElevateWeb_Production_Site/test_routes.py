import unittest
from main_app import app

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'FieldElevate', response.data)

    def test_admin_route(self):
        response = self.app.get('/admin')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Dashboard', response.data)

    def test_investor_route(self):
        response = self.app.get('/investor')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Investor Dashboard', response.data)

    def test_health_check(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'OK')

if __name__ == '__main__':
    unittest.main() 