from flask import Flask, request, jsonify
import pymysql.cursors

app = Flask(__name__)

# --- Configuración de la Base de Datos ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'contrasena',
    'database': 'testdb',
    'port': 3306,
    # El cursor de diccionario es útil para obtener resultados como diccionarios
    'cursorclass': pymysql.cursors.DictCursor
}

def obtener_conexion():
    """Establece y retorna la conexión a la base de datos."""
    try:
        return pymysql.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# ----------------------------------------------------------------------
#                             OPERACIONES CRUD
# ----------------------------------------------------------------------

## 2.1. CREATE: Crear un Nuevo Usuario (POST /usuarios)
@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    """Servicio para crear un nuevo usuario."""
    data = request.get_json()
    if not data or 'nombre_usuario' not in data or 'apellido_usuario' not in data or 'email_usuario' not in data:
        return jsonify({"mensaje": "Faltan datos requeridos (nombre_usuario, apellido_usuario, email_usuario)"}), 400

    nombre = data['nombre_usuario']
    apellido = data['apellido_usuario']
    email = data['email_usuario']
    
    conexion = obtener_conexion()
    if conexion is None:
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500

    try:
        with conexion.cursor() as cursor:
            sql = "INSERT INTO usuario (nombre_usuario, apellido_usuario, email_usuario) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nombre, apellido, email))
            conexion.commit()
            nuevo_id = cursor.lastrowid
            return jsonify({"mensaje": "Usuario creado con éxito", "id_usuario": nuevo_id}), 201
    except pymysql.Error as e:
        conexion.rollback()
        # Manejar la violación de la restricción UNIQUE para email_usuario
        if e.args[0] == 1062: # Código de error de duplicado en MySQL
            return jsonify({"mensaje": f"Error: El email '{email}' ya existe."}), 409
        return jsonify({"mensaje": f"Error al crear usuario: {e}"}), 500
    finally:
        conexion.close()

# ----------------------------------------------------------------------

## 2.2. READ (ALL): Obtener todos los Usuarios (GET /usuarios)
@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    """Servicio para obtener la lista de todos los usuarios."""
    conexion = obtener_conexion()
    if conexion is None:
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500
    
    try:
        with conexion.cursor() as cursor:
            sql = "SELECT id_usuario, nombre_usuario, apellido_usuario, email_usuario FROM usuario"
            cursor.execute(sql)
            usuarios = cursor.fetchall()
            return jsonify(usuarios), 200
    except pymysql.Error as e:
        return jsonify({"mensaje": f"Error al listar usuarios: {e}"}), 500
    finally:
        conexion.close()

# ----------------------------------------------------------------------

## 2.3. READ (ONE): Obtener un Usuario por ID (GET /usuarios/<int:id>)
@app.route('/usuarios/<int:id>', methods=['GET'])
def obtener_usuario(id):
    """Servicio para obtener un usuario por su ID."""
    conexion = obtener_conexion()
    if conexion is None:
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500

    try:
        with conexion.cursor() as cursor:
            sql = "SELECT id_usuario, nombre_usuario, apellido_usuario, email_usuario FROM usuario WHERE id_usuario = %s"
            cursor.execute(sql, (id,))
            usuario = cursor.fetchone()
            
            if usuario:
                return jsonify(usuario), 200
            else:
                return jsonify({"mensaje": f"Usuario con ID {id} no encontrado"}), 404
    except pymysql.Error as e:
        return jsonify({"mensaje": f"Error al obtener usuario: {e}"}), 500
    finally:
        conexion.close()

# ----------------------------------------------------------------------

## 2.4. UPDATE: Actualizar un Usuario (PUT /usuarios/<int:id>)
@app.route('/usuarios/<int:id>', methods=['PUT'])
def actualizar_usuario(id):
    """Servicio para actualizar los datos de un usuario existente."""
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "No se enviaron datos para actualizar"}), 400

    # Se permite actualizar parcialmente, solo los campos que vengan en el JSON
    updates = []
    valores = []
    
    if 'nombre_usuario' in data:
        updates.append("nombre_usuario = %s")
        valores.append(data['nombre_usuario'])
    if 'apellido_usuario' in data:
        updates.append("apellido_usuario = %s")
        valores.append(data['apellido_usuario'])
    if 'email_usuario' in data:
        updates.append("email_usuario = %s")
        valores.append(data['email_usuario'])
    
    if not updates:
        return jsonify({"mensaje": "No se proporcionaron campos válidos para actualizar"}), 400

    valores.append(id) # El ID va al final para la cláusula WHERE
    
    conexion = obtener_conexion()
    if conexion is None:
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500

    try:
        with conexion.cursor() as cursor:
            sql = "UPDATE usuario SET " + ", ".join(updates) + " WHERE id_usuario = %s"
            filas_afectadas = cursor.execute(sql, tuple(valores))
            conexion.commit()

            if filas_afectadas == 0:
                # Se verifica si el usuario existía previamente
                cursor.execute("SELECT id_usuario FROM usuario WHERE id_usuario = %s", (id,))
                if cursor.fetchone() is None:
                    return jsonify({"mensaje": f"Usuario con ID {id} no encontrado"}), 404
                else:
                    return jsonify({"mensaje": "Usuario actualizado (sin cambios o datos duplicados)"}), 200
            
            return jsonify({"mensaje": "Usuario actualizado con éxito", "filas_afectadas": filas_afectadas}), 200
    except pymysql.Error as e:
        conexion.rollback()
        if e.args[0] == 1062: # Código de error de duplicado en MySQL para email_usuario
            return jsonify({"mensaje": f"Error: El email ya existe o es el mismo."}), 409
        return jsonify({"mensaje": f"Error al actualizar usuario: {e}"}), 500
    finally:
        conexion.close()

# ----------------------------------------------------------------------

## 2.5. DELETE: Eliminar un Usuario (DELETE /usuarios/<int:id>)
@app.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    """Servicio para eliminar un usuario por su ID."""
    conexion = obtener_conexion()
    if conexion is None:
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500

    try:
        with conexion.cursor() as cursor:
            sql = "DELETE FROM usuario WHERE id_usuario = %s"
            filas_eliminadas = cursor.execute(sql, (id,))
            conexion.commit()
            
            if filas_eliminadas > 0:
                return jsonify({"mensaje": f"Usuario con ID {id} eliminado con éxito", "filas_eliminadas": filas_eliminadas}), 200
            else:
                return jsonify({"mensaje": f"Usuario con ID {id} no encontrado"}), 404
    except pymysql.Error as e:
        conexion.rollback()
        return jsonify({"mensaje": f"Error al eliminar usuario: {e}"}), 500
    finally:
        conexion.close()

# ----------------------------------------------------------------------

if __name__ == '__main__':
    # Ejecutar la aplicación en modo debug para desarrollo
    app.run(debug=True)
