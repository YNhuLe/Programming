from flask import Flask, render_template, request, url_for, redirect
import requests
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_bootstrap5 import Bootstrap
from werkzeug.security import check_password_hash, generate_password_hash

from forms import RegisterForm, CreatePostForm, LoginForm
from flask_login import UserMixin, LoginManager, login_user

posts = requests.get("https://api.npoint.io/6fa2a608d6fc9a520b1a").json()

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'lenhuy1996'
Bootstrap(app)


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# create User table for all registered users in database
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))


with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)


# retrieve validated users from database or call error
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('get_posts'))

    return render_template("login.html", form=form)


@app.context_processor
def inject_year():
    return {'currentYear': datetime.now().year}


@app.route('/')
def get_post():
    return render_template("index.html", all_posts=posts)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/form-entry", methods=['POST'])
def receive_data():
    name = request.form['user-name']
    email = request.form['user-email']
    phone = request.form['user-phone']
    message = request.form['user-message']
    return render_template("response.html", name_data=name, email_data=email,
                           phone_data=phone, message_data=message)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = None
    for blog_post in posts:
        if blog_post["id"] == index:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hash_and_salted_password = generate_password_hash(form.password.data, method='pbkdf2:sha256',
                                                          salt_length=8)
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('get_post'))
    return render_template("register.html", form=form)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
