from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# 1. Baza va papkalarni sozlash
basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

db_path = os.path.join(instance_path, 'online_kurs.db')

# 2. Flask sozlamalari
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
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
    full_name = db.Column(db.String(100), default="Eleukanov Janbolat")
    bio = db.Column(db.Text, default="IT-Academy tiykarshisi ham basligi")
    password = db.Column(db.String(200), nullable=False)

# --- BAZANI VA ADMINNI SOZLASH ---
with app.app_context():
    db.create_all()
    target_pw = os.getenv('ADMIN_PASSWORD', 'admin123')
    admin = AdminProfile.query.first()
    if not admin:
        db.session.add(AdminProfile(password=generate_password_hash(target_pw)))
    else:
        admin.password = generate_password_hash(target_pw)
    db.session.commit()

# --- YO'NALISHLAR (ROUTES) ---

@app.route('/')
def index():
    courses = Course.query.all()
    return render_template('index.html', courses=courses)

@app.route('/enroll/<int:id>')
def enroll(id):
    course = Course.query.get_or_404(id)
    return render_template('enroll.html', course=course)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    phone = request.form.get('phone')
    course_id = request.form.get('course_id')
    new_app = Application(name=name, phone=phone, course_id=course_id)
    db.session.add(new_app)
    db.session.commit()
    return render_template('success.html', name=name)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        admin = AdminProfile.query.first()
        if admin and check_password_hash(admin.password, password):
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        return render_template('parol.html', error="Parol qáte!")
    return render_template('parol.html')

@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in'): return redirect(url_for('login'))
    courses = Course.query.all()
    return render_template('admin.html', courses=courses)

@app.route('/admin/add_course', methods=['POST'])
def add_course():
    if not session.get('logged_in'): return redirect(url_for('login'))
    title = request.form.get('title')
    desc = request.form.get('description')
    price = request.form.get('price')
    db.session.add(Course(title=title, description=desc, price=price))
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_course/<int:id>')
def delete_course(id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/arizalar')
def view_arizalar():
    if not session.get('logged_in'): return redirect(url_for('login'))
    courses = Course.query.all()
    return render_template('arizalar.html', courses=courses)

@app.route('/admin/profile', methods=['GET', 'POST'])
def admin_profile():
    if not session.get('logged_in'): return redirect(url_for('login'))
    admin_info = AdminProfile.query.first()
    if request.method == 'POST':
        admin_info.full_name = request.form.get('full_name')
        admin_info.bio = request.form.get('bio')
        new_pw = request.form.get('new_password')
        if new_pw:
            admin_info.password = generate_password_hash(new_pw)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('profile.html', admin_info=admin_info)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)