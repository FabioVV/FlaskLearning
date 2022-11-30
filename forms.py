from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField, PasswordField, BooleanField, EmailField, ValidationError, TextAreaField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, equal_to, length
from flask_ckeditor import CKEditorField

# User Form
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    profile_pic = FileField("Profile Image")

    password_hash = PasswordField("Password",validators=[DataRequired(),equal_to('password_hash2', message='Password have to match!')])
    password_hash2 = PasswordField("Confirm password", validators=[DataRequired()])

    favorite_color = StringField("Favorite color")
    about = TextAreaField("About the author")

    submit = SubmitField("Submit")
#

# Create a Form Class
class NamerForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")
#

# Create Posts Class
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    #content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    content = CKEditorField('content', validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField('Submit')
#

# Create login Class
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField('Submit')
#

# Create search Class
class SearchForm(FlaskForm):
    searched = StringField("Username", validators=[DataRequired()])
    submit = SubmitField('Submit')
#