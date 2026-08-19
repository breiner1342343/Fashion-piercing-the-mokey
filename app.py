from flask import Flask, render_template, request, redirect, session, flash
from config import Config
from database.conexion import mysql
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb

app = Flask(__name__)
app.secret_key = 'wwwwertyuio98764rtyuk'
# Configuración MySQL
app.config['MYSQL_HOST'] = Config.MYSQL_HOST
app.config['MYSQL_USER'] = Config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = Config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = Config.MYSQL_DB
 
# Inicializar MySQL
mysql.init_app(app)
 
@app.route('/')
def inicio():
    nombre_usuario = session.get('nombre')
    return render_template('index.html', nombre=nombre_usuario)
 
@app.route('/registro')
def registro():
    return render_template('registro.html')
 
@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/cerrar_sesion')
def cerrar_sesion():
    session.pop('nombre', None) 
    return redirect('/')
@app.route('/iniciar_sesion', methods=['POST'])
def iniciar_sesion():
    correo = request.form['correo']
    password = request.form['contraseña'] 

    cursor = mysql.connection.cursor()

    cursor.execute(
        "SELECT contraseña FROM clientes WHERE correo = %s",
        (correo,) 
    )

    resultado = cursor.fetchone()
    cursor.close()

    if resultado is None:
        flash('El usuario no existe')
        return render_template('login.html')

    nombre_usuario, contraseña_hash = resultado

    if check_password_hash(contraseña_hash, password):
        session['nombre'] = nombre_usuario
        return redirect('/')

    flash('Usuario o contraseña incorrectos')
    return render_template('login.html')
@app.route('/guardar_cliente', methods=['POST'])
def guardar_cliente():
 
    nombre = request.form['nombre']
    correo = request.form['correo']
    telefono = request.form['telefono']
    password = request.form['contraseña']
    confirmar_password = request.form['confirmar_password']
   
    if password != confirmar_password:
        return "Las contraseñas no coinciden"
   
    password_hash = generate_password_hash(password)
   
    cursor = mysql.connection.cursor()
   
    sql = '''
    INSERT INTO clientes(nombre, correo, telefono, contraseña)
    VALUES(%s, %s, %s, %s)
    '''
 
    datos = (nombre, correo, telefono, password_hash)
 
    cursor.execute(sql, datos)
 
    mysql.connection.commit()
 
    cursor.close()
 
    return redirect('/login')
   
 
if __name__ == '__main__':
    app.run(debug=True)
