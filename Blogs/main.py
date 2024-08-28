from flask import Flask, render_template, request
import requests
from datetime import datetime

posts = requests.get("https://api.npoint.io/ec9ee8e3ac7c9f469029").json()

app = Flask(__name__)
for post in posts:
    print(type(post))
    print(post)


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
    return render_template("response.html", name_data=name, email_data = email,
                           phone_data=phone, message_data=message)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = None
    for blog_post in posts:
        if blog_post["id"] == index:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
