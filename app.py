from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymysql

# Instalasi driver pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)

# --- KONEKSI DATABASE ---
# Pastikan XAMPP sudah START (Apache & MySQL)
# Buat database di phpMyAdmin bernama: wisata_watu_gendong
# Ganti 'username', 'password', dan 'hostname' sesuai tab Databases kamu
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://RisingLow:andyaldy0913@RisingLow.mysql.pythonanywhere-services.com/RisingLow$wisata_watu_gendong'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODEL DATA ---
class Reservasi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    no_hp = db.Column(db.String(20), nullable=False)
    tanggal = db.Column(db.Date, nullable=False)
    pesan = db.Column(db.Text, nullable=True)
    waktu_input = db.Column(db.DateTime, default=datetime.now)

# Buat Tabel Otomatis
with app.app_context():
    try:
        db.create_all()
        print(">> Database Berhasil Terhubung!")
    except Exception as e:
        print(f">> Gagal Konek Database: {e}")

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sejarah')
def sejarah():
    return render_template('sejarah.html')

@app.route('/galeri')
def galeri():
    return render_template('galeri.html')

@app.route('/reservasi', methods=['GET', 'POST'])
def reservasi():
    if request.method == 'POST':
        try:
            nama = request.form['nama']
            no_hp = request.form['no_hp']
            tanggal_str = request.form['tanggal']
            pesan = request.form['pesan']
            
            # Konversi string tanggal ke object date
            tanggal_obj = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
            
            baru = Reservasi(nama=nama, no_hp=no_hp, tanggal=tanggal_obj, pesan=pesan)
            db.session.add(baru)
            db.session.commit()
            return redirect(url_for('reservasi', sukses=1))
        except Exception as e:
            return f"Terjadi Error: {e}"
            
    return render_template('reservasi.html')

@app.route('/admin-data')
def admin_data():
    data = Reservasi.query.order_by(Reservasi.waktu_input.desc()).all()
    return render_template('admin_data.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)