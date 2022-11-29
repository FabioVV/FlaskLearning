from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"
#SQLITE database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:guerra998@localhost/users'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# User Model creation
class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique = True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default = datetime.utcnow)
    def __repr__(self) -> str:
        return '<Name %r>' % self.name
#

# User Form
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite color")
    submit = SubmitField("Submit")
#

# Create a Form Class
class NamerForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")
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
            user = Users(name = form.name.data, email = form.email.data, favorite_color = form.favorite_color.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.email.favorite_color = ''
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
        #DIFFERENT WAY OF GETTING THE FORM
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
        return render_template("update_user.html",form = form, newname = newname)
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