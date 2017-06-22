from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blog = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index', 'post']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users = users)
    #Don't this will work like imagine. Ask TF

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            if not user:
                username_error = "User not in database. Signup above!"
                return render_template('login.html', username_error = username_error, password_error = "")
            elif user.password != password:
                password_error = "Password is incorrect"
                return render_template('login.html', username_error = "", password_error = password_error )
            else: 
                return render_template('login.html', username_error = "", password_error = "")
    return render_template('login.html', username_error = "", password_error = "")

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        #Errors Displayed Empty as Default
        password_error = ""
        username_error = ""

        if not username or username.isspace():
            username_error = "Field Left Blank"
        if not is_un_or_pw_valid(username):
            username_error = "Not a Valid Username"
        if not password or password.isspace():
            password_error = "Field Left Blank"
        if not is_un_or_pw_valid(password):
            password_error = "Needs to be 3 to 20 characters Long With No Whitespaces"
        if not does_pw_match(password, verify):
            password_error = "Passwords didn't match"
        
        if not username_error and not password_error:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/')
            else:
                flash("Duplicate User")
        else: render_template('signup.html', username_error= username_error, password_error = password_error)          
    return render_template('signup.html', username_error = "", password_error = "")

@app.route('/blog')
def blog():
    if request.args.get('id'):
        post_id = request.args.get('id')
        post = Blog.query.filter(id = post_id).one()
        return render_template('postbyid.html', post = post)

    if request.args.get('user'):
        user_id = request.args.get('user')
        owner = User.query.filter_by(id = user_id).first()
        #Ask Max/Pertains to Question 10 on test
        posts = Blog.query.filter_by(owner = owner).all()
        return render_template('singleuser.html', posts = posts)
    #returns everything from the DB
    posts = Blog.query.all()
    #It's in list format so this reverses the list!
    posts = posts[::-1]
    #Flask will render the template using the list passed to it
    return render_template('blog.html', posts = posts)


@app.route('/post', methods = ['GET'])
def post():
    #gets id from a link I have in the /blog using get
    post_id = request.args.get('id')
    #uses the id to query only that id and store
    post = Blog.query.filter(Blog.id == post_id).one()
    # Passes one post by id to the template
    return render_template('postbyid.html', post = post)



@app.route('/newpost', methods=['POST', 'GET'])
def validate():
    #Only executes if form has been submitted
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        username = session['username']
        owner = User.query.filter_by( username = username).first()
        title_error = ""
        body_error = ""
        #Checks if empty or just white space
        if title == "" or title.isspace():
            title_error = "Please Enter A Title"
        if body == "" or body.isspace():
            body_error = "Please Write A Post"

        #if there are no errors
        if not title_error and not body_error:
            #Takes Title and body and makes an object
            post = Blog(title, body, owner)
            #Similar to git add
            db.session.add(post)
            #Similar to git ommit
            db.session.commit()
            # Query syntax to get last id added to DB
            entry = Blog.query.order_by('-id').first()
            #Integer by default, URLs are strings
            id = str(entry.id)
            return redirect('/post?id=' + id)
            
        else:
            #returns templates if errors aren't blank
            return render_template('newpost.html', body_error = body_error, title_error = title_error)
    else:
        return render_template('newpost.html', title_error = "", body_error = "")

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

def does_pw_match(password, verify):
    if password and verify:
        return password == verify
    else:
        return False

def is_un_or_pw_valid(username):
    if username:
        return re.match(r'^[\S]{3,20}$', username) is not None
    else:
        return False
#Apparently you can't initialize the DB in the shell w/o this.
if __name__ == '__main__':
    app.run()

