from urllib import request
from flask import Flask
from flask import render_template, request, redirect
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
    if request.method == 'GET':
        posts = Post.query.all()
        return render_template('index.html', posts=posts)


@app.route('/create', methods=['GET', 'POST'])
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
def delete(id):
    post = Post.query.get(id)

    db.session.delete(post)
    db.session.commit()
    return redirect('/')
