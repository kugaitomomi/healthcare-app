from ensurepip import bootstrap
from enum import unique
from operator import ge
from urllib import request
from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from flask_bootstrap import Bootstrap

from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import pytz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

login_maneger = LoginManager()
login_maneger.init_app(app)


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


class User(UserMixin, db.Model):
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
