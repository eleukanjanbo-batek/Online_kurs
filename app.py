from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Render'dagi Settings -> Environment qismidan oladi
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

# 🔥 SHU JOY O‘ZGARTIRILDI (absolute path)
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'online_kurs.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# --- MODELLAR (O'zgarishsiz qoladi) ---
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.String(50), nullable=False)
    applications = db.relationship('Application', backref='course_rel', lazy=True, cascade="all, delete-orphan")


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)


class AdminProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), default="Eleukanov Janbolat")
    bio = db.Column(db.Text, default="IT-Academy tiykarshisi ham basligi")
    password = db.Column(db.String(200), nullable=False)


# --- BAZANI VA ADMINNI TO'G'RI SOZLASH ---
with app.app_context():
    db.create_all()

    # Render'dagi parolni o'zgaruvchidan olamiz
    target_pw = os.getenv('ADMIN_PASSWORD', 'admin123')
    admin = AdminProfile.query.first()

    if not admin:
        hashed_pw = generate_password_hash(target_pw)
        db.session.add(AdminProfile(password=hashed_pw))
        print("Jana admin jaratildi!")
    else:
        # Har safar sayt yurganda parolni yangilab turadi (Render xatolarini tuzatish uchun)
        admin.password = generate_password_hash(target_pw)
        print("Admin paroli janalandi!")

    db.session.commit()

# --- YO'NALISHLAR (O'zgarishsiz qoladi) ---
# ... (Siz yozgan @app.route qismlari bu yerga tushadi) ...

if __name__ == '__main__':
    app.run(debug=True)