from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import pymysql
import os

# Konfigurasi Driver MySQL
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.secret_key = 'kuncirahasiabanget'  # Wajib untuk session login

# --- KONFIGURASI ---
# 1. Database (Sesuaikan dengan PythonAnywhere/XAMPP kamu)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/wisata_watu_gendong'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 2. Folder Upload Foto
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Pastikan folder ini dibuat otomatis
os.makedirs(os.path.join(app.root_path, UPLOAD_FOLDER), exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- MODEL DATABASE ---

# 1. Model Admin (User)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False) # Password polos (untuk belajar)

# 2. Model Reservasi (Booking)
class Reservasi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    no_hp = db.Column(db.String(20), nullable=False)
    tanggal = db.Column(db.Date, nullable=False)
    pesan = db.Column(db.Text, nullable=True)
    waktu_input = db.Column(db.DateTime, default=datetime.now)

# 3. Model Galeri (Foto)
class Galeri(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(100))
    gambar = db.Column(db.String(200), nullable=False) # Nama file gambar

# 4. Model Artikel (Berita/Blog)
class Artikel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(200), nullable=False)
    isi = db.Column(db.Text, nullable=False)
    gambar = db.Column(db.String(200)) # Gambar header artikel
    tanggal = db.Column(db.Date, default=datetime.now)

# Setup Database & Akun Admin Pertama
with app.app_context():
    try:
        db.create_all()
        # Cek apakah admin sudah ada? Jika belum, buat default: admin/admin123
        if not User.query.filter_by(username='admin').first():
            admin_baru = User(username='admin', password='123')
            db.session.add(admin_baru)
            db.session.commit()
            print(">> Akun Admin Dibuat: User='admin', Pass='123'")
    except Exception as e:
        print(f"Error Database: {e}")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES PUBLIC (USER) ---

@app.route('/')
def index():
    # Tampilkan 3 artikel terbaru di halaman depan
    artikel_terbaru = Artikel.query.order_by(Artikel.tanggal.desc()).limit(3).all()
    return render_template('index.html', artikel=artikel_terbaru)

@app.route('/sejarah')
def sejarah():
    # Halaman ini sekarang menampilkan List Artikel (Blog)
    semua_artikel = Artikel.query.order_by(Artikel.tanggal.desc()).all()
    return render_template('sejarah.html', data=semua_artikel)

@app.route('/galeri')
def galeri():
    # Ambil foto dari database
    data_foto = Galeri.query.all()
    return render_template('galeri.html', data=data_foto)

@app.route('/reservasi', methods=['GET', 'POST'])
def reservasi():
    if request.method == 'POST':
        # (Logika Booking sama seperti sebelumnya)
        tanggal_obj = datetime.strptime(request.form['tanggal'], '%Y-%m-%d').date()
        baru = Reservasi(nama=request.form['nama'], no_hp=request.form['no_hp'], tanggal=tanggal_obj, pesan=request.form['pesan'])
        db.session.add(baru)
        db.session.commit()
        return redirect(url_for('reservasi', sukses=1))
    return render_template('reservasi.html')

# --- ROUTES ADMIN ---

# 1. Halaman Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau Password Salah!')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# 2. Dashboard Admin
@app.route('/dashboard')
@login_required
def dashboard():
    data_res = Reservasi.query.order_by(Reservasi.waktu_input.desc()).all()
    data_gal = Galeri.query.all()
    data_art = Artikel.query.all()
    return render_template('dashboard.html', reservasi=data_res, galeri=data_gal, artikel=data_art)

# 3. Tambah Foto Galeri
@app.route('/tambah_foto', methods=['POST'])
@login_required
def tambah_foto():
    if 'gambar' in request.files:
        file = request.files['gambar']
        if file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            judul = request.form['judul']
            baru = Galeri(judul=judul, gambar=filename)
            db.session.add(baru)
            db.session.commit()
    return redirect(url_for('dashboard'))

# 4. Tambah Artikel
@app.route('/tambah_artikel', methods=['POST'])
@login_required
def tambah_artikel():
    judul = request.form['judul']
    isi = request.form['isi']
    filename = None
    
    if 'gambar' in request.files:
        file = request.files['gambar']
        if file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    baru = Artikel(judul=judul, isi=isi, gambar=filename)
    db.session.add(baru)
    db.session.commit()
    return redirect(url_for('dashboard'))

# 5. Hapus Data
@app.route('/hapus/<tipe>/<int:id>')
@login_required
def hapus(tipe, id):
    if tipe == 'galeri':
        item = Galeri.query.get(id)
        # Hapus file fisik
        try: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item.gambar))
        except: pass
        db.session.delete(item)
    elif tipe == 'artikel':
        item = Artikel.query.get(id)
        db.session.delete(item)
    elif tipe == 'reservasi':
        item = Reservasi.query.get(id)
        db.session.delete(item)
    
    db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)