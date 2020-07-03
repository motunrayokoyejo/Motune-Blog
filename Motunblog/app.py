from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3


app = Flask(__name__)
Bootstrap(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SECRET_KEY'] ='backenddeveloper'
db = SQLAlchemy()
db.init_app(app)

class Blog(db.Model):
    __tablename__ = 'blog'
    __searchable__ = ['title','content','author']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  
    def __repr__(self):
         return 'Blog post ' + str(self.id)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return 'Hello ' + self.first_name

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search/', methods=['GET', 'POST'])
def search():
    db = sqlite3.connect('posts.db')
    cursor = db.cursor()
    search = 'one'
    cursor.execute('SELECT title,content,author from blog WHERE title LIKE "%{}%" OR content LIKE "%{}%"'.format(search,search))
    cursor.fetchall()
    # if request.method == 'POST':
    #     search = request.form.get('search')
    #     db_folder ='posts.db'
    #     conn = sqlite3.connect(db_folder)
    #     c= conn.cursor()
    #     c.execute('SELECT title,content,author from blog WHERE title LIKE "%{}%" OR content LIKE "%{}%"'.format(search,search))
    #     posts = c.fetchall()
    #     print(posts)
    #     return render_template('posts.html', posts=posts)
    # return render_template('posts.html')


@app.route('/register/', methods=['GET','POST'])
def register():
    if request.method =='POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            flash('Passwords do not match! Try again.', 'danger')
        hashed_pwd = generate_password_hash(password, 'sha256')
        details = User(first_name=first_name,last_name=last_name,username=username,email=email,password=hashed_pwd)
        db.session.add(details)
        db.session.commit()
        return redirect('/login/')
    return render_template('register.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not (username and password):
           flash('Username or password cannot be empty')
           return redirect('/login/')
        else:
            username = username.strip()
            password = password.strip()
 
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password,password):
            session['username'] = True
            flash('Welcome ' + username)
            return redirect('/posts/')
        else:
            flash('Invalid username or password')
    return render_template('login.html')
        

@app.route('/posts/', methods=['GET', 'POST'])
def posts():
    if request.method =='POST':
        post_title = request.form['title']
        post_content = request.form['content']
        post_author = request.form['author']
        new_post = Blog(title=post_title,content=post_content,author=post_author)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts/')        
    else:
        all_posts= Blog.query.order_by(Blog.date_posted).all()
        return render_template('posts.html',posts=all_posts)

@app.route('/posts/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        post.title = request.form['title']
        post.author = request.form['author']
        post.content = request.form['content']
        new_post = Blog(title=post_title, content=post_content, author=post_author)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts/')
    else:
        return render_template('new-post.html')
     
@app.route('/posts/edit-blog/<int:id>/', methods=['GET', 'POST'])
def edit_blog(id):
    post = Blog.query.get_or_404(id)

    if request.method =='POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.author = request.form.get('author')
        db.session.commit()
        return redirect('/posts/')

    else:
        return render_template('edit-blog.html',post=post)

@app.route('/posts/delete/<int:id>')
def delete(id):
    post = Blog.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/posts/')




if __name__ == "__main__":
    app.run(debug=True, port=5001)