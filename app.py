from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# Initialize app
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///superheroes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and Marshmallow
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Models

class Hero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    super_name = db.Column(db.String(100), nullable=False)
    hero_powers = db.relationship('HeroPower', backref='hero', cascade="all, delete-orphan")

class Power(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    hero_powers = db.relationship('HeroPower', backref='power', cascade="all, delete-orphan")

    @staticmethod
    def validate_description(description):
        if len(description) < 20:
            raise ValueError("Description must be at least 20 characters long")

class HeroPower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String(50), nullable=False)
    hero_id = db.Column(db.Integer, db.ForeignKey('hero.id'))
    power_id = db.Column(db.Integer, db.ForeignKey('power.id'))

    @staticmethod
    def validate_strength(strength):
        if strength not in ['Strong', 'Weak', 'Average']:
            raise ValueError("Strength must be 'Strong', 'Weak', or 'Average'")

# Schemas

class HeroSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Hero
        include_fk = True
        load_instance = True

class PowerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Power
        include_fk = True
        load_instance = True

class HeroPowerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = HeroPower
        include_fk = True
        load_instance = True

# Initialize schemas
hero_schema = HeroSchema()
heroes_schema = HeroSchema(many=True)
power_schema = PowerSchema()
powers_schema = PowerSchema(many=True)
hero_power_schema = HeroPowerSchema()
hero_powers_schema = HeroPowerSchema(many=True)

# Routes

# GET /heroes - Return a list of heroes
@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    return heroes_schema.jsonify(heroes)

# GET /heroes/:id - Return a hero and their powers by hero ID
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = Hero.query.get(id)
    if not hero:
        return jsonify({"error": "Hero not found"}), 404
    return hero_schema.jsonify(hero)

# GET /powers - Return a list of powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    return powers_schema.jsonify(powers)

# PATCH /powers/:id - Update power description
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({"error": "Power not found"}), 404
    new_description = request.json.get('description')
    if new_description:
        try:
            Power.validate_description(new_description)
            power.description = new_description
            db.session.commit()
            return power_schema.jsonify(power)
        except ValueError as e:
            return jsonify({"errors": [str(e)]}), 400
    return jsonify({"error": "Invalid request"}), 400

# POST /hero_powers - Create a hero power (assign power to hero)
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    strength = request.json.get('strength')
    hero_id = request.json.get('hero_id')
    power_id = request.json.get('power_id')

    if not strength or not hero_id or not power_id:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        HeroPower.validate_strength(strength)
        hero_power = HeroPower(strength=strength, hero_id=hero_id, power_id=power_id)
        db.session.add(hero_power)
        db.session.commit()
        return hero_power_schema.jsonify(hero_power), 201
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400

# Main function to run the app
if __name__ == '__main__':
    app.run(debug=True)
