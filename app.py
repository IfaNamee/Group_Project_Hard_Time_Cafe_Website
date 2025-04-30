# Import necessary modules from Flask and SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Initialize the Flask application
app = Flask(__name__)

# --- Database Configuration ---

# Set up the database URI for SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comments.db'

# Disable modification tracking to save resources
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the Flask app
db = SQLAlchemy(app)

# --- Define Database Model ---

# Create a Comment model representing each comment entry in the database
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each comment
    text = db.Column(db.Text, nullable=False)     # Comment text (required)

class menu_items(db.Model):
    menuId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100))
    price = db.Column(db.Float)
    denotations = db.column(db.String(100))
    category = db.column(db.String(100))
    

class orders(db.Model):
    orderId = db.Column(db.Integer, primary_key=True)
    orderDate = db.Column(db.DateTime, default=datetime.utcnow)
    totalPrice = db.column(db.Float)
    
    
class orderDetails(db.Model):
    detailId = db.Column(db.Integer, primary_key=True)
    
    itemId = db.column(db.Integer, db.ForeignKey('menu_items.menuId'))
    item = db.relationship('menu_items', backref='menu_items', lazy=True)
    
    specialOrderId = db.column(db.Integer, db.ForeignKey('orders.orderId'))
    special = db.relationship('orders', backref='orders', lazy=True)
    
    quantity = db.Column(db.Integer)
    specialInstructions = db.column(db.String(100))
    itemPrice = db.column(db.Float)

    
# Create all the tables defined by the model (only runs once at app start)
with app.app_context():
    db.create_all()

#create lists to populate menu_items table
sandwiches = [
    ('Seitan Philly', 
     'House-made seitan, green pepper, onion, swiss, optional: add mushrooms $1.50, sub house-made vegan cheese $3',
     11.50,'','sandwiches'),
    ('Seitan Gyro',
      'House-made seitan, romaine, tomato, red onion, cucumber, warm pita, side of tahini-garlic sauce, optional: add hummus $2.50',
      10.00,'vegan','sandwiches'),
    ('Banh Mi',
       'House-made seitan, cucumber, pickled daikon radish and carrot mix, cilantro-jalapeno sauce',
       11.00,'vegan','sandwiches'),
    ('Korean BBQ Tofu Bun',
     'Grilled marinated tofu, house-made kimchi, vegan mayo',
     11.00,'vegan','sandwiches'),
    ('Falafel Sandwich',
     'House-made falafel patties, romaine, tomato, red onion, cucumber on a warm pita, side of tahini-garlic sauce, optional: add hummus $2',
     10.00,'vegan','sandwiches'),
    ('Grilled Cheese',
     'Choice of bread: white, wheat, marble rye; grilled with choice of: cheddar or swiss, optional: sub house-made vegan cheese $3',
     9.00,'','sandwiches'),
    ('Veggie Wrap',
     'Garden vegetable tortilla, cheddar, hummus, spinach, tomato, grilled onion, green pepper, mushroom',
     14.00,'','sandwiches'),
    ('Tempeh Reuben',
     'Grilled tempeh, swiss, sauerkraut, thousand island dressing on marble rye, optional: add mushrooms $1.50, sub house-made vegan cheese $3',
     13.50,'','sandwiches'),
    ('TLT',
      'Grilled tempeh, lettuce, tomato, house-made vegan mayo on toasted wheat',
      11.00,'vegan','sandwiches'),
    ('Veggie Burger',
     'House-made veggie patty with lettuce, onion, tomato, side of vegan mayo, choice of: cheddar or swiss; optional: sub house-made vegan cheese $3',
     15.00,'','sandwiches')
    ]
platters = [
    ('Hummus Platter',
     'House-made hummus, spinach, tomato, cucumber, red onion, kalamata olives, served with warm pita bread and lemon wedge, optional: add feta $3, extra pita $2',
     12.00,'vegan','platters'),
    ('Falafel Platter',
      'House-made falafel patties, spinach, tomato, cucumber, red onion, kalamata olives, served with warm pita bread, hummus, lemon wedge and tahini-garlic dressing, optional: add feta $3, extra pita $2',
      14.00,'vegan','platters'),
    ('Tofu Garden Scramble',
     'Scrambled tofu, broccoli, cauliflower, carrot, garlic, grilled onion, green pepper, mushroom, served with brown rice on a bed of spinach with lemon wedge',
     12.50,'vegan, gluten-free','platters'),
    ('Steamed Rice and Vegetables',
     'Steamed kale, broccoli, cauliflower, carrot, garlic, brown rice, lemon wedge, choice of: korean bbq, tahini-garlic, or peanut sauce; optional: add seitan or tofu $3, add tempeh $3.50',
     10.00,'vegan, gluten-free','platters'),
    ('Seitan Fajitas',
     'Flour tortillas, house-made seitan grilled with onion, green peppers, and mushroom, lime wedge, served with brown rice, salsa, cilantro-jalapeno sauce, corn tortilla chips',
     13.00,'vegan','platters'),
    ('Burrito Grande',
     'Refried pinto beans or ancho-lime black beans, cheddar, brown rice, romaine lettuce, tomato, red onion, side of salsa, sour cream, cabbage jalapeno slaw, lime wedge, and corn tortilla chips, optional: sub house-made vegan cheese and cilantro-jalapeno sauce $3',
     16.00,'','platters'),
    ('Bean and Rice Burrito',
     'Refried pinto beans or ancho-lime black beans, and brown rice, side of salsa, cabbage jalapeno slaw, lime wedge, and corn tortilla chips, optional: add cheddar $2.50, add house-made vegan cheese $3',
     10.00,'vegan','platters'),
    ('Full Quesadilla',
     'Fried flour tortilla, cheddar, brown rice, refried pinto beans or ancho-lime black beans, side of salsa, cabbage jalapeno slaw, lime wedge, and sour cream, optional: sub house-made vegan cheese and cilantro-jalapeno sauce $3',
     13.00,'','platters'),
    ('Half Quesadilla',
     'Fried flour tortilla, cheddar, brown rice, refried pinto beans or ancho-lime black beans, side of salsa, cabbage jalapeno slaw, lime wedge, and sour cream, optional: sub house-made vegan cheese and cilantro-jalapeno sauce $3',
     9.00,'','platters'),
    ('Nachos',
     'Corn tortilla chips, cheddar, refried pinto beans or ancho-lime black beans, house-made salsa, cabbage jalapeno slaw, sour cream, lime wedge, optional: sub house-made vegan cheese and cilantro-jalapeno sauce $3',
     15.50,'gluten-free','platters')
]

smallPlates = [
    ('Chips and Salsa',
     'Organic corn tortilla chips with house-made salsa',
     7.00,'vegan, gluten-free','smallPlates'),
    ('Beans and Rice',
     'Refried pinto beans or ancho-lime black beans with rice served with lime wedge',
     7.00,'vegan, gluten-free','smallPlates'),
    ('Hummus and Pita',
     'House-made hummus, warm pita bread, served with lemon wedge',
     7.00,'vegan','smallPlates')
]

shortOrder = [
    ('Buttermilk Short Stack',
     'Three small cakes made with real buttermilk, optional: add real maple syrup $3',
     5.50,'','shortOrder'),
    ('Vegan Big Fat Pancake',
     'Plate sized vegan pancake, optional: add real maple syrup $3',
     5.50,'vegan','shortOrder'),
    ('French Toast',
     'Five slices of white bread, topped with powdered sugar, optional: add real maple syrup $3',
     10.00,'','shortOrder'),
    ('Granola with Yogurt',
     'With coconut, almond, and yogurt',
     5.50,'vegan','shortOrder'),
    ('Granola with Oatmilk',
     'With coconut, almond, and oatmilk',
     5.00,'vegan','shortOrder'),
    ('Granola with Soy or Dairy Milk',
     'With coconut, almond, and soy or dairy milk',
     4.50,'vegan','shortOrder'),
    ('Eggs and Toast',
     'Two eggs (specify style) with choice of toast: white, wheat, marble rye, optional: sub biscuit or bagel $1.50',
     6.00,'','shortOrder'),
    ('Tofu and Toast',
     'Scrambled tofu served with choice of toast: white, wheat, marble rye, optional: sub vegan biscuit or bagel $1.50',
     5.00,'vegan','shortOrder'),
    ('Full Hashbrowns',
     'Full order of hashbrowns, optional: add cheese $2.50, add house-made vegan cheese $3',
     6.00,'vegan','shortOrder'),
    ('Half Hashbrowns',
     'Half order of hashbrowns, optional: add cheese $2.50, add house-made vegan cheese $3',
     3.50,'vegan','shortOrder'),
    ('Vegan Sausage',
     'Single patty, made in-house',
     3.00,'vegan','shortOrder'),
    ('Bagel with Cream Cheese',
     'Simple bagel with cream cheese',
     5.00,'','shortOrder')
]

soups = [
    ('Bowl',
     'Soup of the day with choice of: gluten-free corn tortilla chips, white, wheat, or marble rye bread',
     6.00,'','soups'),
    ('Cup',
     'Soup of the day with choice of: gluten-free corn tortilla chips, white, wheat, or marble rye bread',
     4.50,'','soups'),
]

salads = [
    ('Greek Salad',
     'Spinach, romaine, tomato, red onion, cucumber, kalamata olive, feta, and lemon wedge, served with warm pita bread and balsamic viniagrette',
     15.00,'','salads'),
    ('Haystack',
     'Crushed corn tortilla chips, romaine, refried pinto beans or ancho-lime black beans, cheddar, tomato, house-made salsa, sour cream, and cabbage jalapeno slaw',
     15.50,'gluten-free','salads'),
    ('Garden Salad',
     'Romaine, spinach, onion, green pepper, carrot, cucumber, tomato, broccoli, cauliflower, choice of dressing',
     9.50,'vegan, gluten-free','salads'),
    ('Side Salad',
     'Romaine lettuce, tomato, cucumber, red onion, choice of dressing',
     5.00,'vegan, gluten-free','salads')
]

breakfast = [
    ('Helter Skelter',
     'Hashbrowns topped with a scrambled egg, cheddar, grilled onion, green pepper, mushroom, broccoli, califlower, tomato, choice of toast: white, wheat, marble rye',
     13.50,'gluten-free','breakfast'),
    ('Huevos Rancheros',
    'Corn tortillas topped with cheddar, refried pinto beans or ancho-lime black beans, basted eggs, salsa, sour cream, lime wedge, and cabbage jalapeno slaw',
    12.50,'gluten-free','breakfast'),
    ('Breakfast Burrito',
     'Cheddar, scrambled eggs, refried pinto beans or ancho-lime black beans, side of salsa, sour cream, cabbage jalapeno slaw, lime wedge, and corn tortilla chips',
     15.00,'','breakfast'),
    ('Migas',
     'Crispy corn tortillas scrambled with grilled onion, green pepper, mushroom, and eggs on a bed of spinach, topped with salsa and sour cream with cabbage jalapeno slaw and lime wedge',
     11.00,'gluten-free','breakfast'),
    ('Peasant Potatoes',
     'Hashbrown topped with grilled onion, green pepper, broccoli, cauliflower',
     11.00,'vegan, gluten-free','breakfast'),
    ('Full Biscuits and Gravy',
     'Buttermilk biscuits, house-made mushroom gravy topped with tomato and scallions',
     10.50,'','breakfast'),
    ('Half Biscuits and Gravy',
     'Buttermilk biscuit, house-made mushroom gravy topped with tomato and scallions',
     6.00,'','breakfast'),
    ('Breakfast Bagel',
     'House-made vegan sausage patty, scrambled egg, cheddar',
     8.00,'','breakfast'),
    ('Full Classic Breakfast',
     '2 eggs (specify style) with hashbrowns, choice of toast: wheat, white, marble rye',
     12.00,'','breakfast'),
    ('Half Classic Breakfast',
     '1 egg (specify style) with hashbrowns, choice of toast: wheat, white, marble rye',
     6.50,'','breakfast'),
    ('Biscuit Breakfast',
     'Buttermilk biscuit, one egg (specify style), hashbrowns, vegan sausage patty, optional: add house-made mushroom gravy $3',
     10.50,'','breakfast'),
    ('Vegan Helter Skelter',
     'Hashbrowns topped with scrambled tofu, grilled onion, green pepper, mushroom, broccoli, cauliflower, tomato, choice of toast: white, wheat, marble rye; optional: add house-made vegan cheese $3',
     13.00,'vegan, gluten-free','breakfast'),
    ('Vegan Rancheros',
     'Corn tortillas topped with refried pinto beans or ancho-lime black beans, scrambled with tofu, salsa, cilantro-jalapeno sauce, lime wedge, and cabbage jalapeno slaw, optional: add house-made vegan cheese $3',
     11.50,'vegan, gluten-free','breakfast'),
    ('Vegan Breakfast Burrito',
     'Scrambled tofu, refried pinto beans or ancho-lime black beans, side of salsa, cilantro-jalapeno sauce, cabbage jalapeno slaw, lime wedge, and corn tortilla chips, optional: add house-made vegan cheese $3',
     12.50,'vegan','breakfast'),
    ('Vegan Migas',
     'Crispy corn tortillas scrambled with grilled onion, green pepper, mushroom, tofu on a bed of spinach, topped with salsa and cilantro-jalapeno sauce with cabbage jalapeno slaw and lime wedge',
     10.00,'vegan, gluten-free','breakfast'),
    ('Full Vegan Biscuits and Gravy',
     'Vegan biscuits, house-made mushroom gravy topped with tomato and scallions',
     10.50,'vegan','breakfast'),
    ('Half Vegan Biscuits and Gravy',
     'Vegan biscuit, house-made mushroom gravy topped with tomato and scallions',
     6.00,'vegan','breakfast'),
    ('Vegan Breakfast Bagel',
     'House-made vegan sausage patty, scrambled tofu, house-made vegan cheese',
     10.50,'vegan','breakfast'),
    ('Full Vegan Classic Breakfast',
     'Scrambled tofu, hashbrowns, choice of toast: wheat, white, marble rye',
     11.50,'vegan','breakfast'),
    ('Half Vegan Classic Breakfast',
     'Scrambled tofu, hashbrowns, choice of toast: wheat, white, marble rye',
     6.00,'vegan','breakfast'),
    ('Vegan Biscuit Breakfast',
     'Vegan biscuit, scrambled tofu, hashbrowns, vegan sausage patty, optional: add house-made mushroom gravy $3',
     10.00,'vegan','breakfast')
]

# --- Define Routes ---

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')  # Renders home page

@app.route('/menu')
def menu():
    return render_template('menu.html')


# Route for the About page (supports both GET and POST)
@app.route('/about', methods=['GET', 'POST'])
def about():
    if request.method == 'POST':
        # Get the comment text submitted by the user
        comment_text = request.form['comment']

        # If comment is not empty, save it to the database
        if comment_text.strip():
            new_comment = Comment(text=comment_text.strip())
            db.session.add(new_comment)
            db.session.commit()

        # Redirect to avoid form resubmission on refresh
        return redirect(url_for('about'))

    # On GET request, fetch the latest 10 comments, newest first
    comments = Comment.query.order_by(Comment.id.desc()).limit(10).all()
    return render_template('about.html', comments=comments)

# Start the Flask development server
if __name__ == '__main__':
    app.run(debug=True)