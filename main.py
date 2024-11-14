from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file, Response
from io import BytesIO
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from controllers.rawmaterials import add_items_route, get_items_route
from routes.rawroutues import item_bp
from database.database import DBConfig
from flask_mail import Mail, Message
from bson.objectid import ObjectId
from datetime import datetime
import dateutil.parser
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import pymongo
# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Update this with your mail server details
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'cakeshopinventory@gmail.com'  # Update with your email
app.config['MAIL_PASSWORD'] = 'nfnk ptxq juhc pyjo'  # Update with your email password
mail = Mail(app)

# Connect to MongoDB
client = MongoClient('mongodb+srv://saidivya:saidivya1234@inventory.xp13j.mongodb.net/?retryWrites=true&w=majority&appName=Inventory')
db = client['Inventory']
users_collection = db['users']
suppliers_collection = db['suppliers']
rawmaterials_collection = db['rawmaterials']
baked_collection = db['bakedmaterials']
inventory_collection = db['inventory']

# Initialize database
DBConfig()

# Register blueprint for raw materials
app.register_blueprint(item_bp)

# Route to render the main HTML page (before login)
@app.route("/")
def home():
    return render_template("index.html")

# Route for the inventory page
# Route to manage inventory
@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    if request.method == 'POST':
        # Retrieve form data as JSON
        data = request.get_json()
        name = data.get('name')
        quantity = data.get('quantity')
        expiry_date = data.get('expiry_date')
        previous_stock = data.get('previous_stock')
        
        print("Form data received:")
        print(f"name: {name}")
        print(f"quantity: {quantity}")
        print(f"expiry_date: {expiry_date}")
        print(f"previous_stock: {previous_stock}")

        # Validation: Check if required fields are empty
        if not name or not quantity or not expiry_date or not previous_stock:
            return jsonify({'message': 'All fields are required!'}), 400
        
        # Insert the new item into the MongoDB inventory collection
        new_item = {
            'name': name,
            'quantity': int(quantity),
            'expiry_date': expiry_date,
            'previous_stock': int(previous_stock)
        }
        try:
            result = rawmaterials_collection.insert_one(new_item)
            new_item['_id'] = str(result.inserted_id)  # Convert ObjectId to string for JSON serialization
            print(f"Item added with ID: {result.inserted_id}")
            return jsonify({'message': 'item added successfully!', 'item': new_item}), 200
        except Exception as e:
            print(f"Error adding item: {e}")
            return jsonify({'message': 'Error adding item to database!'}), 500
    
    # For GET requests, retrieve all inventory items
    items = list(rawmaterials_collection.find())
    baked_products = list(baked_collection.find())
    return render_template('inventory.html', items=items, baked_products=baked_products)

# Route to edit an existing item in the inventory
@app.route('/edit_inventory/<item_id>', methods=['POST'])
def edit_inventory(item_id):
    data = request.json
    name = data.get('name')
    quantity = data.get('quantity')
    expiry_date = data.get('expiry_date')
    previous_stock = data.get('previous_stock')

    # Update the item in the MongoDB inventory collection
    update_data = {
        'name': name,
        'quantity': quantity,
        'expiry_date': expiry_date,
        'previous_stock': previous_stock
    }
    result = rawmaterials_collection.update_one(
        {'_id': ObjectId(item_id)},
        {'$set': update_data}
    )

    if result.modified_count == 1:
        return jsonify({'message': 'Item updated successfully!'}), 200
    else:
        return jsonify({'message': 'No changes made to the item.'}), 200

from bson import ObjectId

# Route to delete an item from the inventory
@app.route('/delete_inventory/<item_id>', methods=['DELETE'])
def delete_inventory(item_id):
    try:
        result = rawmaterials_collection.delete_one({'_id': ObjectId(item_id)})
        if result.deleted_count == 1:
            return jsonify({'message': 'Item deleted successfully!'}), 200
        else:
            return jsonify({'message': 'Item not found!'}), 404
    except Exception as e:
        return jsonify({'message': 'Error deleting item from database!'}), 500



@app.route('/update_item/<item_id>', methods=['POST'])
def update_item(item_id):
    data = request.json
    print(f"Incoming data for item ID {item_id}: {data}")  # Log incoming data

    # Check for existing item
    existing_item = rawmaterials_collection.find_one({'_id': ObjectId(item_id)})
    print(f"Existing item data: {existing_item}")  # Log existing item data

    if not existing_item:
        return jsonify({'message': 'Item not found!'}), 404

    # Prepare the new values with correct data types
    name = data.get('name')
    quantity = data.get('quantity')  # Quantity stored as a string
    expiry_date = data.get('expiryDate')  # Stored as a string in format "YYYY-MM-DD"
    previous_stock = data.get('prevStock')  # Stored as a string

    # Log the new values
    print(f"New values to update: {name}, {quantity}, {expiry_date}, {previous_stock}")  

    # Check if there's any change
    if (existing_item['name'] == name and
        existing_item['quantity'] == quantity and
        existing_item['expiry_date'] == expiry_date and
        existing_item['previous_stock'] == previous_stock):
        return jsonify({'message': 'No changes made to the item.'}), 200  # If no changes, return early

    # Proceed with the update
    result = rawmaterials_collection.update_one(
        {'_id': ObjectId(item_id)},
        {'$set': {
            'name': name,
            'quantity': quantity,
            'expiry_date': expiry_date,
            'previous_stock': previous_stock
        }}
    )

    print(f"Update result: {result}")  # Log the modified count

    if result.modified_count == 1:
        # Fetch the updated document and convert ObjectId to string for JSON serialization
        return jsonify({'message': 'Item updated successfully!'}), 200
    else:
        return jsonify({'message': 'No changes made to the item.'}), 400
    


@app.route('/baked_products', methods=['GET', 'POST'])
def baked_products():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        quantity = data.get('quantity')
        prepdate = data.get('prepdate')
        expiry_date = data.get('expiry_date')

        print("Baked product form data received:")
        print(f"name: {name}")
        print(f"quantity: {quantity}")
        print(f"prepdate: {prepdate}")
        print(f"expiry_date: {expiry_date}")

        # Check if all fields are provided and valid
        if not all([name, quantity, prepdate, expiry_date]):
            return jsonify({'message': 'All fields are required!'}), 400

        try:
            quantity = int(quantity)
            prepdate = datetime.strptime(prepdate, '%Y-%m-%d').date()
            expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
        except ValueError as ve:
            print(f"Date parsing error: {ve}")
            return jsonify({'message': 'Invalid data format! Ensure date is YYYY-MM-DD and quantity is a number.'}), 400

        # New baked product data structure
        new_baked_product = {
            'name': name,
            'quantity': quantity,
            'prepdate': prepdate.isoformat(),
            'expiry_date': expiry_date.isoformat(),
        }

        try:
            result = baked_collection.insert_one(new_baked_product)
            new_baked_product['_id'] = str(result.inserted_id)
            print(f"Item added with ID:{result.inserted_id}")
            return jsonify({'message': 'Baked product added successfully!', 'item': new_baked_product}), 201
        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({'message': 'Error adding baked product to database!'}), 500

    # Retrieve baked products to display on the page
    baked_products = list(baked_collection.find())
    return render_template('inventory_management.html', baked_products=baked_products)

@app.route('/edit_baked_product/<item_id>', methods=['POST'])
def edit_baked_product(item_id):
    data = request.json
    name = data.get('name')
    quantity = data.get('quantity')
    prepdate = data.get('prepdate')
    expiry_date = data.get('expiry_date')
    update_data = {
        'name': name,
        'quantity': quantity,
        'prepdate': prepdate,
        'expiry_date': expiry_date
    }
    result = baked_collection.update_one(
        {'_id': ObjectId(item_id)},
        {'$set': update_data}
    )

    if result.modified_count == 1:
        return jsonify({'message': 'Baked product updated successfully!'}), 200
    else:
        return jsonify({'message': 'No changes made to the baked product.'}), 200


@app.route('/delete_baked_product/<item_id>', methods=['DELETE'])
def delete_baked_product(item_id):
    try:
        # Check if the provided item_id is a valid ObjectId format
        object_id = ObjectId(item_id)
    except Exception as e:
        return jsonify({'message': f'Invalid ObjectId format: {str(e)}'}), 400

    # Log the object_id to confirm it's correct
    print(f"Attempting to delete item with ID: {item_id}")

    # Try to find the item first to check if it's in the database
    item = baked_collection.find_one({'_id': object_id})
    
    # Log the result of the find query
    if item:
        print(f"Item found: {item}")
    else:
        print("Item not found")

    if not item:
        return jsonify({'message': 'Baked product not found!'}), 404

    # Delete the item if found
    result = baked_collection.delete_one({'_id': object_id})
    if result.deleted_count == 1:
        return jsonify({'message': 'Baked product deleted successfully!'}), 200
    else:
        return jsonify({'message': 'Error deleting baked product from database!'}), 500


@app.route('/update_baked_product/<item_id>', methods=['POST'])
def update_baked_product(item_id):
    data = request.json
    print(f"Incoming data for baked product ID {item_id}: {data}")

    existing_product = baked_collection.find_one({'_id': ObjectId(item_id)})
    print(f"Existing baked product data: {existing_product}")

    if not existing_product:
        return jsonify({'message': 'Baked product not found!'}), 404

    name = data.get('name')
    quantity = data.get('quantity')
    prepdate = data.get('prepdate')
    expiry_date = data.get('expiry_date')

    if (existing_product['name'] == name and
        existing_product['quantity'] == quantity and
        existing_product['prepdate'] == prepdate and
        existing_product['expiry_date'] == expiry_date):
        return jsonify({'message': 'No changes made to the baked product.'}), 200

    result = baked_collection.update_one(
        {'_id': ObjectId(item_id)},
        {'$set': {
            'name': name,
            'quantity': quantity,
            'prepdate': prepdate,
            'expiry_date': expiry_date,
        }}
    )

    if result.modified_count == 1:
        return jsonify({'message': 'Baked product updated successfully!'}), 200
    else:
        return jsonify({'message': 'No changes made to the baked product.'}), 400



# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            return redirect(url_for('inventory'))
        else:
            return jsonify({'message': 'Invalid username or password.'})
    else:
        return render_template('index.html')


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
        return jsonify({'message': 'User registered successfully!'}),

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
    low_stock_items = list(db.rawmaterials.find({"quantity": {"$lte": 5}}))
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

        # Trigger the order (send email)
        email_sent = send_order_to_supplier(supplier, product)

        # Check if email was sent successfully
        if email_sent:
            return jsonify({'message': 'Order sent to supplier successfully!'}), 200
        else:
            return jsonify({'error': 'Failed to send order email'}), 500

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
               f"The cake shop"
        
        # Use your actual email sending logic here
        send_email(supplier['contact_email'], subject, body)  # Replace with your actual email function

        print("Order sent successfully!")  # Debug: Confirm order sent
        return True  # Return True if email is sent successfully
    except Exception as e:
        print(f"Error sending order: {str(e)}")  # Debug: Catch any errors in sending
        return False  # Return False if email sending fails


# Function to send an email using Flask-Mail
def send_email(to, subject, body):
    msg = Message(subject, recipients=[to], sender="cakeshopinventory@gmail.com")
    msg.body = body
    try:
        mail.send(msg)
        print(f"Email sent to {to}")  # Debug: Confirm email sent
    except Exception as e:
        print(f"Error sending email: {str(e)}")  # Debug: Catch any email sending errors
        raise


@app.route('/wastage_log')
def wastage_log():
    today = datetime.now()

    # Fetch expired raw materials and safely check for expiry_date
    raw_expired = [
        {**item, "expiry_date": dateutil.parser.parse(item["expiry_date"])}  # Convert to datetime object
        for item in rawmaterials_collection.find()
        if "expiry_date" in item and dateutil.parser.parse(item["expiry_date"]) < today
    ]

    # Fetch expired baked materials and safely check for expiry_date
    baked_expired = [
        {**item, "expiry_date": dateutil.parser.parse(item["expiry_date"])}  # Convert to datetime object
        for item in baked_collection.find()
        if "expiry_date" in item and dateutil.parser.parse(item["expiry_date"]) < today
    ]

    return render_template('wastage_log.html', raw_expired=raw_expired, baked_expired=baked_expired)

# Route to delete an expired item
@app.route('/delete-wastage/<material_type>/<item_id>', methods=['POST'])
def delete_wastage(material_type, item_id):
    collection = rawmaterials_collection if material_type == "raw" else baked_collection
    collection.delete_one({"_id": ObjectId(item_id)})
    return redirect(url_for('wastage_log'))

@app.route('/end_day_report')
def end_day_report():
    # Fetch data from MongoDB and structure it for display
    data = list(baked_collection.find({}, {"_id": 0, "name": 1, "quantity": 1, "sold_quantity": 1, "expiry_date": 1}))
    
    # Pass data to the template
    return render_template("end_day_report.html", report_data=data)

# Additional route for CSV download (optional)
@app.route('/download_csv')
def download_csv():
    items = baked_collection.find()
    
    def generate():
        data = ['Product Name, Stock Quantity, Sold Quantity, Expiry Date\n']  # Header row
        for item in items:
            line = f"{item['name']},{item['quantity']},{item['sold_quantity']},{item['expiry_date']}\n"
            data.append(line)
        return data

    return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=report.csv"})

# Additional route for PDF download (optional)
@app.route('/download_pdf')
def download_pdf():
    items = baked_collection.find()

    # Create a PDF in memory
    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=letter)
    pdf.setTitle("End of Day Report")
    
    pdf.drawString(100, 750, "End of Day Report")
    pdf.drawString(100, 735, f"Date: {datetime.now().date()}")

    # Define starting Y position for table data
    y_position = 700
    pdf.drawString(50, y_position, "Product Name")
    pdf.drawString(200, y_position, "Stock Quantity")
    pdf.drawString(350, y_position, "Sold Quantity")
    pdf.drawString(500, y_position, "Expiry Date")

    y_position -= 20
    
    for item in items:
        if y_position < 50:
            pdf.showPage()
            y_position = 750  # Reset position for new page
            pdf.drawString(50, y_position, "Product Name")
            pdf.drawString(200, y_position, "Stock Quantity")
            pdf.drawString(350, y_position, "Sold Quantity")
            pdf.drawString(500, y_position, "Expiry Date")
            y_position -= 20
        
        # Ensure sold_quantity is valid, and set a default value if not
        sold_quantity = str(item.get('sold_quantity', 'N/A'))  # Default to 'N/A' if not found
        pdf.drawString(50, y_position, item['name'])
        pdf.drawString(200, y_position, str(item['quantity']))
        pdf.drawString(350, y_position, sold_quantity)
        pdf.drawString(500, y_position, item['expiry_date'])
        y_position -= 20
    
    pdf.showPage()
    pdf.save()
    output.seek(0)

    return Response(
        output,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment;filename=end_day_report_{datetime.now().date()}.pdf"}
    )


# Ensure the app runs
if __name__ == "__main__":
    app.run(debug=True)
