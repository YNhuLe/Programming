# 📝 Flask Blog FunTime 🎉

Welcome to the Flask Blog FunTime project! This little app is all about fetching some awesome blog posts and displaying them in a stylish and elegant way. We’re using the magic of Flask, mixed with a dash of Python and a sprinkle of HTML. Let’s dive in, shall we? 🚀

## 🧐 What's this about?

Ever wanted to create a simple blog site without the hassle? Well, you're in the right place! This project pulls blog posts from an external API and displays them beautifully using Flask. Because who needs to write their own content when the internet is full of it, am I right? 😜

## 🛠️ How do I make it work?

Getting this baby up and running is as easy as pie 🥧. Just follow these steps:

1. **Clone the repo** 📥:
    ```bash
    git clone https://github.com/YNhuLe/flask-blog-funtime.git
    cd flask-blog-funtime
    ```

2. **Set up your conda environment** 🐍:
    ```bash
    conda env create -f environment.yml
    conda activate envname
    ```

3. **Install the dependencies** 📦:
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the app** 🏃‍♂️:
    ```bash
    python main.py
    ```

5. **Open your browser** 🌐 and head to:
    ```
    http://127.0.0.1:5000/
    ```
    Voilà! You should see your blog in all its glory! 🎉

## 📚 The Anatomy of This Masterpiece

- `app.py` - The heart of our application. It fetches the blog posts and routes them to the right places.
- `post.py` - A simple class to make handling our posts a breeze 🌬️.
- `templates/` - Where the HTML magic happens ✨. 
  - `index.html` - The homepage that lists all the blog posts.
  - `post.html` - The detailed page for each blog post.

## 🔮 API Details

We’re using the `npoint.io` API to grab the blog content. You can switch out the `blog_api` URL in `app.py` to point to your own API if you want to be fancy 🕺.

## 🙌 Contributing

Feel free to dive in! Open an issue or submit a PR. We love more ideas and feedback! 💡

## 🏅 Credits

- Flask, because it's lightweight and awesome. 🧙‍♂️
- Python, because we like to keep things snake-y. 🐍
- Emojis, because why not? 😎

## 📅 Developer 👩‍💻👩
[JennyLe]



**Happy Coding!** 🥳
