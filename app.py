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
db = SQLAlchemy(app)

# --- Define Database Model ---

# Create a Comment model representing each comment entry in the database
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each comment
    text = db.Column(db.Text, nullable=False)     # Comment text (required)

# Create all the tables defined by the model (only runs once at app start)
with app.app_context():
    db.create_all()

# --- Define Routes ---

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')  # Renders home page

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

# --- CHECKOUT ROUTES --- 
@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/place_order', methods=['POST'])
@csrf.exempt # only if using AJAX with CSRF token in header
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