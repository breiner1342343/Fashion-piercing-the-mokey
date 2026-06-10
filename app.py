from flask import Flask, request
from config import Config
from database.conexion import mysql

app = Flask(__name__)

@app.route('/')
def inicio():
    return "Sistema de ventas online"

@app.route('/guardar_cliente', methods=['POST'])
def guardar_cliente():
    nombre = request.form['nombre']
    correo = request.form['correo']
    telefono = request.form['telefono']
    cursor = mysql.connection.cursor()
    sql = """
INSERT INTO clientes(nombre, correo, telefono)
VALUES(%s, %s, %s)
"""
    datos = (nombre, correo, telefono)
    cursor.execute(sql, datos)
    mysql.connection.commit()
    cursor.close()
    return "Cliente guardado correctamente"

if __name__ == '__main__':
    app.run(debug=True)
