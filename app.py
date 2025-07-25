from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost/fusse_cafe')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

# Import models after db initialization
from models import Customer, Reservation, Newsletter, Table, MenuCategory, MenuItem, Admin

# Import and register blueprints
from routes.reservations import reservations_bp
from routes.newsletter import newsletter_bp
from routes.menu import menu_bp

app.register_blueprint(reservations_bp, url_prefix='/api')
app.register_blueprint(newsletter_bp, url_prefix='/api')
app.register_blueprint(menu_bp, url_prefix='/api')

@app.route('/')
def index():
    return {'message': 'Café Fausse API is running!', 'status': 'success'}

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'service': 'cafe-fausse-api'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 