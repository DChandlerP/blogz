from flask import Flask, request, redirect, render_template
'''
from flask_sqlalchemy import SQLAlchemy
'''


app = Flask(__name__)
app.config['DEBUG'] = True

'''
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:beproductive@localhost:8889/get-it-done'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.string(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body
'''

@app.route('/', methods=['POST', 'GET'])
def newpost():
    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()