from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health.db'
db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    low_morning = db.Column(db.Integer, nullable=True)
    upper_morning = db.Column(db.Integer, nullable=True)
    low_evening = db.Column(db.Integer, nullable=True)
    upper_evening = db.Column(db.Integer, nullable=True)
    pulse = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Integer, nullable=True)
    medicine = db.Column(db.String(100), nullable=True)
    diary = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.now(pytz.timezone('Asia/Tokyo')))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create')
def create():
    return render_template('create.html')
