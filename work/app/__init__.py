from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, methods=["GET", "POST","PUT","DELETE"], supports_credentials=True)

class CustomException(Exception):
    def __init__(self, message):
        super().__init__(message)

@app.errorhandler(Exception)
def handle_custom_exception(error):
    print('--------Error--------\n', error, '\n---------------------')
    response = jsonify({'code':400, 'message': str(error)})
    response.status_code = 400
    return response

jwt = JWTManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database initialization
from app.models.models import *
with app.app_context():
    db.create_all()
    
# Register blueprints
from app.views import views_bp
app.register_blueprint(views_bp, url_prefix='')



