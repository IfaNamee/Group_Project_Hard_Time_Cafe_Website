import unittest
from app import app # assure flask app is created in app.py

class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        # sets up a test client
        self.app = app.test_client()
        self.app.testing = True

        def test_home_route(self):
            response = self.app.get('/')
            self.assertEqual(response.status_code, 200)

if __name__== '__main__':
    unittest.main() 