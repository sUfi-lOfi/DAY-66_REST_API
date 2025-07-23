from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from sqlalchemy import func

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
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
    def to_dict(self):
        return {c.name : getattr(self,c.name) for c in self.__table__.columns }


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")




# HTTP GET - Read Record
@app.route("/random")
def random_cafe():
    cafe = db.session.execute(db.select(Cafe).order_by(func.random()).limit(1)).scalars().first()
    return jsonify(cafe.to_dict())
@app.route("/all")
def all_cafe():
    cafes = db.session.execute(db.select(Cafe)).scalars().all()
    cafes = [cafe.to_dict() for cafe in cafes]
    return jsonify(cafes)

@app.route("/search")
def particular_cafe():
    location = request.args.get("location")
    search = db.session.execute(db.select(Cafe).where(Cafe.location == location)).scalars().all()
    cafes = [cafe.to_dict() for cafe in search]
    if cafes:
        return jsonify(cafes)
    else:
        return jsonify({'error':"Cafe not found in that location"}) , 404
# HTTP POST - Create Record
@app.route('/add',methods=["POST"])
def add_cafe():
    data = request.get_json()
    allowed_fields = {
        "name", "map_url", "img_url", "location", "seats",
        "has_toilet", "has_wifi", "has_sockets", "can_take_calls", "coffee_price"
    }

    filtered_data = {key: value for key, value in data.items() if key in allowed_fields}
    try:
        cafe = Cafe(**filtered_data)
        db.session.add(cafe)
        db.session.commit()
        return {"success":"Cafe successfully added"}, 200
    except:
        return {"error":"Check all field names and their data types"}, 404
# HTTP PUT/PATCH - Update Record
@app.route("/update/<int:cafe_id>",methods=["PUT"])
def update(cafe_id):
    allowed_fields = {
        "name", "map_url", "img_url", "location", "seats",
        "has_toilet", "has_wifi", "has_sockets", "can_take_calls", "coffee_price"
    }
    data = request.get_json()
    filtered_data = {key:value for key,value in data.items() if key in allowed_fields}
    cafe = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
    if not cafe:
        return {"error","Cafe not found"} , 404
    else:
        try :
            for key,value in filtered_data.items():
                setattr(cafe,key,value)
            db.session.commit()
        except:
            return {"error":"Check the fields again"}, 404
        else:
            return {"Success": "Cafe updated!"}, 200



# HTTP DELETE - Delete Record
@app.route("/delete/<int:cafe_id>",methods = ["DELETE"])
def delete_cafe(cafe_id):
    if request.args.get("api_key") == "api_key":
        cafe_to_delete = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify({"Success" : "Cafe Delete"}) , 200
        else:
            return {"error":"No cafe found"}
    else:
        return {"error":"Enter valid credentials"} ,300
if __name__ == '__main__':
    app.run(debug=True)
