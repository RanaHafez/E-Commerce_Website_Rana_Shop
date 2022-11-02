import flask_login
from flask import Flask, url_for, request, render_template, redirect, flash
from flask_login import LoginManager, login_user, UserMixin, logout_user, login_required
from forms import *
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import stripe
import os
from items import *

domain = "http://127.0.0.1:5000/"
stripe.api_key = os.environ['STRIPE_API_KEY']
app = Flask(__name__)

# this is needed for forms and db
app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rana_shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# login manager and initialize the app
login_manager = LoginManager()
login_manager.init_app(app=app)

method="pbkdf2:sha256"
salt_length=8


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tabelname__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    password = db.Column(db.String(100))
    items = db.relationship("CartItem", backref="user")


class CartItem(db.Model):
    __tabelname__ = 'cartItems'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price_id = db.Column(db.String(500), nullable=False)
    image = db.Column(db.String(500), nullable=False)
    name = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    is_purchased = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

db.create_all()


@app.route("/")
def home():
    return render_template("index.html", books=books)


@app.route("/login", methods=["POST", "GET"])
def login():
    login_form = LoginForm()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # check if there is no user.
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Sorry, You need to register first .. ")
            return redirect(url_for("register"))

        # check if the password does not match
        if not check_password_hash(user.password, password):
            # if they are not equal
            flash("Incorrect password, Try Again")
            return redirect((url_for("login")))

        login_user(user)
        return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    register_form = RegisterForm()
    if request.method == "POST":
        print("POST")
        name = request.form.get("name")
        email = request.form.get("email")
        print(name)
        print(email)
        # check if the user exists before
        user = User.query.filter_by(email=email).first()
        if user:
            flash(f"Hello {name}, You are already register please login instead")
            return redirect(url_for("login"))
        else:
            print("There is not user ... ")
            new_user = User(
                name=name,
                email=email,
                password=generate_password_hash(password=request.form.get("password"), method=method, salt_length=salt_length)
            )
            db.session.add(new_user)
            db.session.commit()
            # login_user(new_user)
            return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


def get_cart_items():
    return CartItem.query.filter_by(user_id=flask_login.current_user.id, is_purchased=int(False)).all()


@app.route("/get-cart")
@login_required
def get_cart():
    items = get_cart_items()
    print(items)
    return render_template("cart.html", cart_items=items)


@login_required
@app.route("/delete/<int:id>")
def delete(id):
    book_to_delete = CartItem.query.get(id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for("get_cart"))



@app.route("/add-cart/<book>", methods=["POST","GET"])
# @login_required
def add_cart(book):
    print(request.form.get("quantity"))
    if flask_login.current_user.is_authenticated:
        if request.method == "POST":
            for item in books:
                if item["name"] == book:
                    b = item
            print(b)
            item = CartItem(
                price_id=b["price_id"],
                quantity=request.form.get("quantity"),
                image=b["image"],
                name=b["name"],
                description=b["description"],
                is_purchased=int(False),
                user_id=flask_login.current_user.id
            )
            db.session.add(item)
            db.session.commit()
            return redirect(url_for("get_cart"))

    flash("Before You Add to Cart, Please Login to your account .. ")
    return redirect(url_for("login"))


@app.route("/secret")
@login_required
def secret_page():
    return render_template("cart.html")


@app.route("/create-checkout-session", methods=["POST","GET"])
@login_required
def checkout():
    print(request.args)
    items = get_cart_items()
    line_items = [{"price": item.price_id, "quantity": item.quantity} for item in items]
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode="payment",
            success_url=f"{domain}success",
            cancel_url=f"{domain}fail"
        )

    except Exception as e:
        return str(e)
    return redirect(checkout_session.url, code=303)


@app.route("/success")
def success():
    items = CartItem.query.filter_by(user_id=flask_login.current_user.id).delete()
    db.session.commit()
    return render_template("success.html")


@app.route("/fail")
def fail():
    return render_template("fail.html")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
