from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from dotenv import load_dotenv
import random, os

load_dotenv()
app = Flask(__name__)

VERIFIER = os.environ["VERIFIER"]
# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    # function for Converting DB data to dictionary to be used as json data
    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

with app.app_context():
    db.create_all()

TRUTHY = {"1", "true", "yes", "on"}
def form_bool(field: str) -> bool:
    return request.form.get(field, "").strip().lower() in TRUTHY

@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)
    # body = {"cafe":{
    #     "id" : random_cafe.id,
    #     "name" : random_cafe.name,
    #     "map_url" : random_cafe.map_url,
    #     "img_url" : random_cafe.img_url,
    #     "location" : random_cafe.location,
    #     "seats" : random_cafe.seats,
    #     "has_toilet" : random_cafe.has_toilet,
    #     "has_wifi" : random_cafe.has_wifi,
    #     "has_sockets" : random_cafe.has_sockets,
    #     "can_take_calls" : random_cafe.can_take_calls,
    #     "coffee_price" : random_cafe.coffee_price
    # }}
    # return jsonify(body)
    return jsonify(cafe=random_cafe.to_dict())

@app.route("/all")
def get_all_cafes():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()
    return jsonify(cafe=[cafe.to_dict() for cafe in all_cafes])

@app.route("/search")
def search_cafe():
    location = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location==location))
    all_cafes = result.scalars().all()
    return jsonify(cafe=[cafe.to_dict() for cafe in all_cafes])


# HTTP POST - Create Record
@app.route("/suggest", methods=["POST"])
def add_cafe():
    new_cafe = Cafe(
        name = request.form.get("name"),
        map_url = request.form.get("map_url"),
        img_url = request.form.get("img_url"),
        location = request.form.get("location"),
        seats = request.form.get("seats"),
        has_toilet = form_bool("has_toilet"),
        has_wifi = form_bool("has_wifi"),
        has_sockets = form_bool("has_sockets"),
        can_take_calls = form_bool("can_take_calls"),
        coffee_price = request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})
# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"]) #ID = 22
def update_coffee_price(cafe_id):
    new_price = request.args.get("coffee_price")
    try:
        cafe = db.session.get(Cafe, cafe_id)
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200
    except:
        return jsonify(error={'Not found': 'Sorry a cafe with that id was not found in the database.'}), 404

# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    user_key = request.args.get("api-key")
    if VERIFIER == user_key:
        try:
            cafe = db.get_or_404(Cafe, cafe_id)
        except:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
        else:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully reported the cafe as closed."}), 200
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the right api_key."}), 403

if __name__ == '__main__':
    app.run(debug=True)
