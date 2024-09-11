from flask import Flask, render_template, url_for, redirect
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Jennyle'
Bootstrap5(app)


class CafeForm(FlaskForm):
    cafe = StringField('Cafe name', validators=[DataRequired()])
    location = StringField("cafe location on Google map", validators=[DataRequired(), URL()])
    open = StringField("Opening hour", validators=[DataRequired()])
    close = StringField("Closing hour", validators=[DataRequired()])
    coffee_rating = SelectField("Coffee Rating", validators=[DataRequired()],
                                choices=["☕️", "☕☕", "☕☕☕", "☕☕☕☕", "☕☕☕☕☕"])
    power_rating = SelectField("Power Rating", validators=[DataRequired()],
                               choices=["✘", "💪", "💪💪", "💪💪💪", "💪💪💪💪", "💪💪💪💪💪"])
    wifi_rating = SelectField("Wifi rating", validators=[DataRequired()],
                              choices=["✘", "🔌", "🔌🔌", "🔌🔌🔌", "🔌🔌🔌🔌", "🔌🔌🔌🔌🔌"])
    submit = SubmitField('submit')


@app.route('/')
def home():
    return render_template("index.html")


@app.route("/add", methods=["GET", "POST"])
def add_cafes():
    form = CafeForm()
    if form.validate_on_submit():
        with open("cafe-data.csv", mode="a", encoding="utf-8") as csv_file:
            csv_file.write(f"\n{form.cafe.data},"
                           f"{form.location.data},"
                           f"{form.open.data},"
                           f"{form.close.data},"
                           f"{form.coffee_rating.data},"
                           f"{form.wifi_rating.data},"
                           f"{form.power_rating.data}")
        return redirect(url_for("cafes_list"))
    return render_template("add.html", form=form)


@app.route('/cafes')
# open the cafe-data.csv file, rea through it and add them to list_of_rows List
def cafes_list():
    with open('cafe-data.csv', newline='', encoding='utf-8') as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        list_of_rows = []
        for row in csv_data:
            list_of_rows.append(row)
            print(list_of_rows[0])
    # render the cafes.html wit the cafe-data from the csv file
    return render_template('cafes.html', cafes=list_of_rows)


if __name__ == '__main__':
    app.run(debug=True)
