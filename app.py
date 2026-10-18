from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database.conexion import mysql
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import MySQLdb.cursors
import uuid
import os 

app = Flask(__name__)
app.secret_key = 'wwwwertyuio98764rtyuk'

app.config['MYSQL_HOST'] = Config.MYSQL_HOST
app.config['MYSQL_USER'] = Config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = Config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = Config.MYSQL_DB
 
mysql.init_app(app)
 
@app.route('/')
def inicio():
    nombre_usuario = session.get('nombre')
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id, nombre, descripcion, precio, stock, imagen FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    
    return render_template('index.html', nombre=nombre_usuario, productos=productos)

@app.route('/registro')
def registro():
    return render_template('cliente/registro.html')

@app.route('/admin')
def admin():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM productos")
    productos_bd = cursor.fetchall() 
    cursor.close()
    
    return render_template('admin/admin.html', productos=productos_bd) 

@app.route('/login')
def login():
    usuario = session.get('correo')
    if usuario:
            session['user_id'] = usuario['id']
            session['nombre'] = usuario['nombre']
            print("👉 LOGIN EXITOSO. Sesión actual:", session) # <--- Añade esto
            return redirect('/catalogo')
    return render_template('cliente/login.html')
@app.route('/crear')
def crear():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM productos")
    productos_bd = cursor.fetchall() 
    cursor.close()
    
    return render_template('admin/crear.html', productos=productos_bd)

@app.route('/crear_cliente')
def crear_clienete():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM clientes")
    clientes_bd = cursor.fetchall() 
    cursor.close()
    
    return render_template('admin/crear_cliente.html', clientes=clientes_bd)

@app.route('/cerrar_sesion')
def cerrar_sesion():
    session.clear() 
    return redirect('/login')

@app.route('/iniciar_sesion', methods=['POST'])
def iniciar_sesion():
    correo = request.form['correo']
    password = request.form['contraseña'] 

    cursor = mysql.connection.cursor()
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

        if rol_usuario == "admin":
            return redirect('/admin')
        else:
            return redirect('/')

    flash('Usuario o contraseña incorrectos', 'error')
    return redirect('/login')

@app.route('/eliminar_producto/<int:id>')
def eliminar_producto(id):
    try:
        cursor = mysql.connection.cursor()
        
        cursor.execute("SELECT imagen FROM productos WHERE id = %s", (id,))
        producto = cursor.fetchone()
        
        if producto and producto[0]:
            ruta_imagen = os.path.join(app.root_path, "static", "img", "productos", producto[0])
            if os.path.exists(ruta_imagen):
                os.remove(ruta_imagen)

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
    tipo = request.form['tipo']
    material = request.form['material']

    if not imagen or imagen.filename == '':
        flash('Debes seleccionar una imagen para el producto', 'error')
        return redirect('/crear')

    if not archivo_permitido(imagen.filename):
        flash('Formato no permitido. Solo se aceptan PNG, JPG, JPEG, GIF y WEBP.', 'error')
        return redirect('/crear')

    try:
        ext = imagen.filename.rsplit('.', 1)[1].lower()
        nombre_imagen = f"{uuid.uuid4().hex}.{ext}"

        ruta_carpeta = os.path.join(app.root_path, "static", "img", "productos")
        
        os.makedirs(ruta_carpeta, exist_ok=True)
        
        ruta_completa = os.path.join(ruta_carpeta, nombre_imagen)
        imagen.save(ruta_completa)

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO productos (nombre, tipo, material, descripcion, precio, stock, imagen) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (nombre, tipo, material, descripcion, precio, stock, nombre_imagen)
        )
        mysql.connection.commit()
        cursor.close()

        flash('Producto guardado correctamente', 'exito')

    except Exception as e:
        mysql.connection.rollback()
        flash(f'Ocurrió un error al guardar: {str(e)}', 'error')

    return redirect('/crear')

@app.route('/registrar_cliente', methods=['POST'])
def registrar_cliente():
    nombre = request.form.get("nombre")
    correo = request.form.get("email")
    telefono = request.form.get("telefono")

    if not nombre or not correo or not telefono:
        flash('Por favor, completa todos los campos obligatorios.', 'error')
        return redirect('/crear_cliente')

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            """
            INSERT INTO clientes (nombre, correo, telefono)
            VALUES (%s, %s, %s)
            """, (nombre, correo, telefono)
        )
        mysql.connection.commit()
        cursor.close()

        flash('Cliente guardado correctamente', 'exito')

    except Exception as e:
        mysql.connection.rollback()
        cursor.close()
        flash(f'Ocurrió un error al guardar: {str(e)}', 'error')

    return redirect('/crear_cliente')

@app.route('/eliminar_cliente/<int:id>')
def eliminar_cliente(id):
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM clientes WHERE id = %s", (id,))
        mysql.connection.commit()
        
        flash('Cliente eliminado correctamente', 'exito')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al eliminar el cliente: {str(e)}', 'error')
    finally:
        if cursor:
            cursor.close()

    return redirect('/crear_cliente')

@app.route("/cambiarImagenProducto/<int:id>")
def cambiar_imagen_producto(id):

    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT id, nombre, imagen FROM productos WHERE id=%s",
        (id,)
    )

    producto = cursor.fetchone()
    cursor.close()

    return render_template(
        "admin/cambiarImagenProducto.html",
        producto=producto
    )

@app.route("/actualizarImagenProducto/<int:id>", methods=["POST"])
def actualizar_imagen_producto(id):

    try:

        imagen = request.files.get("imagen")

        if not imagen or imagen.filename == "":
            flash("Debe seleccionar una imagen", "error")
            return redirect(f"/cambiarImagenProducto/{id}")

        cursor = mysql.connection.cursor()

        cursor.execute(
            "SELECT imagen FROM productos WHERE id=%s",
            (id,)
        )

        producto = cursor.fetchone()

        imagen_anterior = producto[0]

        nombre_imagen = secure_filename(imagen.filename)

        ruta = os.path.join(
            app.root_path,
            "static",
            "img",
            "productos"
        )

        # eliminar imagen anterior
        if imagen_anterior != "default.png":

            archivo_anterior = os.path.join(
                ruta,
                imagen_anterior
            )

            if os.path.exists(archivo_anterior):
                os.remove(archivo_anterior)

        # guardar nueva imagen
        imagen.save(
            os.path.join(ruta, nombre_imagen)
        )

        cursor.execute(
            "UPDATE productos SET imagen=%s WHERE id=%s",
            (nombre_imagen, id)
        )

        mysql.connection.commit()

        flash("Imagen actualizada correctamente", "success")

    except Exception as e:
        flash(f"Error: {e}", "error")

    finally:
        cursor.close()

    return redirect("/listarProducto")

# CARRITO DE COMPRAS

@app.route("/catalogo")
def listaCatalogo():

    cursor = mysql.connection.cursor()

    # Total de registros
    cursor.execute("SELECT COUNT(*) FROM productos")
    total_registros = cursor.fetchone()[0]

    # Productos de la página actual
    cursor.execute("""
        SELECT * FROM productos""")

    productos = cursor.fetchall()

    cursor.close()

    #total_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina

    return render_template(
        'cliente/catalogo.html',
        productos=productos
     #   pagina=pagina,
      #  total_paginas=total_paginas
    )

@app.route("/agregarCarrito/<int:id_producto>", methods=["POST"])
def agregar_carrito(id_producto):

    #if "id" not in session:
       # return redirect("/login")

    id_usuario = session["id"]

    cursor = mysql.connection.cursor()

    # Verificar si ya existe

    cursor.execute("""
        SELECT id, cantidad
        FROM carrito
        WHERE id_usuario=%s
        AND id_producto=%s
    """, (id_usuario, id_producto))

    existe = cursor.fetchone()

    if existe:

        cursor.execute("""
            UPDATE carrito
            SET cantidad = cantidad + 1
            WHERE id_usuario=%s
            AND id_producto=%s
        """, (id_usuario, id_producto))

    else:

        cursor.execute("""
            INSERT INTO carrito(
                id_usuario,
                id_producto,
                cantidad
            )
            VALUES(%s,%s,1)
        """, (id_usuario, id_producto))

    mysql.connection.commit()
    cursor.close()

    flash("Producto agregado al carrito", "success")

    return redirect(request.referrer)

@app.route("/carrito")
def carrito():

    if "user_id" not in session:
        print("❌ Alerta: No hay 'user_id' en la sesión. Redirigiendo al login...")
        return redirect("/login")
    # Usamos la misma clave con la que guardaste el login ('user_id')
    id_usuario = session["user_id"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            c.id,
            p.id,
            p.nombre,
            p.precio,
            c.cantidad,
            (p.precio * c.cantidad) subtotal,
            p.imagen

        FROM carrito c

        INNER JOIN productos p
            ON c.id_producto=p.id

        WHERE c.id_usuario=%s
    """, (id_usuario,))

    productos = cursor.fetchall()

    total = sum(float(item[5]) for item in productos)

    cursor.close()

    return render_template(
        "cliente/carrito.html",
        productos=productos,
        total=total
    )
@app.route("/eliminarDelCarrito/<int:id_carrito>")
def eliminar_del_carrito(id_carrito):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        DELETE FROM carrito
        WHERE id=%s
    """, (id_carrito,))

    mysql.connection.commit()

    cursor.close()

    flash("Producto eliminado", "success")

    return redirect("/carrito")

@app.route("/finalizarCompra")
def finalizar_compra():

    id_usuario = session["id"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            p.id,
            p.precio,
            c.cantidad

        FROM carrito c

        INNER JOIN productos p
            ON p.id=c.id_producto

        WHERE c.id_usuario=%s
    """, (id_usuario,))

    carrito = cursor.fetchall()

    if not carrito:
        flash("El carrito está vacío", "error")
        return redirect("/carrito")

    total = sum(item[1] * item[2] for item in carrito)

    cursor.execute("""
        INSERT INTO pedidos(
            id_usuariofK,
            total,
            estado
        )
        VALUES(%s,%s,'pendiente')
    """, (id_usuario, total))

    id_pedido = cursor.lastrowid

    for producto in carrito:

        id_producto = producto[0]
        precio = producto[1]
        cantidad = producto[2]

        subtotal = precio * cantidad

        cursor.execute("""
            INSERT INTO detalle_pedido(
                id_pedido,
                id_producto,
                cantidad,
                precio_unitario,
                subtotal
            )
            VALUES(%s,%s,%s,%s,%s)
        """, (
            id_pedido,
            id_producto,
            cantidad,
            precio,
            subtotal
        ))

        cursor.execute("""
            UPDATE productos
            SET stock=stock-%s
            WHERE id=%s
        """, (
            cantidad,
            id_producto
        ))

    cursor.execute("""
        DELETE FROM carrito
        WHERE id_usuario=%s
    """, (id_usuario,))

    mysql.connection.commit()

    cursor.close()

    flash("Pedido generado correctamente", "success")

    return redirect("/")
if __name__ == '__main__':
    app.run(debug=True)