from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:pwforbuildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):
    query = db_session.query_property()
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True)
    body = db.Column(db.String)

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/post',)
def post():
    post_id = request.args.get(id)
    post_title = Blog.query.title(id==post_id)
    post_body = Blog.query.body(id==post_id)

    return render_template(post.html, post_title=post_title, post_body=post_body)

@app.route('/blog', methods=['GET'])
def blog():
    posts = Blog.query.id.all()
    post_id = blog.id
    post_title = Blog.query.title.(id==post_id)
    post_body = blog.body

    return render_template('blog.html', posts=posts, post_id=post_id, post_title=post_title)

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == 'GET':
        return render_template('newpost.html')
    if request.method == 'POST':
        post_title = request.form['blog_title']
        post_body = request.form['blog_body']
        if not post_title:
            flash("You forgot the title!")
            return redirect('/')
        if not post_body:
            flash("You forgot the body!")
            return redirect('/')
        
        db.session.add(post_title, post_body)
        db.session.commit()
        return render_template('post.html', post_title=blog_title, post_body=blog_body)

if __name__ == '__main__':
    app.run()