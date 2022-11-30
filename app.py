from flask import (Flask, flash, redirect, render_template, request, session,url_for)
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, EmailField, ValidationError
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, equal_to, length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date


app = Flask(__name__)
app.secret_key = "supersecretkey"
#SQLITE database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:guerra998@localhost/users'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Blog post model creation
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(50))
    content = db.Column(db.Text)
    author = db.Column(db.String(75))
    slug = db.Column(db.String(100))
    date_posted = db.Column(db.DateTime, default = datetime.utcnow)
#

# User Model creation
class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique = True)
    favorite_color = db.Column(db.String(120))
    password_hash = db.Column(db.String(128))
    date_added = db.Column(db.DateTime, default = datetime.utcnow)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return '<Name %r>' % self.name
#


# User Form
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])

    password_hash = PasswordField("Password",validators=[DataRequired(),equal_to('password_hash2', message='Password have to match!')])
    password_hash2 = PasswordField("Confirm password", validators=[DataRequired()])

    favorite_color = StringField("Favorite color")

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
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField('Submit')
#

#JSON
@app.route('/date')
def getdate():
    return {"Date": date.today()}
#


## ROUTES AND CONTROLLERS BELlOW


#Home page
@app.route('/')
def index():
    return render_template("index.html")
#

#Name page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form submitted Succesfully!")
    return render_template('name.html',name = name, form = form)
#

#Add user
@app.route('/user/add', methods=['GET','POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email = form.email.data).first()
        if user is None:
            hashedpasswd = generate_password_hash(form.password_hash.data, 'sha256')
            user = Users(name = form.name.data, 
            email = form.email.data, 
            password_hash = hashedpasswd, 
            favorite_color = form.favorite_color.data)

            db.session.add(user)
            db.session.commit()

        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.email.favorite_color = ''
        form.password_hash = ''
        flash("User created!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html",form = form, name = name, our_users = our_users)
#

#Update user
@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id:int):
    form = UserForm()
    newname = Users.query.get_or_404(id)
    if request.method == "POST":
        #DIFFERENT WAY OF GETTING THE FORM DATA
        newname.name = request.form['name']
        newname.email = request.form['email']
        newname.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash("User updated successfully!")
            return render_template("update_user.html",form = form, newname = newname)
        except:
            flash("User not updated! (Error)")
            return render_template("update_user.html",form = form, newname = newname)
    else:
        return render_template("update_user.html",form = form, newname = newname, id = id)
#

# Delete user
@app.route('/delete/<int:id>')
def delete(id:int):
    usertodelete = Users.query.get_or_404(id)
    name = None
    form = NamerForm()
    try:
        db.session.delete(usertodelete)
        db.session.commit()
        flash("User deleted successfully!")
        return redirect(url_for("add_user"))
    except:
        flash("User not deleted (Error)")
        
        return redirect(url_for("add_user"))
#

# Add post page
@app.route('/add-post', methods=['GET','POST'])
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Posts(title = form.title.data, content = form.content.data, author = form.author.data, slug = form.slug.data)
        # Clear the form
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''

        db.session.add(post)
        db.session.commit()
        flash("Blog Post Submitted")
    return render_template('add_post.html', form = form)
#

# Show posts
@app.route('/posts')
def posts():
    # grab all posts from the database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts = posts)
#

#Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500
#


if __name__ == "__main__":
    app.run("0.0.0.0", port=5002, debug=True)