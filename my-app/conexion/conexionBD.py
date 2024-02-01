

# Importando Libreria mysql.connector para conectar Python con MySQL
import mysql.connector


def connectionBD():
    print("ENTRO A LA CONEXION")
    try:
        # connection = mysql.connector.connect(
        connection = mysql.connector.connect(
            host="173.255.114.9",
            port=3306,
            user="xavier",
            password="xavier.38",
            database="Proyecto"
        )
        if connection.is_connected():
            print("Conexión exitosa a la BD")
            return connection

    except mysql.connector.Error as error:
        print(f"No se pudo conectar: {error}")


