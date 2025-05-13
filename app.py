from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os 
import stripe 
import uuid
from datetime import datetime 

# Initialize the Flask application
app = Flask(__name__)

# --- Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Stripe API keys (replace with real one)
stripe.api_key = 'your_stripe_secret_key_here'

# --- Models ---
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)

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

# --- Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/menu', methods=['GET'])
def menu():
    category = request.args.get('category', 'all')
    if category == 'all':
        menuItems = menu_items.query.all()
    else:
        menuItems = menu_items.query.filter_by(category=category).all()
    categories = db.session.query(menu_items.category).distinct().order_by(menu_items.category).all()
    return render_template('menu.html', menuItems=menuItems, categories=categories, selected_category=category)

@app.route('/about', methods=['GET', 'POST'])
def about():
    if request.method == 'POST':
        comment_text = request.form['comment']
        if comment_text.strip():
            new_comment = Comment(text=comment_text.strip())
            db.session.add(new_comment)
            db.session.commit()
        return redirect(url_for('about'))
    comments = Comment.query.order_by(Comment.id.desc()).limit(10).all()
    return render_template('about.html', comments=comments)

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/place_order', methods=['POST'])
def place_order():
    try:
        data = request.get_json()
        if not data or 'cart' not in data:
            return jsonify({'success': False, 'error': 'No data received'}), 400

        new_order = orders(
            totalPrice=sum(item['price'] * item['quantity'] for item in data['cart'])
        )
        db.session.add(new_order)
        db.session.flush()  # to get orderId before committing

        for item in data['cart']:
            order_detail = orderDetails(
                itemId=item['id'],
                specialOrderId=new_order.orderId,
                quantity=item['quantity'],
                itemPrice=item['price']
            )
            db.session.add(order_detail)

        db.session.commit()

        return jsonify({
            'success': True,
            'order_id': new_order.orderId,
            'redirect': url_for('order_confirmation')
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/order_confirmation')
def order_confirmation():
    return render_template('order_confirmation.html')

def seed_menu_items():
    if menu_items.query.count() > 0:
        print("Menu already seeded.")
        return

    sandwiches = [
        menu_items(name='Seitan Philly', 
                   description='House-made seitan, green pepper, onion, swiss...',
                   price=11.50, denotations='', category='Sandwiches'),
        menu_items(name='Seitan Gyro',
                   description='House-made seitan, romaine, tomato, red onion...',
                   price=10.00, denotations='vegan', category='Sandwiches'),
        # Add more items from your original list here...
    ]

    platters = [
        menu_items(name='Hummus Platter',
                   description='House-made hummus, spinach, tomato...',
                   price=12.00, denotations='vegan', category='Platters'),
        # More platter items...
    ]

    # ... Add the rest: smallPlates, shortOrder, Soups, Salads, Breakfast

    db.session.add_all(sandwiches + platters)  # + smallPlates + ...
    db.session.commit()
    print("Menu seeded successfully.")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_menu_items()
    app.run(debug=True)
