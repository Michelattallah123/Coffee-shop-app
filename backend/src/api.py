import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

## ROUTES

@app.route('/drinks')
def get_drinks():  
    drinks = Drink.query.all()
    drinks = [drink.short() for drink in drinks]

    return jsonify({'success': True, 'drinks':drinks}), 200

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):  
    drinks = Drink.query.all()
    drinks = [drink.long() for drink in drinks] 
    return jsonify({'success': True, 'drinks':drinks}), 200



@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(payload):
    body = request.get_json()
    recipe = body.get('recipe', None)
    title = body.get('title', None)
    drink = Drink(title=title,recipe=json.dumps(recipe))
    Drink.insert(drink)
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 201



@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload,id):
        data = request.get_json()
        title = data.get('title', None)
        recipe = data.get('recipe', None)
        drink = Drink.query.filter_by(id=id).one_or_none()
        if drink is None:
            abort(404)
        drink.title = title
        drink.recipe = json.dumps(recipe)
        drink.update()
        drink = Drink.query.filter_by(id=id).one_or_none()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })


    


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
        drink = Drink.query.filter_by(id=id).one_or_none()
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({
            'success': True,
            'deleted': drink_id
        })



## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "Unprocessable"
                    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    
    }), 404

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'Unauthorized'
    } , 401)

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method not allowed'
    }, 405)

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error'
    }, 500)
