from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog')
def display_blog():
    posts = Blog.query.all()
    posts = posts[::-1]
    return render_template('blog.html', posts = posts)

@app.route('/post', methods = ['GET'])
def display_post():
    post_id = request.args.get('id')
    post = Blog.query.filter(Blog.id == post_id).one()
    return render_template('postbyid.html', post = post)

@app.route('/newpost', methods=['POST', 'GET'])
def validate():
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        title_error = ""
        body_error = ""

        if title == "" or title.isspace():
            title_error = "Please Enter A Title"
        if body == "" or body.isspace():
            body_error = "Please Write A Post"

        #if there are no errors
        if not title_error and not body_error:
            post = Blog(title, body)
            db.session.add(post)
            db.session.commit()
            entry = Blog.query.order_by('-id').first()
            id = str(entry.id)
            return redirect('/post?id=' + id)
            #get id for post
            #return redirect('/post?id=? + id)
        else:
            return render_template('newpost.html', body_error = body_error, title_error = title_error)
    else:
        return render_template('newpost.html', title_error = "", body_error = "")



if __name__ == '__main__':
    app.run()