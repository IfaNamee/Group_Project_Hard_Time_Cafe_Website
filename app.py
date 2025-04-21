from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')  # Make sure this file exists in templates/

if __name__ == '__main__':
    app.run(debug=True)
