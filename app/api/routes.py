from flask import Blueprint, request, jsonify
from app.helpers import token_required
from app.models import db, Car, car_schema, cars_schema

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/cars', methods=['POST'])
@token_required
def create_car(current_user_token):
    cars_data = request.get_json()
    if isinstance(cars_data, list):
        cars = []
        for car_data in cars_data:
            make = car_data['make']
            model = car_data['model']
            year = car_data['year']
            price = car_data['price']
            user_token = current_user_token.token
            car = Car(make=make, model=model, year=year, price=price, user_token=user_token)
            db.session.add(car)
            cars.append(car)
        db.session.commit()
        response = cars_schema.dump(cars)
        return jsonify(response), 201
    else:
        return jsonify({'message': 'Invalid data format, expected a list of cars'}), 400


@api.route('/cars', methods=['GET'])
@token_required
def get_cars(current_user_token):
    cars = Car.query.filter_by(user_token=current_user_token.token).all()
    response = cars_schema.dump(cars)
    return jsonify(response)

@api.route('/cars/<id>', methods=['GET'])
@token_required
def get_single_car(current_user_token, id):
    car = Car.query.get(id)
    response = car_schema.dump(car)
    return jsonify(response)

@api.route('/cars/<id>', methods=['PUT'])
@token_required
def update_car(current_user_token, id):
    print(f'Updating car with ID: {id}')
    car = Car.query.get(id)
    if car:
        data = request.get_json()
        if not all(k in data for k in ('make', 'model', 'year', 'price')):
            return jsonify({'message': 'Missing data'}), 400

        print(f'Car found: {car}')
        car.make = data['make']
        car.model = data['model']
        car.year = data['year']
        car.price = data['price']
        db.session.commit()
        response = car_schema.dump(car)
        return jsonify(response), 200
    else:
        print('Car not found')
        return jsonify({'message': 'Car not found'}), 404

@api.route('/cars/<id>', methods=['DELETE'])
@token_required
def delete_car(current_user_token, id):
    car = Car.query.get(id)
    if car:
        if car.user_token != current_user_token.token:
            return jsonify({'message': 'Unauthorized to delete this car'}), 403
        
        db.session.delete(car)
        db.session.commit()
        return jsonify({'message': 'Car deleted successfully'}), 200
    else:
        return jsonify({'message': 'Car not found'}), 404
