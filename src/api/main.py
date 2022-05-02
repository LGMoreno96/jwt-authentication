
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_jwt_extended  import JWTManager,create_access_token, get_jwt_identity, jwt_required
from flask_cors import CORS
from sqlalchemy import true
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User



app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY']= os.environ.get('FLASK_API_KEY')
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

jwt=JWTManager(app)


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "GET /user response "
    }

    return jsonify(response_body), 200


@app.route('/signup', methods=['POST'])
def create_user():
    body=request.json
    user=User.create(
        name=body["name"],
        email=body["email"],
        password=body["password"]
    )
    if user is not None:
        db.session.add(user)
        try:
            db.session.commit()
            return jsonify(user.serialize()),201
        except Exception as error:  
            db.session.rollback()
            return jsonify({
                "msg":"An error occurred while trying to record data"
            }),500
    else:
        return jsonify({"msg":"Info is incorrect, please check"}),400



@app.route('/token', methods=['POST'])
def handle_token():

    body = request.json

    email = body['email']
    password = body['password']
    
    user = User.query.filter_by( email = email).one_or_none()
    if user is None:
        return jsonify({
            'msj': 'Invalid user'
        }),400

    if password != user.password:

        return jsonify({
            'msj': 'Bad Request'
        }),400

    access_token = create_access_token(identity = user.id)

    return jsonify(
        {'token': access_token,
        'user': user.serialize()
        }
    ),201

@app.route('/protected', methods=["GET"])
@jwt_required()
def handle_protegido():
    user_id = get_jwt_identity()
    return jsonify(
        {
            'user_id':user_id
        }
    ),200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=PORT, debug=False)