from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/random')
def random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(random_cafe.to_dict())

@app.route('/all')
def all_cafes():
    cafes = db.session.query(Cafe).all()

    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


## HTTP GET - Read Record
@app.route('/search')
def search_cafes():
    location = request.args.get('loc')
    cafe = db.session.query(Cafe).filter_by(location=location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={'not found': 'none location'})



## HTTP POST - Create Record
@app.route('/add', methods=['POST', 'GET'])
def add():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})

## HTTP PUT/PATCH - Update Record
@app.route('/update_price/<cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    cafe = db.session.query(Cafe).filter_by(id=cafe_id).first()
    new_price = request.form.get('new_price')
    cafe.coffee_price = new_price
    db.session.commit()
    return jsonify(response={'success': 'Coffee price updated'})

## HTTP DELETE - Delete Record
@app.route('/report-closed/<cafe_id>', methods=['DELETE'])
def cafe_closed(cafe_id):
    key = request.args.get('api-key')
    if key == 'MyKey':
        cafe = db.session.query(Cafe).filter_by(id=cafe_id).first()
        db.session.delete(cafe)
        db.session.commit()
        return jsonify(response={'success': 'the cafe has been deleted'})
    else:
        return jsonify(response={'error': 'you are not authorized to delete cafes'})


if __name__ == '__main__':
    app.run(debug=True)
