from flask import Flask, render_template, url_for, session, redirect, request, flash, get_flashed_messages
from models import Pengguna, Transaksi
from functools import wraps
from datetime import datetime
import os

# os.system('sudo /opt/lampp/lampp start')

application = Flask(__name__)
application.config['SECRET_KEY'] = '1234567890!@#$%^&*()'
application.config['UPLOAD_FOLDER'] = os.path.realpath('.') + '/static/uploads'
application.config['MAX_CONTENT_PATH'] = 10000000

pengguna = Pengguna()
transaksi = Transaksi()

def balance_count():
    pengguna_id = session.get('pengguna_id')

    pemasukan = transaksi.get_sum_income(pengguna_id)
    pengeluaran = transaksi.get_sum_spending(pengguna_id)
    if pemasukan == None or pengeluaran == None:
        pemasukan = 0
        pengeluaran = 0
        data_rekap = (0, 0, 0, 0)
    else:
        saldo = pemasukan - pengeluaran
        try:
            persen = round((pengeluaran / pemasukan) * 100)
        except:
            persen = 0

        if persen > 100:
            persen = 100
        data_rekap = (pemasukan, pengeluaran, persen, saldo)
    return data_rekap

def check_role(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if session.get('role') == 'admin':
            return redirect(url_for('dashboard_admin'))
        if session.get('role') == 'user':
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return decorated

def check_session_user(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if 'name' not in session:
            return redirect('login')
        elif session.get('role') == 'admin':
            return redirect(url_for('dashboard_admin'))
        return func(*args, **kwargs)
    return decorated

def check_session_admin(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if 'name' not in session:
            return redirect('login')
        elif session.get('role') == 'user':
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return decorated

@application.route('/')
@check_session_user
def index():
    data_rekap = balance_count()

    # semua data transaksi user
    data = transaksi.ambilDataTransaksi(session.get('pengguna_id'))

    # mengambil nama user yang tersimpan di session
    name = session.get('name')

    if session.get('pesan') == 'add_income_berhasil':
        session.pop('pesan', '')
        return render_template('dashboard.html', name=name, data_rekap=data_rekap, add_income_berhasil=True, data=data)
    elif session.get('pesan') == 'add_spending_berhasil':
        session.pop('pesan', '')
        return render_template('dashboard.html', name=name, data_rekap=data_rekap, add_spending_berhasil=True, data=data)
    elif session.get('pesan') == 'delete_transaksi_berhasil':
        session.pop('pesan', '')
        return render_template('dashboard.html', name=name, data_rekap=data_rekap, delete_transaksi_berhasil=True, data=data)
    elif session.get('pesan') == 'edit_transaksi_berhasil':
        session.pop('pesan', '')
        return render_template('dashboard.html', name=name, data_rekap=data_rekap, edit_transaksi_berhasil=True, data=data)

    return render_template('dashboard.html', data=data, name=name, data_rekap=data_rekap)

@application.route('/login', methods=['GET', 'POST'])
@check_role
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username != '' and password != '':
            if len(username) > 3 and len(password) > 3:
                try:
                    data_user = pengguna.ambilDataUser(username, password)
                    session['pengguna_id'] = data_user[0]
                    session['name'] = data_user[1]
                    session['role'] = data_user[4]
                    role = data_user[4]
                    if role == 'admin':
                        return redirect(url_for('dashboard_admin')) 

                    return redirect(url_for('index'))
                except:
                    return render_template('login.html', tidak_ada=True)
            else:
                return render_template('login.html', kurang=True)
        else:
            return render_template('login.html', kosong=True)

    if session.get('pesan') == 'registrasi_berhasil':
        session.pop('pesan','')
        return render_template('login.html', berhasil=True)
    return render_template('login.html')

@application.route('/register', methods=['GET', 'POST'])
@check_role
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        if username != '' and password != '':
            if len(username) > 3 and len(password) > 3:
                if pengguna.ambilDataUser(username, password) == None:
                    data = (name, username, password, 'user', '')
                    pengguna.insertDataUser(data)
                    session['pesan'] = 'registrasi_berhasil'
                    return redirect(url_for('login'))
                else:
                    return render_template('register.html', sudah_ada=True)
            else:
                return render_template('register.html', kurang=True)
        else:
            return render_template('register.html', kosong=True)
    return render_template('register.html')

@application.route('/show_note/<no>')
@check_session_user
def show_note(no):
    data = transaksi.ambilSatuDataTransaksi(no)
    return render_template('show_note.html', data=data)

@application.route('/dashboard_admin')
@check_session_admin
def dashboard_admin():
    if session.get('role') == 'user':
        return redirect(url_for('index'))
    name = session.get('name')
    total_user = pengguna.ambilTotalUser()

    transaction_data = pengguna.get_all_transaction()
    
    try:
        if transaction_data[0][0] == None:
            return render_template('dashboard_admin.html', name=name, total_user=total_user, transaction_data=transaction_data)
    except:
        pass

    if session.get('pesan') == 'delete_user_berhasil':
        session.pop('pesan', '')
        return render_template('dashboard_admin.html', name=name, total_user=total_user, delete_user_berhasil=True, transaction_data=transaction_data)
    return render_template('dashboard_admin.html', name=name, total_user=total_user, transaction_data=transaction_data)

@application.route('/add_income', methods=['GET', 'POST'])
@check_session_user
def add_income():
    name = session.get('name')

    saldo = balance_count()[3]

    if request.method == 'POST':
        # mengambil pengguna id dari session
        pengguna_id = session.get('pengguna_id')

        # mengambil description, nominal, dan date dari form
        description = request.form['description']
        nominal = request.form['nominal']
        date = request.form['date']

        if date == '':
            date = datetime.now().date()


        # mengambil total transaksi saat ini
        jumlah = str(transaksi.getCountTransaksiIdinDatabase())

        # mengatur lokasi penyimpanan dan nama file
        file_location = application.config['UPLOAD_FOLDER'] + '/' + 'nota_' + jumlah

        if description != '' and nominal != '':
            try:
                nominal = int(nominal)
                try:
                    nota = request.files['nota']

                    if nota.filename != '':
                        nota.save(file_location)

                    filename = 'nota_' + jumlah
                    data = (pengguna_id, date, description, nominal, 0, filename)
                    transaksi.insertDataTransaksi(data)
                    session['pesan'] = 'add_income_berhasil'
                    return redirect(url_for('index'))
                except:
                    return render_template('add_income.html', name=name, saldo=saldo, gagal=True)
            except:
                return render_template('add_income.html', name=name, saldo=saldo, bukan_angka=True)
        else:
            return render_template('add_income.html', name=name, saldo=saldo, kosong=True)
    return render_template('add_income.html', name=name, saldo=saldo)

@application.route('/add_spending', methods=['GET', 'POST'])
@check_session_user
def add_spending():
    name = session.get('name')

    saldo = balance_count()[3]

    if request.method == 'POST':
        # mengambil pengguna id dari session
        pengguna_id = session.get('pengguna_id')

        # mengambil description, nominal, dan date dari form
        description = request.form['description']
        nominal = request.form['nominal']
        date = request.form['date']

        if date == '':
            date = datetime.now().date()

        # mengambil total transaksi saat ini
        jumlah = str(transaksi.getCountTransaksiIdinDatabase())

        # mengatur lokasi penyimpanan dan nama file
        file_location = application.config['UPLOAD_FOLDER'] + '/' + 'nota_' + jumlah
        
        if description != '' and nominal != '':
            try:
                nominal = int(nominal)
                try:
                    nota = request.files['nota']

                    if nota.filename != '':
                        nota.save(file_location)

                    filename = 'nota_' + jumlah

                    data = (pengguna_id, date, description, 0, nominal, filename)
                    print(data)
                    transaksi.insertDataTransaksi(data)
                    session['pesan'] = 'add_spending_berhasil'
                    return redirect(url_for('index'))
                except:
                    return render_template('add_spending.html', saldo=saldo, name=name , gagal=True)
            except:
                return render_template('add_spending.html', saldo=saldo, name=name , bukan_angka=True)
        else:
            return render_template('add_spending.html', saldo=saldo, name=name , kosong=True)
    return render_template('add_spending.html', saldo=saldo, name=name)

@application.route('/profile')
@check_session_user
def profile():
    data = pengguna.ambilDataUserbyId(session.get('pengguna_id'))

    saldo = balance_count()[3]

    if session.get('pesan') == 'update_profil_berhasil':
        session.pop('pesan', '')
        return render_template('profile.html', data=data, saldo=saldo, berhasil=True)

    return render_template('profile.html', data=data, saldo=saldo)

@application.route('/edit_profile', methods=['GET', 'POST'])
@check_session_user
def edit_profile():
    data = pengguna.ambilDataUserbyId(session.get('pengguna_id'))

    if request.method == 'POST':
        pengguna_id = session.get('pengguna_id')
        name = request.form['name']
        username = request.form['username']
        new_password = request.form['new-password']
        renew_password = request.form['renew-password']
        bio = request.form['bio']
        if name != '' and username != '' and new_password != '' and renew_password != '':
            if len(name) > 3 and len(username) > 3 and len(new_password) > 3 and len(renew_password) > 3:
                if new_password == renew_password:
                    try:
                        data = (name, username, new_password, bio, pengguna_id)
                        pengguna.updateProfil(data)
                        session['name'] = name
                        session['pesan'] = 'update_profil_berhasil'
                        return redirect(url_for('profile'))
                    except:
                        return render_template('edit_profile.html', data=data, gagal=True)
                else:
                    return render_template('edit_profile.html', data=data, tidak_cocok=True)
            else:
                return render_template('edit_profile.html', data=data, kurang=True)
        else:
            return render_template('edit_profile.html', data=data, kosong=True)

    return render_template('edit_profile.html', data=data)

@application.route('/edit_transaction/<no>', methods=['GET', 'POST'])
@check_session_user
def edit_transaction(no):
    data = transaksi.ambilSatuDataTransaksi(no)
    print(data)

    saldo = balance_count()[3]

    if request.method == 'POST':
        # mengambil pengguna id dari session
        transaksi_id = data[0]

        # mengambil description, nominal, dan file nota dari form
        description = request.form['description']
        nominal = request.form['nominal']
        date = request.form['date']

        if date == '':
            date = data[3]

        # mengambil total transaksi saat ini
        jumlah = str(transaksi.getCountTransaksiIdinDatabase())

        # mengatur lokasi penyimpanan dan nama file
        file_location = application.config['UPLOAD_FOLDER'] + '/' + data[6]
        
        if description != '' and nominal != '':
            try:
                nominal = int(nominal)
                try:
                    nota = request.files['nota']

                    if nota.filename != '':
                        nota.save(file_location)

                    filename = data[6]

                    # jika yang 0 adalah pengeluaran maka insert data pemasukan
                    if data[2] == 0:
                        data = (description, nominal, 0, filename, date, transaksi_id)

                    # jika yang 0 adalah pemasukan maka insert data pengeluaran
                    elif data[1] == 0:
                        data = (description, 0, nominal, filename, date, transaksi_id)
                    
                    print(data)
                    transaksi.updateTransaksi(data)

                    session['pesan'] = 'edit_transaksi_berhasil'
                    return redirect(url_for('index'))
                except:
                    return render_template('edit_transaction.html', gagal=True, saldo=saldo, data=data)
            except:
                return render_template('edit_transaction.html', bukan_angka=True, saldo=saldo, data=data)
        else:
            return render_template('edit_transaction.html', kosong=True, saldo=saldo, data=data)
    return render_template('edit_transaction.html', data=data, saldo=saldo)

@application.route('/delete_transaksi/<no>')
def delete_transaksi(no):
    transaksi.deleteTransaksi(no)
    session['pesan'] = 'delete_transaksi_berhasil'
    return redirect(url_for('index'))

@application.route('/delete_user/<no>')
def delete_user(no):
    transaksi.deleteTransaksiWherePenggunaId(no)
    pengguna.deleteUser(no)
    session['pesan'] = 'delete_user_berhasil'
    return redirect(url_for('dashboard_admin'))

@application.route('/logout')
def logout():
    session.pop('pengguna_id', '')
    session.pop('name', '')
    session.pop('role', '')
    return redirect(url_for('login'))

if __name__ == '__main__':
    application.run(debug=True)