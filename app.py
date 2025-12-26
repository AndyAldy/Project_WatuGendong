import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from datetime import datetime

# HAPUS/COMMENT BAGIAN INI AGAR TIDAK ERROR DI LAPTOP
# import pymysql 
# pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.secret_key = 'kuncirahasiabanget'

# --- KONFIGURASI DATABASE PINTAR ---
# 1. Coba cari database Vercel
db_url = os.environ.get("POSTGRES_URL") 

# 2. Fix bug kecil untuk Vercel (ubah postgres:// jadi postgresql://)
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# 3. LOGIKA OTOMATIS:
# Jika ada db_url (artinya di Vercel), pakai itu.
# Jika TIDAK ada (artinya di Laptop), pakai 'sqlite:///database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Folder Upload (Gunakan /tmp untuk Vercel, atau static/uploads untuk lokal)
if os.environ.get("VERCEL"):
    app.config['UPLOAD_FOLDER'] = '/tmp'
else:
    # Kalau di laptop, simpan di folder static/uploads biar awet
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- MODEL DATABASE ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Reservasi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    no_hp = db.Column(db.String(20), nullable=False)
    tanggal = db.Column(db.Date, nullable=False)
    pesan = db.Column(db.Text, nullable=True)
    waktu_input = db.Column(db.DateTime, default=datetime.now)

class Galeri(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(100))
    gambar = db.Column(db.String(200), nullable=False)

class Artikel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(200), nullable=False)
    isi = db.Column(db.Text, nullable=False)
    gambar = db.Column(db.String(200))
    tanggal = db.Column(db.Date, default=datetime.now)

# Setup Database Otomatis
with app.app_context():
    db.create_all()
    # Buat admin jika belum ada
    if not User.query.filter_by(username='admin').first():
        admin_baru = User(username='admin', password='123')
        db.session.add(admin_baru)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES ---

@app.route('/')
def index():
    try:
        artikel_terbaru = Artikel.query.order_by(Artikel.tanggal.desc()).limit(3).all()
    except:
        artikel_terbaru = []
    return render_template('index.html', artikel=artikel_terbaru)

@app.route('/sejarah')
def sejarah():
    try:
        semua_artikel = Artikel.query.order_by(Artikel.tanggal.desc()).all()
    except:
        semua_artikel = []
    return render_template('sejarah.html', data=semua_artikel)

# ROUTE BARU: Detail Artikel (Yang tadi kita bahas)
@app.route('/artikel/<int:id>')
def detail_artikel(id):
    data_artikel = Artikel.query.get_or_404(id)
    # Pastikan nama file ini sesuai dengan yang ada di folder templates Anda
    return render_template('detail_sejarah.html', item=data_artikel)

@app.route('/galeri')
def galeri():
    try:
        data_foto = Galeri.query.all()
    except:
        data_foto = []
    return render_template('galeri.html', data=data_foto)

@app.route('/reservasi', methods=['GET', 'POST'])
def reservasi():
    if request.method == 'POST':
        try:
            tanggal_obj = datetime.strptime(request.form['tanggal'], '%Y-%m-%d').date()
            baru = Reservasi(nama=request.form['nama'], no_hp=request.form['no_hp'], tanggal=tanggal_obj, pesan=request.form['pesan'])
            db.session.add(baru)
            db.session.commit()
            return redirect(url_for('reservasi', sukses=1))
        except:
            pass
    return render_template('reservasi.html')

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

@app.route('/dashboard')
@login_required
def dashboard():
    data_res = Reservasi.query.order_by(Reservasi.waktu_input.desc()).all()
    data_gal = Galeri.query.all()
    data_art = Artikel.query.all()
    return render_template('dashboard.html', reservasi=data_res, galeri=data_gal, artikel=data_art)

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

# --- ROUTE EDIT DATA ---

@app.route('/edit/artikel/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_artikel(id):
    item = Artikel.query.get_or_404(id) # Ambil data atau error 404 jika tidak ada
    
    if request.method == 'POST':
        item.judul = request.form['judul']
        item.isi = request.form['isi']
        
        # Cek apakah admin upload gambar baru?
        if 'gambar' in request.files:
            file = request.files['gambar']
            if file.filename != '':
                filename = secure_filename(file.filename)
                
                # (Opsional) Hapus gambar lama agar hemat memori
                # try: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item.gambar))
                # except: pass
                
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                item.gambar = filename # Update nama file di database
        
        db.session.commit()
        flash('Artikel berhasil diperbarui!')
        return redirect(url_for('dashboard'))
        
    return render_template('edit_artikel.html', item=item)

@app.route('/edit/galeri/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_galeri(id):
    item = Galeri.query.get_or_404(id)
    
    if request.method == 'POST':
        item.judul = request.form['judul']
        
        if 'gambar' in request.files:
            file = request.files['gambar']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                item.gambar = filename
        
        db.session.commit()
        flash('Foto Galeri berhasil diperbarui!')
        return redirect(url_for('dashboard'))
        
    return render_template('edit_galeri.html', item=item)

@app.route('/hapus/<tipe>/<int:id>')
@login_required
def hapus(tipe, id):
    if tipe == 'galeri':
        item = Galeri.query.get(id)
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