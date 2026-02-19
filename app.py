from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models import courses_list  # Models faylidan ro'yxatni chaqiramiz

app = Flask(__name__)

# Ma'lumotlar bazasi sozlamalari
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///online_kurs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Kursga yozilgan mijozlarni saqlash uchun DB model
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    course_title = db.Column(db.String(100), nullable=False)

# Bazani yaratish
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html', courses=courses_list)

@app.route('/enroll/<int:course_id>')
def enroll(course_id):
    course = next((c for c in courses_list if c.id == course_id), None)
    if course:
        return render_template('enroll.html', course_title=course.title)
    return "Kurs topilmadi", 404

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    phone = request.form.get('phone')
    course_title = request.form.get('course_title')

    new_app = Application(name=name, phone=phone, course_title=course_title)
    db.session.add(new_app)
    db.session.commit()

    return render_template('success.html', name=name)

@app.route('/admin/')
def admin():
    all_apps = Application.query.all()
    return render_template('admin.html', apps=all_apps)

# --- YANGI QO'SHILGAN O'CHIRISH FUNKSIYASI ---
@app.route('/delete/<int:id>')
def delete_application(id):
    app_to_delete = Application.query.get_or_404(id) # ID bo'yicha topish
    try:
        db.session.delete(app_to_delete) # Bazadan o'chirish
        db.session.commit() # O'zgarishni tasdiqlash
        return redirect(url_for('admin')) # Admin panelga qaytish
    except:
        return "Ma'lumotni o'chirishda xatolik yuz berdi"

if __name__ == '__main__':
    app.run(debug=True)