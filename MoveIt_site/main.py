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
moving_types = [
    "Local Moving",
    "Long Distance Moving",
    "Residential Moving",
    "Commercial Moving",
    "Packing and Unpacking Services",
    "Furniture Disassembly and Assembly",
    "Specialty Moving (Pianos, Antiques, etc.)",
    "International Moving",
    "Storage Services",
    "Full-Service Moving",
    "Partial Moving Services",
    "Corporate Relocation"
]

@app.route('/quote')
def get_quote():
    return render_template("quote.html", provinces=province_list, type_list=moving_types)

if __name__== "__main__":
    app.run(debug=True)
