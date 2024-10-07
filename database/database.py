from pymongo import MongoClient


# Function to configure and return the MongoDB collection
def DBConfig():
    # Establish MongoDB connection
    client = MongoClient("mongodb+srv://saidivya:saidivya1234@inventory.xp13j.mongodb.net/?retryWrites=true&w=majority&appName=Inventory")
    
    # Define the database
    db = client['Inventory']  
    
    # Initialize the collection
    # inventory_collection = db['rawmaterials']
    # baked_collection = db['bakedmaterials']
    
    
    print("Database is connected")
    return db   # Return the collection to use it elsewhere


