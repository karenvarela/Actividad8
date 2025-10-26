from flask import Flask, request, jsonify
import mysql.connector

# Configuración de la conexión a MySQL
db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "contrasena",
    "database": "testdb",
    "port": 3306
}

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route("/usuarios", methods=["GET"])
def get_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuario")
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(usuarios)

@app.route("/usuarios/<int:id_usuario>", methods=["GET"])
def get_usuario(id_usuario):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuario WHERE id_usuario = %s", (id_usuario,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()
    if usuario:
        return jsonify(usuario)
    return jsonify({"error": "Usuario no encontrado"}), 404

@app.route("/usuarios", methods=["POST"])
def create_usuario():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuario (nombre_usuario, apellido_usuario, email_usuario) VALUES (%s, %s)", 
                   (data["nombre_usuario"], data["apellido_usuario"], data["email_usuario"]))
    conn.commit()
    usuario_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"id_usuario": usuario_id, "message": "Usuario creado"})

@app.route("/usuarios/<int:id_usuario>", methods=["PUT"])
def update_usuario(id_usuario):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE usuario SET nombre_usuario=%s, apellido_usuario=%s, email_usuario=%s WHERE id_usuario=%s",
                   (data["nombre_usuario"], data["apellido_usuario"], data["email_usuario"], id_usuario))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Usuarrio actualizado"})

@app.route("/usuarios/<int:id_usuario>", methods=["DELETE"])
def delete_usuario(id_usuario):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuario WHERE id_usuario=%s", (id_usuario,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Usuario eliminado"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
