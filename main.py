from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzpassword@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    title = db.Column(db.String(120), unique=True)
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)
 

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        flash("You must be logged in to blog.", 'error')
        return render_template('/login.html')

@app.route('/index', methods=['GET'])
def index():
    users = User.query.all()
    return render_template('/index.html', users=users)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if username not in existing_user:
            flash('That user does not seem to exist.', 'error')
            return render_template('/login.html')
            
        elif existing_user and check_pw_hash(password, existing_user.pw_hash):
            session['username'] = username
            flash("You are now logged in!")
            return redirect('/newpost.html')
        else:
            flash('User password incorrect, or user does not exist', 'error')
            return render_template('/login.html')

    return render_template('/login.html')


@app.route('/signup', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':  
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        def un_error(username):
            if not username:
                flash("You didn't type anything! Please try again.", 'unerror')
            elif len(username) > 20 or len(username) < 3:
                flash("Your username must be atleast 3 characters long, and not more than 20. Please try again", 'unerror')
            elif ' ' in username == True:
                flash("Your username cannot contain any spaces. Please try again.", 'unerror')
            elif existing_user:
                flash("That username seems to be taken. Please try another.", 'unerror')
            else:
                return False

        def pw_error(password):
            if not password:
                flash("You didn't type anything! Please try again.", 'pwerror')
            elif len(password) > 20 or len(password) < 3:
                flash("Your password must be atleast 3 characters long, and not more than 20. Please try again.", 'pwerror')
            elif ' ' in password:
                flash("Your password cannot contain any spaces. Please try again.", 'pwerror')
            else:
                return False

        def vpw_error(verify):
            if verify != password:
                flash("Your passwords don't match. Please try again", 'vpwerror')
            else:
                return False

        if not un_error(username) and not pw_error(password) and not vpw_error(verify):
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash("You are now registered and logged in!")
            return render_template('/newpost.html')
        else:
            return render_template('/signup.html')
    else:
        return render_template('/signup.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/post/<post_id>')
def post(post_id):
    blogs = Blog.query.all(id==post_id)

    return render_template(post.html, blogs=blogs)

@app.route('/blog', methods=['GET'])
@app.route('/blog/<user_id>', methods=['GET'])
def find_user():
    if user_id:
        blogs = Blog.query.order_by(date).all(owner_id==user_id)
    else:
        blogs = Blog.query.order_by(date).all()
    return render_template(blog.html, blogs=blogs)


@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == 'GET' and 'username' in session:
        user = User.query.all(username==username).first()
        user_id = user.id
        return render_template('newpost.html', user_id=user_id)
    if request.method == 'POST' and 'username' in session:
        post_title = request.form['blog_title']
        post_body = request.form['blog_body']
        if not post_title:
            flash("You forgot the title!")
            return render_template('/newpost.html', blog_title=blog_title, blog_body=blog_body, user_id=user_id)
        if not post_body:
            flash("You forgot the body!")
            return redirect('/newpost.html', blog_title=blog_title, blog_body=blog_body, user_id=user_id)
        
        new_blog = Blog(blog_title, blog_body, user_id)
        db.session.add(new_blog)
        db.session.commit()
        blogs = Blog.query.order_by(date).all(owner_id==user_id)
        return render_template('post.html', blogs=blogs)


def main():
    app.run()

if __name__ == "__main__":
    main()