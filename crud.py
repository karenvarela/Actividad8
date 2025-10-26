# pip install mysql-connector-python flask flask-cors requests
import mysql.connector

# Configurar conexión
conn = mysql.connector.connect(
    host="127.0.0.1",  # Docker expone en localhost
    user="root",
    password="contrasena",
    database="testdb",
    port=3306  # Puerto mapeado en Docker
)
cursor = conn.cursor()

# Crear un usuario
def create_usuario (nombre_usuario, apellido_usuario, email_usuario):
    cursor.execute("INSERT INTO usuario (nombre_usuario, apellido_usuario, email_usuario) VALUES (%s, %s)", 
                   (nombre_usuario, apellido_usuario, email_usuario)
    conn.commit()

# Leer todos los usuarios
def read_usuarios():
    cursor.execute("SELECT * FROM usuario")
    return cursor.fetchall()

# Actualizar un usuario
def update_jedi(id_usuario, nombre_usuario, apellido_usuario, email_usuario):
    cursor.execute("UPDATE usuario SET nombre_usuario=%s, apeellido_usuario=%s, email_usuario=%s WHERE id_usuario=%s", 
                   (nombre_usuario, apellido_usuario, email_usuario, id_usuario))
    conn.commit()

# Eliminar un usuario
def delete_usuario(id_usuario):
    cursor.execute("DELETE FROM usuario WHERE id_usuario=%s", (id_usuario,))
    conn.commit()

# Ejemplo de uso
create_usuario("Karen", "Varela", "karen@project.com")
create_usuario("Dulce", "Limones", "dulce@project.com")
create_usuario("Clara", "Rivera", "clara@project.com")
create_usuario("Alejandro", "Morales", "alejandro@project.com")

print("Usuarios:", read_usuarios())

update_usuario(1, "Karen Cecilia","Varela Castro", "karen.varela@project.com")
#delete_usuario(2)

print("usuarios después de cambios:", read_usuarios())

cursor.close()
conn.close()
