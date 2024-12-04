from flask import Flask, render_template, request, url_for, redirect, flash, get_flashed_messages
import requests
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_bootstrap import Bootstrap
from werkzeug.security import check_password_hash, generate_password_hash
from flask_ckeditor import CKEditor

from forms import RegisterForm, CreatePostForm, LoginForm
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user

# posts = requests.get("https://api.npoint.io/6fa2a608d6fc9a520b1a").json()

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'lenhuy1996'
Bootstrap(app)
ckeditor=CKEditor(app)


class Base(DeclarativeBase):
    pass


# config the User table
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
# config the BLogPost table
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
# config the User table
# app.config['SQLALCHEMY_BINDS'] = {
#     'users': 'sqlite:///users.db',
#     'posts': 'sqlite:///posts.db'
# }

db = SQLAlchemy(model_class=Base)
db.init_app(app)


# create User table for all registered users in database
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))


# create BlogPost table in database
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


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

        # if email does not exist
        if not user:
            flash("This email does not exist.Please try again!", "warning")
            print('not email')
            return redirect(url_for('login'))

        # if password incorrect
        elif not check_password_hash(user.password, password):
            flash("Password incorrect, please try again!", "warning")
            print('not pw')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_post'))
    print("Login page")
    return render_template("login.html", form=form, current_user=current_user)


@app.context_processor
def inject_year():
    return {'currentYear': datetime.now().year}


# show all the posts
@app.route('/')
def get_post():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    print("exist")
    return render_template("index.html", all_posts=posts, current_user=current_user
                           )


@app.route("/about")
def about():
    print("about page")
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html", current_user=current_user)


@app.route("/form-entry", methods=['POST'])
def receive_data():
    name = request.form['user-name']
    email = request.form['user-email']
    phone = request.form['user-phone']
    message = request.form['user-message']
    return render_template("response.html", name_data=name, email_data=email,
                           phone_data=phone, message_data=message)


# add new post
@app.route("/new-post", methods=["GET", "POST"])
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user.name,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_post"))
    return render_template("make_post.html", form=form, current_user=current_user)


# edit post based on the id
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user.name
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make_post.html", form=edit_form, is_edit=True, current_user=current_user)


# show post based on Post_Id
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post, current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # check if the use email exist in the database
        email = form.email.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if user:
            # user already exist in the database, then redirect to the login page
            flash("You've already signed up with this email! Sign in instead!")
            return redirect(url_for('login'))

        # generate hashed password
        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # authenticate user with Flask-login
        login_user(new_user)
        return redirect(url_for('get_post'))
    return render_template("register.html", form=form, current_user=current_user)


# delete a post based on the post_id
@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for("get_post"))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_post'))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
