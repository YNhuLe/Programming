import datetime
from flask import Flask, render_template
import requests
from post import Post


blog_api = 'https://api.npoint.io/ec9ee8e3ac7c9f469029'
response = requests.get(blog_api)
posts_data = response.json()
year = datetime.datetime.now().year

all_posts = []
for post in posts_data:
    post_obj = Post(post["id"], post["title"], post["subtitle"], post["body"])
    all_posts.append(post_obj)


app = Flask(__name__)

@app.route('/')
def get_post():
    return render_template("index.html", posts=all_posts, y=year)


@app.route('/post/<int:index>')
def show_post(index):
    requested_post = None
    for blog_post in all_posts:
        if blog_post.id == index:
            requested_post = blog_post
    return render_template('post.html', y=year, post=requested_post)


if __name__ == "__main__":
    app.run(debug=True)
