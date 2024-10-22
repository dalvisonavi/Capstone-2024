from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from controllers.rawmaterials import add_items_route, get_items_route
from routes.rawroutues import item_bp
from database.database import DBConfig
from flask_mail import Mail, Message
from bson.objectid import ObjectId
# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.yourmailserver.com'  # Update this with your mail server details
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@example.com'  # Update with your email
app.config['MAIL_PASSWORD'] = 'your-email-password'  # Update with your email password
mail = Mail(app)

# Connect to MongoDB
client = MongoClient('mongodb+srv://saidivya:saidivya1234@inventory.xp13j.mongodb.net/?retryWrites=true&w=majority&appName=Inventory')
db = client['Inventory']
users_collection = db['users']
suppliers_collection = db['suppliers']
rawmaterials_collection = db['rawmaterials']
inventory_collection = db['inventory']

# Initialize database
DBConfig()

# Register blueprint for raw materials
app.register_blueprint(item_bp)

# Route to render the main HTML page (before login)
@app.route("/")
def home():
    return render_template("index.html")

# Route for the dashboard page (after login)
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# Route for the inventory page
@app.route("/inventory")
def inventory():
    return render_template("inventory.html")

# Login route
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = users_collection.find_one({'username': username})

    if user and check_password_hash(user['password'], password):
        return redirect(url_for('dashboard'))
    else:
        return jsonify({'message': 'Invalid username or password.'})

# Register route
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

    return render_template('register.html')

# Route to manage orders and suppliers
@app.route('/order_management', methods=['GET', 'POST'])
def order_management():
    if request.method == 'POST':
        print("POST request received")
        
        # Retrieve form data
        supplier_name = request.form.get('supplier_name')
        contact_email = request.form.get('contact_email')
        contact_phone = request.form.get('contact_phone')
        products = request.form.get('products', '').split(",")  # Split products by commas

        # Debug: print retrieved form data
        print("Form data received:")
        print(f"Supplier Name: {supplier_name}")
        print(f"Contact Email: {contact_email}")
        print(f"Contact Phone: {contact_phone}")
        print(f"Products: {products}")

        # Validation: Check if any required field is empty
        if not supplier_name or not contact_email or not contact_phone or not products:
            print("Error: One or more required fields are empty!")
            return jsonify({'message': 'All fields are required!'}), 400

        # Insert data into MongoDB
        try:
            result = suppliers_collection.insert_one({
                'supplier_name': supplier_name,
                'contact_email': contact_email,
                'contact_phone': contact_phone,
                'products': products
            })
            print(f"Supplier added with ID: {result.inserted_id}")
            return redirect(url_for('order_management'))  # Redirect to avoid form resubmission
        except Exception as e:
            print(f"Error adding supplier to database: {e}")
            return jsonify({'message': 'Error adding supplier to database!'}), 500

    # GET request: Fetch suppliers and low stock items
    suppliers = list(suppliers_collection.find())
    print(f"Number of suppliers fetched: {len(suppliers)}")
    low_stock_items = list(db.rawmaterials.find())
    print(f"Number of low stock items fetched: {len(low_stock_items)}")

    return render_template('order_management.html', suppliers=suppliers, low_stock_items=low_stock_items)

@app.route('/update_supplier/<supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    data = request.json
    print(f"Incoming data for supplier ID {supplier_id}: {data}")  # Log incoming data

    # Check for existing supplier
    existing_supplier = suppliers_collection.find_one({'_id': ObjectId(supplier_id)})
    print(f"Existing supplier data: {existing_supplier}")  # Log existing supplier data

    if not existing_supplier:
        return jsonify({'message': 'Supplier not found!'}), 404

    # Prepare the new values
    supplier_name = data.get('supplier_name')
    contact_email = data.get('contact_email')
    contact_phone = data.get('contact_phone')
    products = data.get('products')

    # Log the new values
    print(f"New values to update: {supplier_name}, {contact_email}, {contact_phone}, {products}")  

    # Check if there's any change
    if (existing_supplier['supplier_name'] == supplier_name and
        existing_supplier['contact_email'] == contact_email and
        existing_supplier['contact_phone'] == contact_phone and
        existing_supplier['products'] == products):
        return jsonify({'message': 'No changes made to the supplier.'}), 200  # If no changes, return early

    # Proceed with the update
    result = suppliers_collection.update_one(
        {'_id': ObjectId(supplier_id)},
        {'$set': {
            'supplier_name': supplier_name,
            'contact_email': contact_email,
            'contact_phone': contact_phone,
            'products': products
        }}
    )

    print(f"Update result: {result}")  # Log the update result

    if result.modified_count == 1:
        return jsonify({'message': 'Supplier updated successfully!'}), 200
    else:
        return jsonify({'message': 'No changes made to the supplier.'}), 200


@app.route('/delete_supplier/<supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    try:
        result = suppliers_collection.delete_one({'_id': ObjectId(supplier_id)})
        if result.deleted_count == 1:
            return jsonify({'message': 'Supplier deleted successfully!'}), 200
        else:
            return jsonify({'message': 'Supplier not found!'}), 404
    except Exception as e:
        print(f"Error deleting supplier: {e}")
        return jsonify({'message': 'Error deleting supplier from database!'}), 500

# Route to trigger an order to a supplier
@app.route('/trigger_order/<product_id>', methods=['POST'])
def trigger_order(product_id):
    try:
        print(f"Product ID received: {product_id}")  # Debug: Check if product ID is correct
        
        # Convert the product_id to ObjectId and find the product in the inventory
        product = rawmaterials_collection.find_one({"_id": ObjectId(product_id)})
        
        if not product:
            print("Product not found!")  # Debug: Product not found
            return jsonify({'error': 'Product not found'}), 404

        print(f"Product found: {product}")  # Debug: Check what product was found

        # Ensure the product has a name
        if 'name' not in product:
            print("Product name not found in product details!")  # Debug: Product name is missing
            return jsonify({'error': 'Product name not found'}), 400

        # Find the corresponding supplier based on the product name
        supplier = suppliers_collection.find_one({"products": {"$in": [product['name'].strip()]}})
        
        if not supplier:
            print("Supplier not found!")  # Debug: Supplier not found
            return jsonify({'error': 'Supplier not found for this product'}), 404

        print(f"Supplier found: {supplier}")  # Debug: Check what supplier was found

        # Trigger the order
        send_order_to_supplier(supplier, product)
        
        return jsonify({'message': 'Order sent to supplier successfully!'}), 200
    
    except Exception as e:
        print(f"Error: {str(e)}")  # Debug: Catch any unexpected errors
        return jsonify({'error': str(e)}), 500



# Function to send an order email to the supplier
def send_order_to_supplier(supplier, product):
    try:
        subject = f"Order for {product['name']}"
        body = f"Dear {supplier['supplier_name']},\n\n" \
               f"We would like to order {product['quantity']} units of {product['name']}.\n" \
               f"Please confirm the order.\n\n" \
               f"Best regards,\n" \
               f"Your Company Name"
        
        # Use your email sending logic here
        send_email(supplier['contact_email'], subject, body)  # Replace with your actual email function

        print("Order sent successfully!")  # Debug: Confirm order sent
    except Exception as e:
        print(f"Error sending order: {str(e)}")  # Debug: Catch any errors in sending
        raise

# Function to send an email using Flask-Mail
def send_email(to, subject, body):
    msg = Message(subject, recipients=[to])
    msg.body = body
    try:
        mail.send(msg)
        print(f"Email sent to {to}")  # Debug: Confirm email sent
    except Exception as e:
        print(f"Error sending email: {str(e)}")  # Debug: Catch any email sending errors
        raise
# Ensure the app runs
if __name__ == "__main__":
    app.run(debug=True)
