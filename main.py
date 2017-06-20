from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('signup.html')

@app.route('/blog')
def display_blog():
    #returns everything from the DB
    posts = Blog.query.all()
    #It's in list format so this reverses the list!
    posts = posts[::-1]
    #Flask will render the template using the list passed to it
    return render_template('blog.html', posts = posts)

@app.route('/post', methods = ['GET'])
def display_post():
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
            post = Blog(title, body)
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
    del session['email']
    return redirect('/')

#Apparently you can't initialize the DB in the shell w/o this.
if __name__ == '__main__':
    app.run()