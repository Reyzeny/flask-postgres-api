from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from flask_cors import CORS
import json
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'crud.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pelumi:pelumi@localhost:5432/db1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["DEBUG"] = True
db = SQLAlchemy(app)
ma = Marshmallow(app)
#CORS(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    def __init__(self, username, email):
        self.username = username
        self.email = email
class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('username', 'email')
user_schema = UserSchema()
users_schema = UserSchema(many=True)

class ProductBanner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(80), unique=True)
    def __init__(self, image_name):
        self.image_name = image_name
class ProductBannerSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'image_name')
product_banner_schema = ProductBannerSchema()
product_banners_schema = ProductBannerSchema(many=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(600), unique=False)
    price = db.Column(db.Float)
    discount = db.Column(db.Boolean, default=False)
    discounted_product = db.relationship('DiscountedProduct', backref=db.backref('products', lazy=True))
    no_of_views = db.Column(db.Integer)
    no_of_purchases = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    def __init__(self, name, price, discount=False, no_of_views=0, no_of_purchases=0):
        self.name = name
        self.price = price
        self.discount = discount
        self.no_of_views = no_of_views
        self.no_of_purchases = no_of_purchases
class ProductSchema(ma.Schema):
    class Meta:
        #Fields to expose
        fields = ('id', 'name', 'price', 'discount', 'no_of_views', 'no_of_purchases', 'created_at', 'updated_at')
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
    




class DiscountedProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    discount_percentage = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def __init__(self, product_id, discount_percentage):
        self.product_id = product_id
        self.discount_percentage = discount_percentage
class DiscountedProductSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'product_id', 'discount_percentage', 'created_at')
discounted_product_schema = DiscountedProductSchema()
discounted_products_schema = DiscountedProductSchema(many=True)



db.create_all()














# endpoint to create new user
@app.route("/user", methods=["POST"])
def add_user():
    print(request)
    username = request.json['username']
    email = request.json['email']
    
    
    new_user = User(username, email)

    db.session.add(new_user)
    db.session.commit()

    #result = users_schema.dump(new_user)

    #return jsonify(result.data)
    return json.dumps(new_user.__dict__)


# endpoint to show all users
@app.route("/user", methods=["GET"])
def get_user():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result.data)


# endpoint to get user detail by id
@app.route("/user/<id>", methods=["GET"])
def user_detail(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)










# endpoint to create new product_banner
@app.route("/product_banner", methods=["POST"])
def add_product_banner():
    image_name = request.json['image_name']
    
    new_product_banner = ProductBanner(image_name)

    db.session.add(new_product_banner)
    db.session.commit()

    return jsonify(new_product_banner)


# endpoint to show all product_banners
@app.route("/product_banner", methods=["GET"])
def get_product_banner():
    all_product_banners = ProductBanner.query.all()
    result = product_banners_schema.dump(all_product_banners)
    return jsonify(result.data)


# endpoint to get product_banner detail by id
@app.route("/product_banner/<id>", methods=["GET"])
def product_banner_detail(id):
    product_banner = ProductBanner.query.get(id)
    return product_banner_schema.jsonify(product_banner)














# endpoint to add products
@app.route("/add_product", methods=["POST"])
def add_product():
    name = request.json["name"]
    price = request.json["price"]
    discount = request.json["is_discounted"]
    no_of_views = request.json["no_of_views"]
    no_of_purchases = request.json["no_of_purchases"]
    
    current_product = Product(name, price, discount, no_of_views, no_of_purchases)
    db.session.add(current_product)
    db.session.flush()
    if (discount==True):
        product_id = current_product.id
        discount_percentage = request.json["discount_percentage"]
        discounted_product = DiscountedProduct(product_id=product_id, discount_percentage=discount_percentage)
        db.session.add(discounted_product)
        db.session.flush()
    db.session.commit()
    return "success"




# endpoint to show all top products
@app.route("/top_products", methods=["GET"])
def get_top_products():
    top_products = Product.query.order_by(Product.no_of_views).all()
    result = products_schema.dump(top_products)
    return jsonify(result.data)


if __name__ == '__main__':
    app.run(debug=True)