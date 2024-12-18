import datetime

from flask import Flask, render_template, url_for, request, redirect, flash, jsonify, abort
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, Float, String
from flask_bootstrap import Bootstrap5
from wtforms import StringField, FloatField
from wtforms.validators import DataRequired
from Book_Shelf.config import SECRET

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = True

app.config['SECRET_KEY'] = SECRET

bootstrap = Bootstrap5(app)


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///book_collect.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class AddForm(FlaskForm):
    title = StringField(label='Book Name: ', validators=[DataRequired()])
    author = StringField(label='Book Author: ', validators=[DataRequired()])
    rating = FloatField(label='Rating: ', validators=[DataRequired()])
    image = StringField(validators=[DataRequired()])
    shop = StringField(validators=[DataRequired()])


class UpdateForm(FlaskForm):
    rating = FloatField(label='Rating: ', validators=[DataRequired()])


# create the table schema
class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    image: Mapped[str] = mapped_column(String(500), nullable=False)
    shop: Mapped[str] = mapped_column(String(500), nullable=False)


# initialise the database table
with app.app_context():
    db.create_all()

year = datetime.datetime.now().year


@app.route("/")
def home():
    result = db.session.execute(db.select(Book).order_by(Book.title))
    all_books = result.scalars().all()
    return render_template("index.html", books=all_books, year=year)


# add book into the bookshelf
@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddForm()

    if request.method == "POST" and form.validate_on_submit():
        new_book = Book(
            title=form.title.data,
            author=form.author.data,
            rating=form.rating.data,
            image=form.image.data,
            shop=form.shop.data

        )
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('home'))
    else:
        print(form.errors)
        flash('Error: Please correct the error in the form.', 'danger')
    return render_template('add.html', add_form=form)


# find, and update rating base on the id
@app.route('/edit', methods=["GET", "POST"])
def edit():
    form = UpdateForm()
    if request.method == "POST" and form.validate_on_submit():
        book_id = request.form['id']
        book_to_update = db.get_or_404(Book, book_id)
        book_to_update.rating = request.form['rating']
        db.session.commit()
        return redirect(url_for('home'))
    book_id = request.args.get('id')  # retrieve query parameter named 'id' from the URL
    book_selected = db.get_or_404(Book, book_id)
    return render_template("edit.html", book=book_selected, edit_form=form, year=year)


# route to shop the book
@app.route('/shop')
def shop():
    book_id = request.args.get('id')
    book_to_shop = db.get_or_404(Book, book_id)
    if not book_id:
        abort(400, description="Book ID is required")

    return jsonify({
        'id': book_to_shop.id,
        'name': book_to_shop.title,
        'author': book_to_shop.author,
        'shop': book_to_shop.shop
    })


@app.route('/delete')
def delete():
    book_id = request.args.get('id')
    book_to_delete = db.get_or_404(Book, book_id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


# add the about page and subscription
@app.route('/aboutUs')
def about():
    return render_template("aboutUs.html", year=year)


if __name__ == "__main__":
    app.run(debug=True)
