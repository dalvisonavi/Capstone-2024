from flask import request, jsonify
from database.database import DBConfig

# Get the MongoDB collection
baked_collection = DBConfig()["bakedmaterials"]  # Call the DBConfig function


def delItem():
    try:
        name="vanilla"
        baked_collection.delete_one({"name":name})
        return "deleted successfully"
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "Error deleting item!"}), 500

# Route to add items to MongoDB
def add_items_route():
    try:
        # Get the JSON data from the request
        data = request.json
        item_name = data.get("name")
        item_quantity = data.get("quantity")
        item_expirydate = data.get("expirydate")
        item_prevstock = data.get("prevStock")
        
        if item_name and item_quantity:
            baked_collection.insert_one({
                "name": item_name,
                "quantity": item_quantity,
                "expiry_date": item_expirydate,
                "previous_stock":item_prevstock
            })

            return jsonify({"message": "Item added successfully!"}), 200
        else:
            return jsonify({"message": "Item name and quantity are required!"}), 400

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "Error adding item!"}), 500

def get_items_route():
    try:
        items = list(baked_collection.find())
        
        print(items)

        formatted_items = [{"name": item["name"],"expiry_date":item["expiry_date"],"quantity":item["quantity"],"previous_stock":item["previous_stock"]} for item in items]
        return jsonify(formatted_items), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "Error fetching items!"}), 500


def update_item(name):
    data = request.get_json()
    print(data)
    if not data:
        return jsonify({"message": "No data provided"}), 400
    updated_fields = {
        "name": data.get('name'),
        "quantity": data.get('quantity'),
        "expiry_date": data.get('expirydate'),
        "previous_stock": data.get('prevStock')
    }

    result = baked_collection.update_one(
        {"name": name}, 
        {"$set": updated_fields}
    )
    if result.matched_count > 0:
        return jsonify({"message": "Item updated successfully"}), 200
    else:
        return jsonify({"message": "Item not found"}), 404
    
def delete_item(name):
    result = baked_collection.delete_one({"name": name})
    if result.deleted_count > 0:
        return jsonify({"message": "Item deleted successfully"}), 200
    else:
        return jsonify({"message": "Item not found"}), 404
    