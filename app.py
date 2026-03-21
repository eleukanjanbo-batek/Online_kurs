from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv() # .env faylidagi ma'lumotlarni yuklaydi

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

app = Flask(__name__)
app.secret_key = 'it_academy_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///online_kurs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELLAR ---
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
    full_name = db.Column(db.String(100), default="Rustamov Davron")
    bio = db.Column(db.Text, default="IT-Academy asoschisi va rahbari")
    password = db.Column(db.String(200), nullable=False)

# Bazani yaratish va adminni qo'shish
with app.app_context():
    db.create_all()
    if not AdminProfile.query.first():
        hashed_pw = generate_password_hash('ADMIN_PASSWORD')
        db.session.add(AdminProfile(password=hashed_pw))
        db.session.commit()

# --- YO'NALISHLAR ---
@app.route('/')
def index():
    courses = Course.query.all()
    return render_template('index.html', courses=courses)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        admin = AdminProfile.query.first()
        if admin and check_password_hash(admin.password, password):
            session['logged_in'] = True
            return redirect(url_for('admin_panel'))
        return render_template('parol.html', error="Xato parol!")
    return render_template('parol.html')

@app.route('/logout/')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin/')
def admin_panel():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    courses = Course.query.all()
    admin_info = AdminProfile.query.first()
    return render_template('admin.html', courses=courses, admin_info=admin_info)

@app.route('/admin/arizalar')
def arizalar_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    courses = Course.query.all()
    return render_template('arizalar.html', courses=courses)

@app.route('/admin/profile', methods=['GET', 'POST'])
def profile_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    admin_info = AdminProfile.query.first()
    if request.method == 'POST':
        admin_info.full_name = request.form.get('full_name')
        admin_info.bio = request.form.get('bio')
        new_pw = request.form.get('new_password')
        if new_pw:
            admin_info.password = generate_password_hash(new_pw)
        db.session.commit()
        return redirect(url_for('profile_page'))
    return render_template('profile.html', admin_info=admin_info)

# Kurs qo'shish, o'chirish va arizalar
@app.route('/enroll/<int:id>')
def enroll(id):
    course = Course.query.get_or_404(id)
    return render_template('enroll.html', course=course)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    phone = request.form.get('phone')
    course_id = request.form.get('course_id')
    db.session.add(Application(name=name, phone=phone, course_id=course_id))
    db.session.commit()
    return render_template('success.html', name=name)

@app.route('/admin/add_course', methods=['POST'])
def add_course():
    if not session.get('logged_in'): return redirect(url_for('login'))
    db.session.add(Course(title=request.form.get('title'), description=request.form.get('description'), price=request.form.get('price')))
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/delete_course/<int:id>')
def delete_course(id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/delete_app/<int:id>')
def delete_app(id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    app_data = Application.query.get_or_404(id)
    db.session.delete(app_data)
    db.session.commit()
    return redirect(url_for('arizalar_page'))

if __name__ == '__main__':
    app.run(debug=True)