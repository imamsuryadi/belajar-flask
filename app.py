


from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from databese.db import db, get_all_collection, storage
from firebase_admin import firestore
from functools import wraps


# ===============================================

# Starter Template Flask
# By Makassar Coding

# ================================================
# Menentukan Nama Folder Penyimpanan Asset
app = Flask(__name__, static_folder='static', static_url_path='')
# Untuk Menggunakan flash pada flask
app.secret_key = 'iNiAdalahsecrEtKey'
# Untuk Mentukan Batas Waktu Session
app.permanent_session_lifetime = datetime.timedelta(days=7)
# Menentukan Jumlah Maksimal Upload File
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' in session:
            return f(*args, **kwargs)
        else:
            flash('Anda harus login', 'danger')
            return redirect(url_for('login'))
    return wrapper

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mahasiswa')
@login_required
def mahasiswa():
    
    daftar_mahasiswa = get_all_collection('mahasiswa')

    return render_template('mahasiswa/mahasiswa.html', daftar_mahasiswa=daftar_mahasiswa)

@app.route('/mahasiswa/tambah', methods=['GET','POST'])
@login_required
def tambah_mahasiswa():
    if request.method == 'POST':
        data = {
            'created_at': firestore.SERVER_TIMESTAMP,
            'nama_lengkap': request.form['nama_lengkap'],
            'nim': request.form['nim'],
            'status': request.form['status'],
            'jenis_kelamin': request.form['jenis_kelamin'],
            'tanggal_lahir': request.form['tanggal_lahir'],
            'jurusan': request.form['jurusan'],
        }

        if 'image' in request.files and request.files['image']:
            image = request.files['image']
            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
            filename = image.filename
            lokasi = f"mahasiswa/{filename}"
            ext = filename.rsplit('.', 1)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                storage.child(lokasi).put(image)
                data['photoURL'] = storage.child(lokasi).get_url(None)
            else:
                flash("Foto tidak diperbolehkan", "danger")
                return redirect(url_for('mahasiswa'))

        db.collection('mahasiswa').document().set(data)
        flash('Berhasil menambahkan data', 'success')
        return redirect(url_for('mahasiswa'))
        # return jsonify(request.form)
    jurusan = get_all_collection('jurusan')
    return render_template('mahasiswa/tambah_mahasiswa.html', jurusan=jurusan)

@app.route('/mahasiswa/<uid>')
@login_required
def lihat_mahasiswa(uid):
    mahasiswa = db.collection('mahasiswa').document(uid).get().to_dict()
    return render_template('mahasiswa/lihat_mahasiswa.html', data=mahasiswa)

@app.route('/mahasiswa/edit/<uid>', methods=['GET','POST'])
def edit_mahasiswa(uid):
    if request.method == 'POST':
        data = {
            
            'nama_lengkap': request.form['nama_lengkap'],
            'nim': request.form['nim'],
            'status': request.form['status'],
            'jenis_kelamin': request.form['jenis_kelamin'],
            'tanggal_lahir': request.form['tanggal_lahir'],
            'jurusan': request.form['jurusan'],
        }
        db.collection('mahasiswa').document(uid).update(data)
        flash('Berhasil edit data', 'success')
        return redirect(url_for('mahasiswa'))
    mahasiswa = db.collection('mahasiswa').document(uid).get().to_dict()
    return render_template('mahasiswa/edit_mahasiswa.html', data=mahasiswa)

@app.route('/mahasiswa/hapus/<uid>')
@login_required
def hapus_mahasiswa(uid):  
    db.collection('mahasiswa').document(uid).delete()
    flash('Berhasil hapus data', 'danger')
    return redirect(url_for('mahasiswa'))

@app.route('/login', methods=['POST', 'GET'])
def login ():
    if request.method == 'POST':
        data = {
            'username': request.form['username'],
            'password': request.form['password']
        }
        users_ref = db.collection('users').where('username', '==', data['username']).stream()
        user = {}
        for use in users_ref:
            user = use.to_dict()
        
        if user:
            if check_password_hash(user['password'], data['password']):
                session['user'] = user
                flash('Berhasil Login', 'Success')
                return redirect(url_for('mahasiswa'))
            else:
                flash('Password anda salah', 'danger')
                return redirect(url_for('login'))
        else:
            flash('username tidak ditemukan', 'danger')
            return redirect(url_for('login'))
        
        if 'user' in session:
            return redirect(url_for('mahasiswa'))
            

    return render_template('login.html')

@app.route('/register', methods={'GET', 'POST'})
def register():
    if request.method == 'POST':
        data = {
            'created_at': firestore.SERVER_TIMESTAMP,
            'username': request.form['username'].lower()
        }
        password = request.form['password']
        password_1 = request.form['password_1']

        if password_1 != password:
            flash('Password Tidak Sama', 'danger')
            return redirect(url_for('register'))

        users_ref = db.collection('users').where('username', '==', data['username']).stream()
        user = {}
        for use in users_ref:
            user = use.to_dict()

        if user:
            flash('Username Sudah Terdaftar', 'danger')
            return redirect(url_for('register'))

        data['password'] = generate_password_hash(password, 'sha256')

        db.collection('users').document().set(data)
        flash('Pendaftaran Berhasil', 'success')
        return redirect(url_for('login'))

    
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/jurusan', methods=['POST', 'GET'])
def jurusan():
    if request.method == 'POST':
        data = {
            'created_at': firestore.SERVER_TIMESTAMP,
            'jurusan': request.form['jurusan']
        }
        db.collection('jurusan').document().set(data)
        flash('Berhasil Membuat Jurusan', 'success')
        return redirect(url_for('jurusan'))

    daftar_jurusan = get_all_collection('jurusan')

    return render_template('jurusan/jurusan.html', data=daftar_jurusan)

@app.route('/jurusan/hapus/<uid>')
@login_required
def hapus_jurusan(uid):  
    db.collection('jurusan').document(uid).delete()
    flash('Berhasil hapus data', 'danger')
    return redirect(url_for('jurusan'))

@app.route('/jursan/edit', methods=['POST'])
def edit_jurusan():
    if request.method == 'POST':
        uid = request.form['id_jurusan']
        data = {
            'jurusan': request.form['nama_jurusan']
        }
        db.collection('jurusan').document(uid).update(data)
        flash('Berhasil Edit Jurusan', 'success')
        return redirect(url_for('jurusan'))

# Untuk Menjalankan Program Flask
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)






