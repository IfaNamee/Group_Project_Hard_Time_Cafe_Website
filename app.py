# Import necessary modules from Flask and SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize the Flask application
app = Flask(__name__)

# --- Database Configuration ---

# Set up the database URI for SQLite For (ABOUT US PAGE TO collect custemers comments)
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

# Start the Flask development server
if __name__ == '__main__':
    app.run(debug=True)