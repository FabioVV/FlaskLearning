from flask import (Flask, flash, redirect, render_template, request, session, url_for)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid as uuid
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from flask_login import UserMixin
from datetime import date
from forms import UserForm, LoginForm, PostForm, NamerForm, SearchForm
from flask_ckeditor import CKEditor
import os

app = Flask(__name__)
ckeditor = CKEditor(app)
app.secret_key = "supersecretkey"
#SQLITE database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:guerra998@localhost/users'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#Login Stuffs
loginmanager = LoginManager()
loginmanager.init_app(app)
loginmanager.login_view = 'login'

@loginmanager.user_loader
def load_user(userid):
    return Users.query.get(int(userid))
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

#Login page
@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username = form.username.data).first()
        if user:
            #check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login successfull!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong password! Try again.")
        else:
            flash("Unexistent user.")
    return render_template("login.html",form = form)
#

# Logout
@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out!")
    return redirect(url_for('login'))
#

#Dashboard page
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")
    
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
            username = form.username.data, 
            email = form.email.data, 
            password_hash = hashedpasswd, 
            favorite_color = form.favorite_color.data)

            db.session.add(user)
            db.session.commit()

        name = form.name.data
        form.username.data = ''
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
@login_required
def update(id:int):
    form = UserForm()
    newname = Users.query.get_or_404(id)
    if request.method == "POST":
        #DIFFERENT WAY OF GETTING THE FORM DATA
        newname.name = request.form['name']
        newname.email = request.form['email']
        newname.username = request.form['username']
        newname.favorite_color = request.form['favorite_color']
        newname.about = request.form['about']
        newname.profile_pic = request.files['profile_pic']
      
        #Grab image name
        picfilename = secure_filename(newname.profile_pic.filename)
        # set uuid
        picname = str(uuid.uuid1()) + "_" + picfilename
        newname.profile_pic = picname
        #SAVE IMAGE
        saver = request.files['profile_pic']
        
        try:
            db.session.commit()
            saver.save(os.path.join(app.config['UPLOAD_FOLDER'], picname))
            flash("User updated successfully!")
            return render_template("update_user.html",form = form, newname = newname, id = id)
        except:
            flash("User not updated! (Error)")
            return render_template("update_user.html",form = form, newname = newname, id = id)
    else:
        return render_template("update_user.html",form = form, newname = newname, id = id)
#

# Delete user
@app.route('/delete/<int:id>')
@login_required
def delete(id:int):
    usertodelete = Users.query.get_or_404(id)
    if current_user.id == id:
        try:
            db.session.delete(usertodelete)
            db.session.commit()
            flash("User deleted successfully!")
            return redirect(url_for("add_user"))
        except:
            flash("User not deleted (Error)")
            return redirect(url_for("add_user"))
    else:
        flash("User not deleted (Unauthorized action)")
        return redirect(url_for("dashboard"))
#

# Show all posts
@app.route('/posts')
def posts():
    # grab all posts from the database
    posts = Posts.query.order_by(Posts.date_posted)   
    return render_template('posts.html', posts = posts)
#

# Add post page
@app.route('/add-post', methods=['GET','POST'])
@login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title = form.title.data, content = form.content.data, slug = form.slug.data, poster_id = poster)

        # Clear the form
        form.title.data = ''
        form.content.data = ''
        form.slug.data = ''

        db.session.add(post)
        db.session.commit()
        flash("Blog Post Submitted")
    return render_template('add_post.html', form = form)
#

# Show individual postposts
@app.route('/posts/<int:id>')
@login_required
def post(id):
    # grab all posts from the database
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post = post)
#

# Edit posts
@app.route('/posts/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id) 
    form = PostForm()
    if current_user.id == post.poster.id:
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            post.slug = form.slug.data

            #update database
            db.session.add(post)
            db.session.commit()
            flash("Post has been updated.")
            return redirect(url_for('post', id = post.id))

        form.title.data = post.title
        form.content.data = post.content
        form.slug.data = post.slug
        return render_template('edit_post.html', form = form)
    else:
        flash("Access denied.")
        return redirect(url_for('posts'))
#

# Delete post
@app.route('/posts/delete/<int:id>')
@login_required
def post_delete(id):
    posttodelete = Posts.query.get_or_404(id)
    if current_user.id == posttodelete.poster.id:
        try:
            db.session.delete(posttodelete)
            db.session.commit()
            flash("Post deleted!")
            return redirect(url_for("posts"))
        except:
            flash("Post not deleted. (Error)")
            return redirect(url_for("posts"))
    else:
        flash("Access denied. (Unauthorized action)")
        return redirect(url_for("posts"))
#

# Search function
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    post_s = Posts.query 
    if form.validate_on_submit():
        post_searched = form.searched.data
        post_s = post_s.filter(Posts.content.like('%' + post_searched + '%'))
        post_s = post_s.order_by(Posts.title).all()
        return render_template("search.html", searched = post_s)
#

# Admin function
@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    users = Users.query.order_by(Users.date_added)
    if id == 18:
        return render_template("admin.html", users = users)
    else:
        flash("Unauthorized access.")
        return redirect(url_for('dashboard'))
#

#Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500
#

# Passando para o base.html o form, para que o WTF que foi colocado no NAV funcione, (base includes nav)
@app.context_processor
def base():
    form = SearchForm()
    return dict(form = form)
#

# MODELS BELLOW

# Blog post model creation
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(50))
    content = db.Column(db.Text)
    slug = db.Column(db.String(100))
    date_posted = db.Column(db.DateTime, default = datetime.utcnow)
    
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#

# User Model creation
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique = True)
    favorite_color = db.Column(db.String(120))
    about = db.Column(db.Text(75),nullable=True)
    password_hash = db.Column(db.String(128))
    profile_pic = db.Column(db.String(300), nullable=True)
    date_added = db.Column(db.DateTime, default = datetime.utcnow)

    post_count = db.relationship('Posts', backref='poster')

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
if __name__ == "__main__":
    app.run("0.0.0.0", port=5002, debug=True)