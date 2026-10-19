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

# Función auxiliar para actualizar el contador del carrito en la sesión
def actualizar_contador_carrito(id_usuario):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT SUM(cantidad) FROM carrito WHERE id_usuario = %s", (id_usuario,))
        resultado = cursor.fetchone()
        cursor.close()
        session['total_items'] = int(resultado[0]) if resultado and resultado[0] is not None else 0
    except Exception:
        session['total_items'] = 0

@app.route('/')
def inicio():
    nombre_usuario = session.get('nombre')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id, nombre, descripcion, precio, stock, imagen, tipo, material FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    
    if "id" in session:
        actualizar_contador_carrito(session["id"])
        
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
    return render_template('cliente/login.html')

@app.route('/crear')
def crear():
    # 1. Obtener la página actual desde la URL (por defecto la página 1)
    pagina = request.args.get("pagina", 1, type=int)
    registros_por_pagina = 4

    offset = (pagina - 1) * registros_por_pagina

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # 2. Contar total de registros
    cursor.execute("SELECT COUNT(*) as total FROM productos")
    res_total = cursor.fetchone()
    total_registros = res_total['total'] if res_total else 0

    # 3. Obtener solo los 5 productos de la página actual
    cursor.execute("""
        SELECT * FROM productos
        LIMIT %s OFFSET %s
    """, (registros_por_pagina, offset))

    productos_bd = cursor.fetchall()
    cursor.close()

    # 4. Calcular cuántas páginas hay en total
    total_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina if total_registros > 0 else 1

    # 5. IMPORTANTE: Enviar pagina y total_paginas a render_template
    return render_template(
        'admin/crear.html', 
        productos=productos_bd,
        pagina=pagina,
        total_paginas=total_paginas
    )

@app.route('/crear_cliente')
def crear_cliente():
    pagina = request.args.get("pagina", 1, type=int)
    registros_por_pagina = 7
    offset = (pagina - 1) * registros_por_pagina

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Total de clientes
    cursor.execute("SELECT COUNT(*) as total FROM clientes")
    res_total = cursor.fetchone()
    total_registros = res_total['total'] if res_total else 0

    # Clientes con limit y offset
    cursor.execute("""
        SELECT * FROM clientes
        LIMIT %s OFFSET %s
    """, (registros_por_pagina, offset))
    
    clientes_bd = cursor.fetchall()
    cursor.close()

    total_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina if total_registros > 0 else 1

    return render_template(
        'admin/crear_cliente.html', 
        clientes=clientes_bd,
        pagina=pagina,
        total_paginas=total_paginas
    )
@app.route('/registrar_cliente', methods=['POST'])
def registrar_cliente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['email']
        telefono = request.form['telefono']

        cursor = mysql.connection.cursor()
        
        # Insertar el nuevo cliente en la base de datos
        cursor.execute("""
            INSERT INTO clientes (nombre, correo, telefono, estado, fecha_creacion)
            VALUES (%s, %s, %s, 'Activo', NOW())
        """, (nombre, correo, telefono))
        
        mysql.connection.commit()
        cursor.close()

        flash('Cliente registrado exitosamente')
        return redirect('/crear_cliente')

@app.route('/editar_cliente/<int:id>')
def editar_cliente(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM clientes WHERE id = %s", (id,))
    cliente = cursor.fetchone()
    cursor.close()

    if not cliente:
        flash("El cliente no fue encontrado.")
        return redirect('/crear_cliente')

    return render_template('admin/editar_cliente.html', cliente=cliente)


@app.route('/actualizar_cliente/<int:id>', methods=['POST'])
def actualizar_cliente(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['email']
        telefono = request.form['telefono']

        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE clientes 
            SET nombre = %s, correo = %s, telefono = %s 
            WHERE id = %s
        """, (nombre, correo, telefono, id))
        
        mysql.connection.commit()
        cursor.close()

        flash('Cliente actualizado correctamente')
        return redirect('/crear_cliente')

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
        "SELECT id, nombre, contraseña, rol FROM usuarios WHERE correo = %s",
        (correo,) 
    )
    resultado = cursor.fetchone()
    cursor.close()

    if resultado is None:
        flash('El usuario no existe', 'error')
        return redirect('/login')
        
    id_usuario, nombre_usuario, contraseña_hash, rol_usuario = resultado

    if check_password_hash(contraseña_hash, password):
        session["id"] = id_usuario
        session["rol"] = rol_usuario
        session['nombre'] = nombre_usuario
        
        actualizar_contador_carrito(id_usuario)
        flash(f'¡Bienvenido de nuevo, {nombre_usuario}!', 'exito')

        if rol_usuario == "admin":
            return redirect('/admin')
        else:
            return redirect('/catalogo')

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
@app.route("/editar_producto/<int:id>", methods=["GET", "POST"])
def editar_producto(id):
    # USAR DictCursor para que el HTML reconozca producto.id, producto.nombre, etc.
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == "POST":
        # 1. Capturar TODOS los campos del formulario
        nombre = request.form["nombre"]
        tipo = request.form["tipo"]
        material = request.form["material"]
        descripcion = request.form["descripcion"]
        precio = request.form["precio"]
        stock = request.form["stock"]
        imagen = request.files.get("imagen")

        try:
            # 2. Verificar si el usuario subió una nueva imagen
            if imagen and imagen.filename != "":
                # Obtener la imagen anterior
                cursor.execute("SELECT imagen FROM productos WHERE id=%s", (id,))
                resultado = cursor.fetchone()
                imagen_anterior = resultado['imagen'] if resultado else None

                nombre_imagen = secure_filename(imagen.filename)
                ruta_carpeta = os.path.join(app.root_path, "static", "img", "productos")

                # Eliminar la imagen anterior si existe y no es la por defecto
                if imagen_anterior and imagen_anterior != "default.png":
                    archivo_anterior = os.path.join(ruta_carpeta, imagen_anterior)
                    if os.path.exists(archivo_anterior):
                        os.remove(archivo_anterior)

                # Guardar la nueva imagen
                imagen.save(os.path.join(ruta_carpeta, nombre_imagen))

                # Actualizar incluyendo la nueva imagen y todos los campos
                cursor.execute("""
                    UPDATE productos
                    SET nombre=%s, tipo=%s, material=%s, stock=%s, precio=%s, descripcion=%s, imagen=%s
                    WHERE id=%s
                """, (nombre, tipo, material, stock, precio, descripcion, nombre_imagen, id))
            else:
                # Actualizar los datos SIN modificar la imagen
                cursor.execute("""
                    UPDATE productos
                    SET nombre=%s, tipo=%s, material=%s, stock=%s, precio=%s, descripcion=%s
                    WHERE id=%s
                """, (nombre, tipo, material, stock, precio, descripcion, id))

            mysql.connection.commit()
            flash("Producto actualizado correctamente", "success")

        except Exception as e:
            flash(f"Error al actualizar producto: {e}", "error")

        finally:
            cursor.close()

        return redirect("/crear")

    # Si el método es GET, cargamos los datos del producto
    cursor.execute("SELECT * FROM productos WHERE id=%s", (id,))
    producto = cursor.fetchone()
    cursor.close()

    return render_template("admin/editar_producto.html", producto=producto)

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

    try:
        ext = imagen.filename.rsplit('.', 1)[1].lower()
        nombre_imagen = f"{uuid.uuid4().hex}.{ext}"
        ruta_carpeta = os.path.join(app.root_path, "static", "img", "productos")
        os.makedirs(ruta_carpeta, exist_ok=True)
        imagen.save(os.path.join(ruta_carpeta, nombre_imagen))

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

# CATÁLOGO Y CARRITO

@app.route("/catalogo")
def listaCatalogo():
    if "id" in session:
        actualizar_contador_carrito(session["id"])

    # Capturar el término de búsqueda de la URL (ej. ?busqueda=piercing)
    busqueda = request.args.get('busqueda', '', type=str)

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if busqueda:
        # Si hay algo escrito en el buscador, filtramos los productos
        query = "SELECT * FROM productos WHERE nombre LIKE %s OR tipo LIKE %s OR material LIKE %s OR descripcion LIKE %s"
        param_busqueda = f"%{busqueda}%"
        cursor.execute(query, (param_busqueda, param_busqueda, param_busqueda, param_busqueda))
    else:
        # Si está vacío, mostramos todos los productos con normalidad
        cursor.execute("SELECT * FROM productos")

    productos = cursor.fetchall()
    cursor.close()

    return render_template('cliente/catalogo.html', productos=productos, busqueda=busqueda)

@app.route("/agregarCarrito/<int:id_producto>", methods=["POST"])
def agregar_carrito(id_producto):
    if "id" not in session:
        return redirect("/login")

    id_usuario = session["id"]
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT id, cantidad FROM carrito
        WHERE id_usuario=%s AND id_producto=%s
    """, (id_usuario, id_producto))
    existe = cursor.fetchone()

    if existe:
        cursor.execute("""
            UPDATE carrito SET cantidad = cantidad + 1
            WHERE id_usuario=%s AND id_producto=%s
        """, (id_usuario, id_producto))
    else:
        cursor.execute("""
            INSERT INTO carrito(id_usuario, id_producto, cantidad)
            VALUES(%s, %s, 1)
        """, (id_usuario, id_producto))

    mysql.connection.commit()
    cursor.close()

    actualizar_contador_carrito(id_usuario)
    flash("Producto agregado al carrito", "success")
    return redirect(request.referrer or "/catalogo")
@app.route("/actualizar_cantidad/<int:id_carrito>/<string:accion>")
def actualizar_cantidad(id_carrito, accion):
    if "id" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor()

    if accion == "sumar":
        cursor.execute("UPDATE carrito SET cantidad = cantidad + 1 WHERE id = %s", (id_carrito,))
    elif accion == "restar":
        cursor.execute("SELECT cantidad FROM carrito WHERE id = %s", (id_carrito,))
        res = cursor.fetchone()
        if res and res[0] > 1:
            cursor.execute("UPDATE carrito SET cantidad = cantidad - 1 WHERE id = %s", (id_carrito,))
        else:
            # Si la cantidad es 1 y presiona '-', eliminamos el ítem
            cursor.execute("DELETE FROM carrito WHERE id = %s", (id_carrito,))

    mysql.connection.commit()
    cursor.close()

    actualizar_contador_carrito(session["id"])
    return redirect("/carrito")

@app.route("/carrito")
def carrito():
    if "id" not in session:
        return redirect("/login")

    id_usuario = session["id"]
    actualizar_contador_carrito(id_usuario)

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT c.id, p.id, p.nombre, p.precio, c.cantidad, (p.precio * c.cantidad) subtotal, p.imagen, p.material
        FROM carrito c
        INNER JOIN productos p ON c.id_producto=p.id
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
    cursor.execute("DELETE FROM carrito WHERE id=%s", (id_carrito,))
    mysql.connection.commit()
    cursor.close()

    if "id" in session:
        actualizar_contador_carrito(session["id"])

    flash("Producto eliminado", "success")
    return redirect("/carrito")

if __name__ == '__main__':
    app.run(debug=True)