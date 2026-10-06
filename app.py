from flask import Flask, render_template, request, redirect, session, flash
from config import Config
from database.conexion import mysql
from werkzeug.security import (generate_password_hash, check_password_hash)
from werkzeug.utils import secure_filename
import MySQLdb.cursors
import uuid
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
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM productos")
    productos_bd = cursor.fetchall() 
    cursor.close()
    
    # Se añade productos=productos_bd
    return render_template('admin/admin.html', productos=productos_bd) 
@app.route('/login')
def login():
    return render_template('cliente/login.html')
@app.route('/crear')
def crear():
    # Usamos DictCursor para que Jinja2 pueda acceder por nombre: {{ producto.nombre }}, etc.
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM productos")
    productos_bd = cursor.fetchall() 
    cursor.close()
    
    # IMPORTANTE: Pasamos productos=productos_bd a la plantilla
    return render_template('admin/crear.html', productos=productos_bd)
@app.route('/crear_cliente')
def crear_clienete():
    # Creamos el cursor con DictCursor
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM clientes")
    clientes_bd = cursor.fetchall() 
    cursor.close()
    
    # Pasamos la variable clientes a la plantilla (revisa que el nombre del archivo sea correcto)
    return render_template('admin/crear_cliente.html', clientes=clientes_bd)
    return render_template('admin/crear.html')
@app.route('/cerrar_sesion')
def cerrar_sesion():
    session.clear() 
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
@app.route('/eliminar_producto/<int:id>')
def eliminar_producto(id):
    try:
        cursor = mysql.connection.cursor()
        
        # 1. Obtener el nombre de la imagen para borrarla del disco
        cursor.execute("SELECT imagen FROM productos WHERE id = %s", (id,))
        producto = cursor.fetchone()
        
        if producto and producto[0]:
            ruta_imagen = os.path.join(app.root_path, "static", "img", "productos", producto[0])
            if os.path.exists(ruta_imagen):
                os.remove(ruta_imagen)

        # 2. Eliminar el registro en la BD
        cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
        mysql.connection.commit()
        cursor.close()

        flash('Producto eliminado correctamente', 'exito')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al eliminar el producto: {str(e)}', 'error')

    return redirect('/crear')

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

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
def archivo_permitido(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/guardar_producto', methods=['POST'])
def guardar_producto():
    nombre = request.form.get("nombre")
    precio = request.form.get("precio")
    imagen = request.files.get("imagen")
    descripcion = request.form.get('descripcion')  
    stock = request.form.get('stock')

    if not imagen or imagen.filename == '':
        flash('Debes seleccionar una imagen para el producto', 'error')
        return redirect('/')

    if not archivo_permitido(imagen.filename):
        flash('Formato no permitido. Solo se aceptan PNG, JPG, JPEG, GIF y WEBP.', 'error')
        return redirect('/')

    try:
        ext = imagen.filename.rsplit('.', 1)[1].lower()
        nombre_imagen = f"{uuid.uuid4().hex}.{ext}"

        ruta_carpeta = os.path.join(app.root_path, "static", "img", "productos")
        

        os.makedirs(ruta_carpeta, exist_ok=True)
        
        ruta_completa = os.path.join(ruta_carpeta, nombre_imagen)
        imagen.save(ruta_completa)


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

    except Exception as e:
        # Si falla la BD o el guardado, se revierten los cambios en MySQL
        mysql.connection.rollback()
        flash(f'Ocurrió un error al guardar: {str(e)}', 'error')

    return redirect('/crear')

if __name__ == '__main__':
    app.run(debug=True)