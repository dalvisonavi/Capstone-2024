from flask import Flask, request, jsonify, render_template, redirect, url_for
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb+srv://saidivya:saidivya1234@inventory.xp13j.mongodb.net/?retryWrites=true&w=majority&appName=Inventory')  # Replace with your MongoDB URI
db = client['Inventory']  # Replace 'loginDB' with your database name
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
        return jsonify({'message': 'Login successful!'})
    else:
        return jsonify({'message': 'Invalid username or password.'})

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    
    # Check if user already exists
    if users_collection.find_one({'username': username}):
        return jsonify({'message': 'User already exists!'})
    
    # Hash the password before storing it
    hashed_password = generate_password_hash(password)

    # Create user document
    user = {
        'username': username,
        'password': hashed_password
    }

    users_collection.insert_one(user)
    return jsonify({'message': 'User registered successfully!'})

if __name__ == "__main__":
    app.run(host="0.0.0.0")