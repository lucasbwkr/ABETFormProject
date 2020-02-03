# Source: https://www.youtube.com/watch?v=Z1RJmh_OqeA

from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

# Settings up database which will contain the results here.
# Name of the DB is results.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///results.db'
# Added to remove a deprecated feature (should not cause any issues)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Creating our database. 
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    classname = db.Column(db.String(50), nullable = False)
    results = db.Column(db.String(500), nullable = False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return '<Results %r>' % self.id

# Main page of our web app.
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug = True)
