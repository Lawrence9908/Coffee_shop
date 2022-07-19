# from crypt import methods
import os
from turtle import tilt
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''

GET /drinks
    it should be a public endpoint
    it should contain only the drink.short() data representation
returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
    or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all();
    drink = [drink.short() for drink in drinks]

    return jsonify({
        "success": True,
        "drinks": drink
    }),200


'''

GET /drinks-detail
    it should require the 'get:drinks-detail' permission
    it should contain the drink.long() data representation
returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
    or appropriate status code indicating reason for failure
'''
@app.route('/drinks-details', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_details(payload):
    drinks_data = Drink.query.all()
    drinks = [drinks.short() for drinks in drinks_data]
    return jsonify({
        "success": True,
        "drinks":drinks
    }), 200

'''

POST /drinks
    it should create a new row in the drinks table
    it should require the 'post:drinks' permission
    it should contain the drink.long() data representation
returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
    or appropriate status code indicating reason for failure
'''
@app.route('/post:drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):
    drink_info = request.get_json()
    new_recipe = drink_info.get("recipe", None)
    new_title = drink_info.get("title", None)

    if new_recipe is None or new_title is None:
        abort(400)
    new_recipe = json.dumps(new_recipe)

    drink = None
    try:
        drink_data = Drink(
            recipe = new_recipe,
            title = new_title
        )
        drink_data.insert()
        drink = [drink_data.long()]
    except:
        abort(500)
    return jsonify({
        "success":True,
        "drinks": drink
    }), 200


'''

PATCH /drinks/<id>
    where <id> is the existing model id
    it should respond with a 404 error if <id> is not found
    it should update the corresponding row for <id>
    it should require the 'patch:drinks' permission
    it should contain the drink.long() data representation
returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
    or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>')
@requires_auth('patch:drinks')
def update_drink(payload, id):
    body = request.get_json()
    new_recipe = body.get("recipe",None)
    new_title = body.get("title", None)

    if new_recipe is None or new_title is None:
        abort(404)
    new_recipe=json.dumps(new_recipe)
    
    drink_data = Drink.query.get(id)
    if drink_data is None:
        abort(404)
    drink = None
    try:
        drink_data.recipe = new_recipe
        drink_data.title = new_title
        drink_data.update()
        drink = [drink_data.long()]
    except:
        abort(500)
    return jsonify({
        "success":True,
        "drinks": drink
    }), 200
    
'''
implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(patload, id):

    drink_to_delete = Drink.query.get(id)
    if drink_to_delete is None:
        abort(404)
    try:
        drink_to_delete.delete()
    except: 
        abort(500)
    return jsonify({
        "success": True,
        "drink": id,
    }), 200 

# Error Handling
'''
Example error handling for unprocessable entity
'''
# error handler for 500
@app.errorhandler(500)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500

# error handler for 404
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404

# error handler for 405
@app.errorhandler(405)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not Allowed"
    }), 405

# error handler for 400
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400

# error handler for 422
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Not Processable"
    }), 422

# error handler for 401
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": error.description
    }), 401




