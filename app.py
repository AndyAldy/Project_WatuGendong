from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# --- KONEKSI KE MYSQL XAMPP ---
# Format: mysql+pymysql://username:password@host/nama_database
# Default XAMPP: user='root', password='', host='localhost'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/wisata_watu_gendong'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODEL DATABASE (Tabel Reservasi) ---
class Reservasi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    no_hp = db.Column(db.String(20), nullable=False)
    tanggal = db.Column(db.Date, nullable=False) # Tipe data Date
    pesan = db.Column(db.Text, nullable=True)
    waktu_input = db.Column(db.DateTime, default=datetime.now)

# Membuat Tabel Otomatis di MySQL
with app.app_context():
    db.create_all()

# --- ROUTES (Jalur Halaman) ---

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
        # Ambil data dari form
        nama = request.form['nama']
        no_hp = request.form['no_hp']
        tanggal_str = request.form['tanggal']
        pesan = request.form['pesan']

        # Konversi string tanggal ke format date python
        tanggal_obj = datetime.strptime(tanggal_str, '%Y-%m-%d').date()

        # Simpan ke MySQL
        data_baru = Reservasi(nama=nama, no_hp=no_hp, tanggal=tanggal_obj, pesan=pesan)
        db.session.add(data_baru)
        db.session.commit()

        return redirect(url_for('reservasi', sukses=1))
    
    return render_template('reservasi.html')

@app.route('/admin-data')
def admin_data():
    # Tampilkan data urut dari yang terbaru
    data = Reservasi.query.order_by(Reservasi.waktu_input.desc()).all()
    return render_template('admin_data.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)