

# Importando Libreria mysql.connector para conectar Python con MySQL
import mysql.connector


def connectionBD():
    print("ENTRO A LA CONEXION")
    try:
        # connection = mysql.connector.connect(
        connection = mysql.connector.connect(
            host="localhost",
                #host="viaduct.proxy.rlwy.net",
            port=3306,
            user="Xavi38",
            passwd="xavier.38",
                #passwd="-3GNBRLZpGgc9kPcWT8aBiVNxPPJVGuqLR3",
            database="proyecto",
                #database="crud_python",
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            raise_on_warnings=True

        )
        if connection.is_connected():
            print("Conexión exitosa a la BD")
            return connection

    except mysql.connector.Error as error:
        print(f"No se pudo conectar: {error}")


