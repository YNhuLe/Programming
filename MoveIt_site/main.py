from flask import Flask, render_template
import datetime



app = Flask(__name__)

year = datetime.datetime.now().year
@app.route('/')
def home():
    return render_template("index.html", y=year)

province_list = [
    "Alberta",
    "British Columbia",
    "Manitoba",
    "New Brunswick",
    "Newfoundland and Labrador",
    "Nova Scotia",
    "Ontario",
    "Prince Edward Island",
    "Quebec",
    "Saskatchewan"
]
@app.route('/quote')
def get_quote():
    return render_template("quote.html", provinces=province_list)

if __name__== "__main__":
    app.run(debug=True)
