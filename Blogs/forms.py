from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FloatField, BooleanField
from wtforms.validators import DataRequired, URL, NumberRange
from flask_ckeditor import CKEditorField


# form to create a Blog Post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("BLog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# form to register new user
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign me up!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let me in!")


class CommentForm(FlaskForm):
    input = StringField("Comment", validators=[DataRequired()])
    rating = FloatField("rating (0.0 to 5.0", validators=[NumberRange(min=0.0, max=5.0)])
    like = BooleanField("Like this post")
    submit = SubmitField("Send")
