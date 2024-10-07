from flask import Flask,render_template
from controllers.rawmaterials import add_items_route, get_items_route
from routes.rawroutues import item_bp
from database.database import DBConfig
from flask_cors import CORS

#initialize flask app
app = Flask(__name__)
# Enable CORS for the application
CORS(app)
DBConfig()

# Register the blueprint
app.register_blueprint(item_bp)

# Route to render the main HTML page
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)