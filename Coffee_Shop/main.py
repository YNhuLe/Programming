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
    submit = SubmitField('submit')


@app.route('/')
def home():
    return render_template("index.html")


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
