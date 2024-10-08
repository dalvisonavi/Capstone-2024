from flask import Flask, request, jsonify, render_template, redirect, url_for
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb+srv://saidivya:saidivya1234@inventory.xp13j.mongodb.net/?retryWrites=true&w=majority&appName=Inventory')

db = client['Inventory']
users_collection = db['users']

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = users_collection.find_one({'username': username})

    if user and check_password_hash(user['password'], password):
        return redirect(url_for('add_ingredients'))  
    else:
        return jsonify({'message': 'Invalid username or password.'})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if users_collection.find_one({'username': username}):
            return jsonify({'message': 'User already exists!'})

        hashed_password = generate_password_hash(password)

        user = {
            'username': username,
            'password': hashed_password
        }

        users_collection.insert_one(user)
        return jsonify({'message': 'User registered successfully!'})

    return render_template('register.html')  # Render the registration form


if __name__ == "__main__":
    app.run(debug=True)
