from flask import Blueprint
from controllers.bakedmaterials import add_items_route, get_items_route,request,jsonify
from database.database import DBConfig

# Define a Blueprint for item-related routes
item_baked_bp = Blueprint('item_baked_bp', __name__)
baked_collection = DBConfig('bakedmaterials')
# Route for adding items
@item_baked_bp.route('/add_items', methods=['POST'])
def add_items():
    return add_items_route()

# Route for getting items
@item_baked_bp.route('/get_items', methods=['GET'])
def get_items():
    return get_items_route()



@item_baked_bp.route("/update_item/<string:name>", methods=['PUT'])
def update_item_route(name):
    data = request.get_json()
    print("Name:", name)
    print("Data:", data)

    if not data:
        return jsonify({"message": "No data provided"}), 400

    updated_fields = {
        "name": data.get('name'),
        "quantity": data.get('quantity'),
        "expiry_date": data.get('expirydate'),
        "Prepared_date" : data.get('prepdate'),
        "doneby" : data.get('donyby')
    }

    result = baked_collection.update_one(
        {"name": name}, 
        {"$set": updated_fields}
    )

    if result.matched_count > 0:
        return jsonify({"message": "Item updated successfully"}), 200
    else:
        return jsonify({"message": "Item not found"}), 404
    

@item_baked_bp.route("/delete_item/<string:name>", methods=['DELETE'])
def delete_item_route(name):
    result = baked_collection.delete_one({"name": name})
    if result.deleted_count > 0:
        return jsonify({"message": "Item deleted successfully"}), 200
    else:
        return jsonify({"message": "Item not found"}), 404
    