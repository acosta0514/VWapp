from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_mysqldb import MySQL, MySQLdb
import bcrypt


app = Flask(__name__)

# Connect Mysql
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bancodb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# settings


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/new_register', methods=['GET','POST'])
def new_register():

    if request.method == 'GET':
        return render_template('register.html')
    else:
        name = request.form['nombre']
        apPaterno = request.form['lastname']
        apMaterno = request.form['appMaterno']
        mail = request.form['mail']
        psw = request.form['psw'].encode('utf-8')

        hash_psw = bcrypt.hashpw(psw, bcrypt.gensalt())        
        cursor = mysql.connection.cursor()

        cursor.execute("SELECT mail FROM users WHERE mail=\'%s\'"%mail)
        data = cursor.fetchone()

        if data != mail: 
            cursor.execute('INSERT INTO users (nombre, appPaterno, appMaterno, psw, mail) VALUES (%s,%s,%s,%s,%s)',(name,apPaterno,apMaterno,hash_psw,mail))
            mysql.connection.commit()
            cursor.close()
            flash('Registro agregado correctamente')
            session['nombre'] = name
            session['mail'] = mail
            return redirect(url_for('panel'))
        else:
            flash('el correo '+mail+' ya existe, verificalo.')
            return redirect(url_for('register'))

@app.route('/panel')
def panel():
    return render_template('panel.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        mail = request.form['mail']
        psw = request.form['psw'].encode('utf-8')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE mail=%s",(mail,))
        data = cursor.fetchone()
        cursor.close()
        
        if len(data) > 0:
            prueba = bcrypt.hashpw(psw, data["psw"].encode('utf-8'))
            if prueba != data["psw"].encode('utf-8'):
                session['nombre'] = data['nombre']
                session['mail'] = data['mail']
                return render_template('panel.html') 
            else:
                flash('Contraseña incorrecta')
                return redirect(url_for('index')) 
        else:
            flash('Verifique contraseña o el usuario no existe')
            return redirect(url_for('index'))
    else:
        return render_template('panel.html')
            
@app.route('/logout')
def logout():
    session.clear()
    return render_template('home.html')

if __name__ == '__main__':
    app.secret_key = 'm1s3cr37k3y@45'
    app.run(debug=True)