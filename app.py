# Import necessary modules from Flask and SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect 
import os
import uuid # generating order IDs

# Initialize the Flask application
app = Flask(__name__)

# --- Database Configuration ---

# Set up the database URI for SQLite For (ABOUT US PAGE TO collect custemers comments)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comments.db'

# Disable modification tracking to save resources
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the Flask app
db = SQLAlchemy(app)

# --- Security Configuration ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-fallback-key') # required CSRF
csrf = CSRFProtection(app) # initialize CSRF protection

# --- Database Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://comments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Define Database Model ---

# Create a Comment model representing each comment entry in the database
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each comment
    text = db.Column(db.Text, nullable=False)     # Comment text (required)

class menu_items(db.Model):
    menuId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100))
    price = db.Column(db.Float, nullable=False)
    denotations = db.Column(db.String(100))
    category = db.Column(db.String(100))

    item = db.relationship('orderDetails', foreign_keys='orderDetails.itemId', backref='menu_items', lazy=True)

    def __repr__(self):
        return f'<menu_items name={self.name}>'
    

class orders(db.Model):
    orderId = db.Column(db.Integer, primary_key=True)
    orderDate = db.Column(db.DateTime, default=datetime.utcnow)
    totalPrice = db.Column(db.Float)

    special = db.relationship('orderDetails', foreign_keys='orderDetails.specialOrderId', backref='orders', lazy=True)
    
    
class orderDetails(db.Model):
    detailId = db.Column(db.Integer, primary_key=True)
    
    itemId = db.Column(db.Integer, db.ForeignKey(menu_items.menuId))
    
    specialOrderId = db.Column(db.Integer, db.ForeignKey(orders.orderId))
    
    quantity = db.Column(db.Integer)
    specialInstructions = db.Column(db.String(100))
    itemPrice = db.Column(db.Float)

# Create all the tables defined by the model (only runs once at app start)
with app.app_context():
    db.create_all()

    db.session.query(menu_items).delete()
    db.session.commit()

    if menu_items.query.count() == 0:

        #create lists to populate menu_items table
        Sandwiches = [
            menu_items(name='Seitan Philly', 
            description='House-made seitan, green pepper, onion, swiss, optional: add mushrooms $1.50, sub house-made vegan cheese $3',
            price=11.50,denotations='',category='Sandwiches'),
            menu_items(name='Seitan Gyro',
            description='House-made seitan, romaine, tomato, red onion, cucumber, warm pita, side of tahini-garlic sauce, optional: add hummus $2.50',
            price=10.00,denotations='vegan',category='Sandwiches'),
            menu_items(name='Banh Mi',
            description='House-made seitan, cucumber, pickled daikon radish and carrot mix, cilantro-jalapeno sauce',
            price=11.00,denotations='vegan',category='Sandwiches'),
            menu_items(name='Korean BBQ Tofu Bun',
            description='Grilled marinated tofu, house-made kimchi, vegan mayo',
            price=11.00,denotations='vegan',category='Sandwiches'),
            menu_items(name='Falafel Sandwich',
            description='House-made falafel patties, romaine, tomato, red onion, cucumber on a warm pita, side of tahini-garlic sauce, optional: add hummus $2',
            price=10.00,denotations='vegan',category='Sandwiches'),
            menu_items(name='Grilled Cheese',
            description='Choice of bread: white, wheat, marble rye; grilled with choice of: cheddar or swiss, optional: sub house-made vegan cheese $3',
            price=9.00,denotations='',category='Sandwiches'),
            menu_items(name='Veggie Wrap',
            description='Garden vegetable tortilla, cheddar, hummus, spinach, tomato, grilled onion, green pepper, mushroom',
            price=14.00,denotations='',category='Sandwiches'),
            menu_items(name='Tempeh Reuben',
            description='Grilled tempeh, swiss, sauerkraut, thousand island dressing on marble rye, optional: add mushrooms $1.50, sub house-made vegan cheese $3',
            price=13.50,denotations='',category='Sandwiches'),
            menu_items(name='TLT',
            description='Grilled tempeh, lettuce, tomato, house-made vegan mayo on toasted wheat',
            price=11.00,denotations='vegan',category='Sandwiches'),
            menu_items(name='Veggie Burger',
            description='House-made veggie patty with lettuce, onion, tomato, side of vegan mayo, choice of: cheddar or swiss; optional: sub house-made vegan cheese $3',
            price=15.00,denotations='',category='Sandwiches')
            ]
        Platters = [
            menu_items(name='Hummus Platter',
            description='House-made hummus, spinach, tomato, cucumber, red onion, kalamata olives, served with warm pita bread and lemon wedge, optional: add feta $3, extra pita $2',
            price=12.00,denotations='vegan',category='Platters'),
            menu_items(name='Falafel Platter',
            description='House-made falafel patties, spinach, tomato, cucumber, red onion, kalamata olives, served with warm pita bread, hummus, lemon wedge and tahini-garlic dressing, optional: add feta $3, extra pita $2',
            price=14.00,denotations='vegan',category='Platters'),
            menu_items(name='Tofu Garden Scramble',
            description='Scrambled tofu, broccoli, cauliflower, carrot, garlic, grilled onion, green pepper, mushroom, served with brown rice on a bed of spinach with lemon wedge',
            price=12.50,denotations='vegan, gluten-free',category='Platters'),
            menu_items(name='Steamed Rice and Vegetables',
            description='Steamed kale, broccoli, cauliflower, carrot, garlic, brown rice, lemon wedge, choice of: korean bbq, tahini-garlic, or peanut sauce; optional: add seitan or tofu $3, add tempeh $3.50',
            price=10.00,denotations='vegan, gluten-free',category='Platters'),
            menu_items(name='Seitan Fajitas',
            description='Flour tortillas, house-made seitan grilled with onion, green peppers, and mushroom, lime wedge, served with brown rice, salsa, cilantro-jalapeno sauce, corn tortilla chips',
            price=13.00,denotations='vegan',category='Platters'),
            menu_items(name='Burrito Grande',
            description='Refried pinto beans or ancho-lime black beans, cheddar, brown rice, romaine lettuce, tomato, red onion, side of salsa, sour cream, cabbage jalapeno slaw, lime wedge, and corn tortilla chips, optional: sub house-made vegan cheese and cilantro-jalapeno sauce $3',
            price=16.00,denotations='',category='Platters'),
            menu_items(name='Bean and Rice Burrito',
            description='Refried pinto beans or ancho-lime black beans, and brown rice, side of salsa, cabbage jalapeno slaw, lime wedge, and corn tortilla chips, optional: add cheddar $2.50, add house-made vegan cheese $3',
            price=10.00,denotations='vegan',category='Platters'),
            menu_items(name='Full Quesadilla',
            description='Fried flour tortilla, cheddar, brown rice, refried pinto beans or ancho-lime black beans, side of salsa, cabbage jalapeno slaw, lime wedge, and sour cream, optional: sub house-made vegan cheese and cilantro-jalapeno sauce $3',
            price=13.00,denotations='',category='Platters'),
            menu_items(name='Half Quesadilla',
            description='Fried flour tortilla, cheddar, brown rice, refried pinto beans or ancho-lime black beans, side of salsa, cabbage jalapeno slaw, lime wedge, and sour cream, optional: sub house-made vegan cheese and cilantro-jalapeno sauce $3',
            price=9.00,denotations='',category='Platters'),
            menu_items(name='Nachos',
            description='Corn tortilla chips, cheddar, refried pinto beans or ancho-lime black beans, house-made salsa, cabbage jalapeno slaw, sour cream, lime wedge, optional: sub house-made vegan cheese and cilantro-jalapeno sauce $3',
            price=15.50,denotations='gluten-free',category='Platters')
        ]

        smallPlates = [
            menu_items(name='Chips and Salsa',
            description='Organic corn tortilla chips with house-made salsa',
            price=7.00,denotations='vegan, gluten-free',category='Small Plates'),
            menu_items(name='Beans and Rice',
            description='Refried pinto beans or ancho-lime black beans with rice served with lime wedge',
            price=7.00,denotations='vegan, gluten-free',category='Small Plates'),
            menu_items(name='Hummus and Pita',
            description='House-made hummus, warm pita bread, served with lemon wedge',
            price=7.00,denotations='vegan',category='Small Plates')
        ]

        shortOrder = [
            menu_items(name='Buttermilk Short Stack',
            description='Three small cakes made with real buttermilk, optional: add real maple syrup $3',
            price=5.50,denotations='',category='Short Order'),
            menu_items(name='Vegan Big Fat Pancake',
            description='Plate sized vegan pancake, optional: add real maple syrup $3',
            price=5.50,denotations='vegan',category='Short Order'),
            menu_items(name='French Toast',
            description='Five slices of white bread, topped with powdered sugar, optional: add real maple syrup $3',
            price=10.00,denotations='',category='Short Order'),
            menu_items(name='Granola with Yogurt',
            description='With coconut, almond, and yogurt',
            price=5.50,denotations='vegan',category='Short Order'),
            menu_items(name='Granola with Oatmilk',
            description='With coconut, almond, and oatmilk',
            price=5.00,denotations='vegan',category='Short Order'),
            menu_items(name='Granola with Soy or Dairy Milk',
            description='With coconut, almond, and soy or dairy milk',
            price=4.50,denotations='vegan',category='Short Order'),
            menu_items(name='Eggs and Toast',
            description='Two eggs (specify style) with choice of toast: white, wheat, marble rye, optional: sub biscuit or bagel $1.50',
            price=6.00,denotations='',category='Short Order'),
            menu_items(name='Tofu and Toast',
            description='Scrambled tofu served with choice of toast: white, wheat, marble rye, optional: sub vegan biscuit or bagel $1.50',
            price=5.00,denotations='vegan',category='Short Order'),
            menu_items(name='Full Hashbrowns',
            description='Full order of hashbrowns, optional: add cheese $2.50, add house-made vegan cheese $3',
            price=6.00,denotations='vegan',category='Short Order'),
            menu_items(name='Half Hashbrowns',
            description='Half order of hashbrowns, optional: add cheese $2.50, add house-made vegan cheese $3',
            price=3.50,denotations='vegan',category='Short Order'),
            menu_items(name='Vegan Sausage',
            description='Single patty, made in-house',
            price=3.00,denotations='vegan',category='Short Order'),
            menu_items(name='Bagel with Cream Cheese',
            description='Simple bagel with cream cheese',
            price=5.00,denotations='',category='Short Order')
        ]

        Soups = [
            menu_items(name='Bowl',
            description='Soup of the day with choice of: gluten-free corn tortilla chips, white, wheat, or marble rye bread',
            price=6.00,denotations='',category='Soups'),
            menu_items(name='Cup',
            description='Soup of the day with choice of: gluten-free corn tortilla chips, white, wheat, or marble rye bread',
            price=4.50,denotations='',category='Soups'),
        ]

        Salads = [
            menu_items(name='Greek Salad',
            description='Spinach, romaine, tomato, red onion, cucumber, kalamata olive, feta, and lemon wedge, served with warm pita bread and balsamic viniagrette',
            price=15.00,denotations='',category='Salads'),
            menu_items(name='Haystack',
            description='Crushed corn tortilla chips, romaine, refried pinto beans or ancho-lime black beans, cheddar, tomato, house-made salsa, sour cream, and cabbage jalapeno slaw',
            price=15.50,denotations='gluten-free',category='Salads'),
            menu_items(name='Garden Salad',
            description='Romaine, spinach, onion, green pepper, carrot, cucumber, tomato, broccoli, cauliflower, choice of dressing',
            price=9.50,denotations='vegan, gluten-free',category='Salads'),
            menu_items(name='Side Salad',
            description='Romaine lettuce, tomato, cucumber, red onion, choice of dressing',
            price=5.00,denotations='vegan, gluten-free',category='Salads')
        ]

        Breakfast = [
            menu_items(name='Helter Skelter',
            description='Hashbrowns topped with a scrambled egg, cheddar, grilled onion, green pepper, mushroom, broccoli, califlower, tomato, choice of toast: white, wheat, marble rye',
            price=13.50,denotations='gluten-free',category='Breakfast'),
            menu_items(name='Huevos Rancheros',
            description='Corn tortillas topped with cheddar, refried pinto beans or ancho-lime black beans, basted eggs, salsa, sour cream, lime wedge, and cabbage jalapeno slaw',
            price=12.50,denotations='gluten-free',category='Breakfast'),
            menu_items(name='Breakfast Burrito',
            description='Cheddar, scrambled eggs, refried pinto beans or ancho-lime black beans, side of salsa, sour cream, cabbage jalapeno slaw, lime wedge, and corn tortilla chips',
            price=15.00,denotations='',category='Breakfast'),
            menu_items(name='Migas',
            description='Crispy corn tortillas scrambled with grilled onion, green pepper, mushroom, and eggs on a bed of spinach, topped with salsa and sour cream with cabbage jalapeno slaw and lime wedge',
            price=11.00,denotations='gluten-free',category='Breakfast'),
            menu_items(name='Peasant Potatoes',
            description='Hashbrown topped with grilled onion, green pepper, broccoli, cauliflower',
            price=11.00,denotations='vegan, gluten-free',category='Breakfast'),
            menu_items(name='Full Biscuits and Gravy',
            description='Buttermilk biscuits, house-made mushroom gravy topped with tomato and scallions',
            price=10.50,denotations='',category='Breakfast'),
            menu_items(name='Half Biscuits and Gravy',
            description='Buttermilk biscuit, house-made mushroom gravy topped with tomato and scallions',
            price=6.00,denotations='',category='Breakfast'),
            menu_items(name='Breakfast Bagel',
            description='House-made vegan sausage patty, scrambled egg, cheddar',
            price=8.00,denotations='',category='Breakfast'),
            menu_items(name='Full Classic Breakfast',
            description='2 eggs (specify style) with hashbrowns, choice of toast: wheat, white, marble rye',
            price=12.00,denotations='',category='Breakfast'),
            menu_items(name='Half Classic Breakfast',
            description='1 egg (specify style) with hashbrowns, choice of toast: wheat, white, marble rye',
            price=6.50,denotations='',category='Breakfast'),
            menu_items(name='Biscuit Breakfast',
            description='Buttermilk biscuit, one egg (specify style), hashbrowns, vegan sausage patty, optional: add house-made mushroom gravy $3',
            price=10.50,denotations='',category='Breakfast'),
            menu_items(name='Vegan Helter Skelter',
            description='Hashbrowns topped with scrambled tofu, grilled onion, green pepper, mushroom, broccoli, cauliflower, tomato, choice of toast: white, wheat, marble rye; optional: add house-made vegan cheese $3',
            price=13.00,denotations='vegan, gluten-free',category='Breakfast'),
            menu_items(name='Vegan Rancheros',
            description='Corn tortillas topped with refried pinto beans or ancho-lime black beans, scrambled with tofu, salsa, cilantro-jalapeno sauce, lime wedge, and cabbage jalapeno slaw, optional: add house-made vegan cheese $3',
            price=11.50,denotations='vegan, gluten-free',category='Breakfast'),
            menu_items(name='Vegan Breakfast Burrito',
            description='Scrambled tofu, refried pinto beans or ancho-lime black beans, side of salsa, cilantro-jalapeno sauce, cabbage jalapeno slaw, lime wedge, and corn tortilla chips, optional: add house-made vegan cheese $3',
            price=12.50,denotations='vegan',category='Breakfast'),
            menu_items(name='Vegan Migas',
            description='Crispy corn tortillas scrambled with grilled onion, green pepper, mushroom, tofu on a bed of spinach, topped with salsa and cilantro-jalapeno sauce with cabbage jalapeno slaw and lime wedge',
            price=10.00,denotations='vegan, gluten-free',category='Breakfast'),
            menu_items(name='Full Vegan Biscuits and Gravy',
            description='Vegan biscuits, house-made mushroom gravy topped with tomato and scallions',
            price=10.50,denotations='vegan',category='Breakfast'),
            menu_items(name='Half Vegan Biscuits and Gravy',
            description='Vegan biscuit, house-made mushroom gravy topped with tomato and scallions',
            price=6.00,denotations='vegan',category='Breakfast'),
            menu_items(name='Vegan Breakfast Bagel',
            description='House-made vegan sausage patty, scrambled tofu, house-made vegan cheese',
            price=10.50,denotations='vegan',category='Breakfast'),
            menu_items(name='Full Vegan Classic Breakfast',
            description='Scrambled tofu, hashbrowns, choice of toast: wheat, white, marble rye',
            price=11.50,denotations='vegan',category='Breakfast'),
            menu_items(name='Half Vegan Classic Breakfast',
            description='Scrambled tofu, hashbrowns, choice of toast: wheat, white, marble rye',
            price=6.00,denotations='vegan',category='Breakfast'),
            menu_items(name='Vegan Biscuit Breakfast',
            description='Vegan biscuit, scrambled tofu, hashbrowns, vegan sausage patty, optional: add house-made mushroom gravy $3',
            price=10.00,denotations='vegan',category='Breakfast')
        ]

        db.session.add_all(Sandwiches)
        db.session.add_all(Platters)
        db.session.add_all(smallPlates)
        db.session.add_all(shortOrder)
        db.session.add_all(Soups)
        db.session.add_all(Salads)
        db.session.add_all(Breakfast)
        db.session.commit()

# --- Define Routes ---


# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')  # Renders home page

@app.route('/menu', methods=['GET'])
def menu():
    category = request.args.get('category','all')
    if category == 'all':
        menuItems = menu_items.query.all()
    else:
        menuItems = menu_items.query.filter_by(category=category).all()
    
    categories = db.session.query(menu_items.category).distinct().all()
    return render_template('menu.html', menuItems=menuItems, categories=categories, selected_category=category)


# Route for the About page (supports both GET and POST)
@app.route('/about', methods=['GET', 'POST'])
@csrf.exempt
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

# --- CHECKOUT ROUTES --- 
@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/place_order', methods=['POST'])

def place_order():
    try:
        # Get and validate data
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        # validate required fields
        required = ['cart', 'payment', 'address']
        if not all(k in data for k in required):
            return jsonify({'success': False, 'error': 'Missing fields'}), 400
        
        # process order(mock)
        print(f"New order: {len(data['cart'])} items to {data['address']}")


        return jsonify({
            'success': True,
            'order_id': str(uuid.uuid4()), # temp mock id
            'redirect': url_for('order_confirmation')
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/order_confirmation')
def order_confirmation():
    return render_template('order_confirmation.html') # create confirmation.html page later!

# --- Error Handling ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Start the Flask development server
if __name__ == '__main__':
    app.run(debug=True)
