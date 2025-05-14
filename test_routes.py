import unittest
from app import app, menu_items # assure flask app is created in app.py
from flask import request

class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        # sets up a test client
        self.app = app.test_client()
        self.app.testing = True

    def test_home_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_seed_menu_items(self):
        category = request.args.get('category')
        allCategories = menu_items.query.filter_by(category=category).all()
        assert len(allCategories) == 7
        assert 'Sandwiches' in allCategories and 'Platters' in allCategories and 'Breakfast' in allCategories and 'Salads' in allCategories and 'Short Order' in allCategories and 'Small Plates' in allCategories and 'Soups' in allCategories


if __name__== '__main__':
    unittest.main() 