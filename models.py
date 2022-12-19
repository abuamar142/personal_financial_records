import pymysql
import config

database = cursor = None

class Pengguna():
    def __init__(self, pengguna_id=None, nama=None, username=None, password=None, role=None, bio=None,):
        self.pengguna_id = pengguna_id
        self.nama = nama
        self.username = username
        self.password = password
        self.role = role
        self.bio = bio

    def openDatabase(self):
        global database, cursor
        database = pymysql.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        cursor = database.cursor()

    def closeDatabase(self):
        global database, cursor
        database.close()

    def ambilDataUserbyId(self, pengguna_id):
        self.openDatabase()
        cursor.execute(
            "SELECT pengguna_id, nama, username, MD5(password), role, bio FROM pengguna WHERE pengguna_id='%s'" % pengguna_id
        )
        data_user = cursor.fetchone()
        self.closeDatabase()
        return data_user

    def ambilDataUser(self, username, password):
        self.openDatabase()
        cursor.execute(
            "SELECT * FROM pengguna WHERE username = '%s' AND password = MD5('%s') " % (username, password)
        )
        data_user = cursor.fetchone()
        self.closeDatabase()
        return data_user

    def ambilTotalUser(self):
        self.openDatabase()
        cursor.execute(
            "SELECT COUNT(pengguna_id) FROM pengguna WHERE role = 'user'"
        )
        total_user = cursor.fetchone()
        self.closeDatabase()
        return total_user[0]

    def ambilSemuaDataUserNotHaveTransaction(self):
        self.openDatabase()
        cursor.execute(
            "SELECT P.pengguna_id, P.nama, P.username, MD5(P.password) FROM pengguna P  LEFT JOIN transaksi T ON P.pengguna_id = T.pengguna_id WHERE T.transaksi_id IS NULL AND P.role = 'user'"
        )
        data_user = cursor.fetchall()
        self.closeDatabase()
        return data_user

    def ambilSemuaDataUserHaveTransaction(self):
        self.openDatabase()
        cursor.execute(
            "SELECT P.pengguna_id, P.nama, P.username, MD5(P.password), COUNT(T.transaksi_id) as jumlah_transaksi_user FROM pengguna P, transaksi T WHERE P.pengguna_id = T.pengguna_id and P.role = 'user' GROUP BY P.pengguna_id"
        )
        data_user = cursor.fetchall()
        self.closeDatabase()
        return data_user

    def insertDataUser(self, data):
        self.openDatabase()
        cursor.execute(
            "INSERT INTO pengguna (nama, username, password, role, bio) VALUES('%s', '%s', MD5('%s'), '%s', '%s')" % data
        )
        database.commit()
        self.closeDatabase

    def updateProfil(self, data):
        self.openDatabase()
        cursor.execute(
            "UPDATE pengguna SET nama='%s', username='%s' , password=MD5('%s') , bio='%s' WHERE pengguna_id='%s' " % data)
        database.commit()
        self.closeDatabase()

    def deleteUser(self, pengguna_id):
        self.openDatabase()
        cursor.execute(
            "DELETE FROM pengguna WHERE pengguna_id='%s'" % pengguna_id)
        database.commit()
        self.closeDatabase()

class Transaksi():
    def __init__(self, transaksi_id=None, pemasukan=None, pengeluaran=None, date=None, deskripsi=None, pengguna_id=None, upload_file=None):
        self.transaksi_id = transaksi_id
        self.pemasukan = pemasukan
        self.pengeluaran = pengeluaran
        self.date = date
        self.deskripsi = deskripsi
        self.pengguna_id = pengguna_id
        self.upload_file = upload_file
        
    def openDatabase(self):
        global database, cursor
        database = pymysql.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        cursor = database.cursor()

    def closeDatabase(self):
        global database, cursor
        database.close()

    def insertDataTransaksi(self, data):
        self.openDatabase()
        cursor.execute(
            "INSERT INTO transaksi (pengguna_id, date, deskripsi, pemasukan, pengeluaran, upload_file) VALUES('%s', NOW(), '%s', '%s', '%s', '%s')" % data
        )
        database.commit()
        self.closeDatabase

    def ambilSatuDataTransaksi(self, transaksi_id):
        self.openDatabase()
        cursor.execute(
            "SELECT * FROM transaksi WHERE transaksi_id = '%s'" % transaksi_id)
        data_user = cursor.fetchone()
        self.closeDatabase()
        return data_user

    def ambilDataTransaksi(self, pengguna_id):
        self.openDatabase()
        cursor.execute(
            "SELECT * FROM transaksi WHERE pengguna_id = '%s' ORDER BY date DESC" % pengguna_id)
        data_user = cursor.fetchall()
        self.closeDatabase()
        return data_user

    def updateTransaksi(self, data):
        self.openDatabase()
        cursor.execute(
            "UPDATE transaksi SET deskripsi='%s', pemasukan='%s', pengeluaran='%s', upload_file='%s' WHERE transaksi_id='%s' " % data
        )
        database.commit()
        self.closeDatabase()

    def deleteTransaksiWherePenggunaId(self, pengguna_id):
        self.openDatabase()
        cursor.execute(
            "DELETE FROM transaksi WHERE pengguna_id='%s'" % pengguna_id)
        database.commit()
        self.closeDatabase()

    def deleteTransaksi(self, transaksi_id):
        self.openDatabase()
        cursor.execute(
            "DELETE FROM transaksi WHERE transaksi_id='%s'" % transaksi_id)
        database.commit()
        self.closeDatabase()

    def getCountTransaksiIdinDatabase(self):
        self.openDatabase()
        cursor.execute(
            "SELECT COUNT(transaksi_id) FROM transaksi"
        )
        jumlah = cursor.fetchone()
        self.closeDatabase()
        return jumlah[0] + 1

    def getCountIncomebyUser(self, pengguna_id):
        self.openDatabase()
        cursor.execute(
            "SELECT SUM(pemasukan) FROM transaksi WHERE pengguna_id='%s'" % pengguna_id
        )
        income = cursor.fetchone()
        self.closeDatabase()
        return income[0]

    def getCountSpendingbyUser(self, pengguna_id):
        self.openDatabase()
        cursor.execute(
            "SELECT SUM(pengeluaran) FROM transaksi WHERE pengguna_id='%s'" % pengguna_id
        )
        spending = cursor.fetchone()
        self.closeDatabase()
        return spending[0]