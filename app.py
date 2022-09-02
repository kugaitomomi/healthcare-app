from flask import Flask, make_response
from flask import render_template, request, redirect, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import pytz
import pandas as pd
import matplotlib.pyplot as plt
import csv
from io import StringIO


app = Flask(__name__)
DB_URL = 'sqlite:///health.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
image = Blueprint("image", __name__, static_url_path='/images',
                  static_folder='./static/images')
app.register_blueprint(image)


df = pd.read_csv('healthlog.csv')
header = df.columns
record = df.values.tolist()

login_maneger = LoginManager()
login_maneger.init_app(app)


class Post(db.Model):
    __tablename__ = "healthlog"
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


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(12))


@login_maneger.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
@login_required
def index():
    if request.method == 'GET':
        posts = Post.query.all()
        return render_template('index.html', posts=posts)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

# フォームから取得した値は、dbのどのカラムに当てはまるのか指定してあげないといけない。
        user = User(username=username,
                    password=generate_password_hash(password, method='sha256'))
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    else:
        return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect('/')

    else:
        return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        upper_morning = request.form.get('upper_morning')
        low_morning = request.form.get('low_morning')
        upper_evening = request.form.get('upper_evening')
        low_evening = request.form.get('low_evening')
        pulse = request.form.get('pulse')
        weight = request.form.get('weight')
        medicine = request.form.get('medicine')
        diary = request.form.get('diary')

# フォームから取得した値は、dbのどのカラムに当てはまるのか指定してあげないといけない。
        post = Post(upper_morning=upper_morning, low_morning=low_morning,
                    upper_evening=upper_evening, low_evening=low_evening, pulse=pulse, weight=weight, medicine=medicine, diary=diary)

        db.session.add(post)
        db.session.commit()
        return redirect('/')

    else:
        return render_template('create.html')


@app.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)
    else:
        post.upper_morning = request.form.get('upper_morning')
        post.low_morning = request.form.get('low_morning')
        post.upper_evening = request.form.get('upper_evening')
        post.low_evening = request.form.get('low_evening')
        post.pulse = request.form.get('pulse')
        post.weight = request.form.get('weight')
        post.medicine = request.form.get('medicine')
        post.diary = request.form.get('diary')

        db.session.commit()
        return redirect('/')


@app.route('/<int:id>/delete', methods=['GET'])
@login_required
def delete(id):
    post = Post.query.get(id)

    db.session.delete(post)
    db.session.commit()
    return redirect('/')


@app.route('/graph')
def graph():
    return render_template('graph.html', header=header, record=record)


@app.route('/quickbooks/<obj>')
def download(obj):

    f = StringIO()
    writer = csv.writer(
        f, quotechar='"', quoting=csv.QUOTE_ALL, lineterminator="\n")

    if obj == 'healthlog':
        writer.writerow(
            ['id', 'upper_morning', 'low_morning', 'upper_evening', 'low_evening', 'pulse', 'weight', 'medicine', 'diary' 'created_at'])
        for post in Post.query.all():
            writer.writerow(
                [post.id, post.upper_morning, post.low_morning, post.upper_evening, post.low_evening, post.pulse, post.weight, post.medicine, post.diary, post.created_at])

    res = make_response()
    res.data = f.getvalue()
    res.headers['Content-Type'] = 'text/csv'
    res.headers['Content-Disposition'] = 'attachment; filename=' + obj + '.csv'
    return res
