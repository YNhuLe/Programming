from flask import Flask, render_template, request, url_for, redirect, flash, get_flashed_messages
import requests
from datetime import datetime, date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from flask_bootstrap import Bootstrap
from werkzeug.security import check_password_hash, generate_password_hash
from flask_ckeditor import CKEditor
import hashlib
from forms import RegisterForm, CreatePostForm, LoginForm, CommentForm
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user

from functools import wraps
from flask import abort
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = True
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
Bootstrap(app)
ckeditor = CKEditor(app)


# config the Database for 3 users, comments, blog_posts tables , "sqlite:///posts.db"
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
db = SQLAlchemy(model_class=Base)
db.init_app(app)
print(app.config['SQLALCHEMY_DATABASE_URI'])


# create User table for all registered users in database
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    # set the relationship between 2 database model( users and blog_posts) in the relationship 1-to-many
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")


# create BlogPost table in database
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # create foreign key, "users.id" referred from the User table
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    # Reference to the User object, the posts refers to the post property in the User class
    author = relationship("User", back_populates="posts")

    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    # one user can have many comments
    comments = relationship("Comment", back_populates="parent_post", cascade='all, delete-orphan')


# create Comment table in database
class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    posted_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    # Child relationship with the post
    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
    # one post can have many comments
    parent_post = relationship("BlogPost", back_populates="comments")


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
    try:

        result = db.session.execute(db.select(BlogPost))
        posts = result.scalars().all()
        return render_template("index.html", all_posts=posts, current_user=current_user)
    except Exception as error:
        return f"An error occurred: {error}"


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


# create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # if user is not 1 then return 403 error
        if current_user.id != 1:
            return abort(403)
        # otherwise, continue with the route function
        return f(*args, **kwargs)

    return decorated_function


# create commenter only for the
def only_commenter(f):
    @wraps(f)
    def check(*args, **kwargs):
        user = db.session.execute(db.select(Comment).where(Comment.author_id == current_user.id)).scalar()
        if not current_user.is_authenticated or current_user.id != user.author_id:
            return abort(403)
        return f(*args, **kwargs)

    return check


# only allow user who is the comment owner and authenticated to delete the comment
@app.route("/delete/comment/<int:comment_id>/<int:post_id>")
@only_commenter
def delete_comment(post_id, comment_id):
    comment_to_delete = db.get_or_404(Comment, comment_id)
    db.session.delete(comment_to_delete)
    db.session.commit()
    return redirect(url_for("show_post", post_id=post_id))


# add new post
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        # check the input from the form and the data from database

        existing_post = BlogPost.query.filter((BlogPost.title == form.title.data) |
                                              (BlogPost.subtitle == form.subtitle.data)).first()
        if existing_post:
            flash('The title or the subtitle is already exists. Please choose  different one.', "error")
            return redirect(url_for('add_new_post'))

        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_post"))
    return render_template("make_post.html", form=form, current_user=current_user)


# edit post based on the id
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=current_user,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make_post.html", form=edit_form, is_edit=True, current_user=current_user)


# fucntion to create Gravatar URL
def gravatar(email, size=50, default='monsterid', rating='g'):
    email_hash = hashlib.md5(email.strip().lower().encode('utf-8')).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d={default}&r={rating}"

# calculate the time different between the post and the comment
def cal_time_different(posted_time):
    current_time = datetime.now()
    time_diff = current_time - posted_time

    # get the days, hours, minute
    days = time_diff.days
    hours, remainder = divmod(time_diff.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    if days > 0:
        return f"{days}d"
    elif hours > 0:
        return f"{hours}h"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return "Just now"


# show post based on Post_Id, allow user to comment on the post
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    comment_form = CommentForm()

    # only allow logged-in users to comment
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to log in or register to comment.", "error")
            return redirect(url_for("login"))
        new_comment = Comment(
            text=comment_form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post,
            posted_time=datetime.now()
        )
        # data = cleanify(request.comment_form.get('ckeditor'))
        db.session.add(new_comment)
        db.session.commit()
        # clear the field after the submission
        comment_form.comment_text.data = ""
    comments = Comment.query.filter_by(post_id=post_id).all()
    the_time = []
    for comment_time in comments:
        print(comment_time.posted_time)
        time = cal_time_different(comment_time.posted_time)
        the_time.append(time)
        print(the_time)

        # add gravatar

    gravatar_url = {comment.comment_author.id: gravatar(comment.comment_author.email)
                    for comment in requested_post.comments}

    return render_template("post.html", post=requested_post,
                           current_user=current_user, form=comment_form, avatar=gravatar_url,
                           logged_in=current_user, posted_time=the_time)


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


# delete a post based on the post_id, prompt confirmation if any comments in the post
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)

    # if the post has comment
    if post_to_delete.comments:
        db.session.delete(post_to_delete)
        db.session.commit()
        return redirect(url_for("get_post"))
    db.session.delete(post_to_delete)
    db.session.commit()

    return redirect(url_for("get_post"))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_post'))


if __name__ == "__main__":
    app.run(debug=False, port=5000)
