from flask import Flask, render_template, request, redirect, session, flash
from config import Config
from database.conexion import mysql
from werkzeug.security import (generate_password_hash, check_password_hash)
from werkzeug.utils import secure_filename
import os 

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
    return render_template('cliente/registro.html')
@app.route('/admin')
def admin():
    return render_template('admin/admin.html')
@app.route('/login')
def login():
    return render_template('cliente/login.html')

@app.route('/cerrar_sesion')
def cerrar_sesion():
    session.clear()  # Limpia toda la sesión (nombre, rol, etc.)
    return redirect('/login')

@app.route('/iniciar_sesion', methods=['POST'])
def iniciar_sesion():
    correo = request.form['correo']
    password = request.form['contraseña'] 

    cursor = mysql.connection.cursor()

    # 1. Se agrega 'rol' a la consulta SQL
    cursor.execute(
        "SELECT nombre, contraseña, rol FROM usuarios WHERE correo = %s",
        (correo,) 
    )

    resultado = cursor.fetchone()
    cursor.close()

    if resultado is None:
        flash('El usuario no existe', 'error')
        return redirect('/login')

    # 2. Desempaquetado correcto de los 3 datos
    nombre_usuario, contraseña_hash, rol_usuario = resultado

    if check_password_hash(contraseña_hash, password):
        session["rol"] = rol_usuario
        session['nombre'] = nombre_usuario
        
        flash(f'¡Bienvenido de nuevo, {nombre_usuario}!', 'exito')

        # 3. Redirección condicional según el rol
        if rol_usuario == "admin":
            return redirect('/admin')  # Asegúrate de tener esta ruta creada
        else:
            return redirect('/')

    flash('Usuario o contraseña incorrectos', 'error')
    return redirect('/login')

@app.route('/guardar_cliente', methods=['POST'])
def guardar_cliente():
    nombre = request.form['nombre']
    correo = request.form['correo']
    telefono = request.form['telefono']
    password = request.form['contraseña']
    confirmar_password = request.form['confirmar_password']
   
    if password != confirmar_password:
        flash('Las contraseñas no coinciden', 'error')
        return redirect('/registro')
   
    password_hash = generate_password_hash(password)
   
    cursor = mysql.connection.cursor()
   
    sql = '''
    INSERT INTO usuarios (nombre, correo, telefono, contraseña)
    VALUES(%s, %s, %s, %s)
    '''
 
    datos = (nombre, correo, telefono, password_hash)
    cursor.execute(sql, datos)
    mysql.connection.commit()
    cursor.close()
 
    flash('Registro exitoso. Inicia sesión.', 'exito')
    return redirect('/login')

@app.route('/guardar_producto', methods=['POST'])
def guardar_producto():
    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]
    precio = request.form["precio"]
    stock = request.form["stock"]
    imagen = request.files["imagen"]
    
    nombre_imagen = secure_filename(imagen.filename)

    ruta = os.path.join(app.root_path, "static", "img", "productos", nombre_imagen)
    imagen.save(ruta)

    cursor = mysql.connection.cursor()
    cursor.execute(
        """
        INSERT INTO productos(nombre, descripcion, precio, stock, imagen)
        VALUES(%s, %s, %s, %s, %s)
        """, (nombre, descripcion, precio, stock, nombre_imagen)
    )

    mysql.connection.commit()
    cursor.close()

    flash('Producto guardado correctamente', 'exito')
    return redirect('/')  # 4. Retorno obligatorio para evitar el TypeError

if __name__ == '__main__':
    app.run(debug=True)