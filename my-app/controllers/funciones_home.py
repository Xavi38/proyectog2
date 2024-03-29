
# Para subir archivo tipo foto al servidor
from werkzeug.utils import secure_filename
import uuid  # Modulo de python para crear un string

from conexion.conexionBD import connectionBD  # Conexión a BD

import re
import os

from os import remove  # Modulo  para remover archivo
from os import path  # Modulo para obtener la ruta o directorio
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from io import BytesIO
from datetime import datetime

import openpyxl  # Para generar el excel
# biblioteca o modulo send_file para forzar la descarga
from flask import send_file, session

def accesosReporte():
    try:
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                if session['ID_Cargo'] == 1:
                    querySQL = """
                        SELECT Ingreso.ID, Usuario.Nombre AS Usuario_Nombre, Ingreso.Fecha, Ingreso.Hora, Area.Nombre AS Area_Nombre, Ingreso.Clave, Tarjeta_rfid.Lectura
                        FROM Ingreso
                        JOIN Usuario ON Usuario.ID = Ingreso.ID_Usuario
                        JOIN Area ON Usuario.ID_Area = Area.ID
                        JOIN Tarjeta_rfid ON Usuario.ID = Tarjeta_rfid.ID
                        ORDER BY Usuario.ID DESC
                    """
                    cursor.execute(querySQL)
                else:
                    Nombre = session['Nombre']
                    querySQL = """
                        SELECT Ingreso.ID, Usuario.Nombre AS Usuario_Nombre, Ingreso.Fecha, Ingreso.Hora, Area.Nombre AS Area_Nombre, Ingreso.Clave, Tarjeta_rfid.Lectura
                        FROM Ingreso
                        JOIN Usuario ON Usuario.ID = Ingreso.ID_Usuario
                        JOIN Area ON Usuario.ID_Area = Area.ID
                        JOIN Tarjeta_rfid ON Usuario.ID = Tarjeta_rfid.ID
                        ORDER BY Usuario.ID DESC
                    """
                    cursor.execute(querySQL, (Nombre,))

                accesosBD = cursor.fetchall()
        return accesosBD
    except Exception as e:
        print(f"Error en la función accesosReporte: {e}")
        return []

def generarReporteExcel():
    dataAccesos = accesosReporte()
    wb = openpyxl.Workbook()
    hoja = wb.active

    # Agregar la fila de encabezado con los títulos
    cabeceraExcel = ("ID", "NOMBRE", "FECHA", "HORA", "ÁREA", "CLAVE GENERADA", "LECTURA RFID")
    hoja.append(cabeceraExcel)

    # Agregar los registros a la hoja
    for registro in dataAccesos:
        ID = registro['ID']
        Nombre = registro['Usuario_Nombre']
        Fecha = registro['Fecha']
        Hora = registro['Hora']
        Area = registro['Area_Nombre']
        Clave = registro['Clave']
        Lectura = registro['Lectura']

        # Agregar los valores a la hoja
        hoja.append((ID, Nombre, Fecha, Hora, Area, Clave, Lectura))

    fecha_actual = datetime.now()
    archivoExcel = f"Reporte_accesos_{session['Nombre']}_{fecha_actual.strftime('%Y_%m_%d')}.xlsx"
    carpeta_descarga = "../static/downloads-excel"
    ruta_descarga = os.path.join(os.path.dirname(os.path.abspath(__file__)), carpeta_descarga)

    if not os.path.exists(ruta_descarga):
        os.makedirs(ruta_descarga)
        os.chmod(ruta_descarga, 0o755)

    ruta_archivo = os.path.join(ruta_descarga, archivoExcel)
    wb.save(ruta_archivo)

    # Enviar el archivo como respuesta HTTP
    return send_file(ruta_archivo, as_attachment=True)

def generarReportePDF():
    dataAccesos = accesosReporte()
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=landscape(letter))
    y_position = 500
    pdf.drawString(350, y_position, "Reporte de Accesos")
    y_position -= 30  # Mayor separación del título
    pdf.line(1, y_position + 20, 7 * 120, y_position + 20)
    cabeceraPDF = ["ID", "Usuario_Nombre", "Fecha", "Hora", "Area_Nombre", "Clave", "Lectura"]
    pdf.line(1, y_position, 7 * 120, y_position)
    for i in range(len(cabeceraPDF)):
        pdf.line(1 + i * 120, y_position, 1 + i * 120, y_position - 20)
        pdf.drawString(1 + i * 120, y_position, cabeceraPDF[i])
        pdf.line(1 + i * 120, y_position - 20, 1 + i * 120, y_position - 30)
    pdf.line(1, y_position - 30, 7 * 120, y_position - 30)
    for registro in dataAccesos:
        pdf.line(1, y_position - 30, 7 * 120, y_position - 30)
        y_position -= 20
        print(f"Registro actual: {registro}")
        for i in range(len(cabeceraPDF)):
            pdf.drawString(1 + i * 120, y_position, str(registro[cabeceraPDF[i]]))
            pdf.line(1 + i * 120, y_position - 10, 1 + i * 120, y_position - 30)
        pdf.line(1, y_position - 30, 7 * 120, y_position - 30)
    pdf.save()
    buffer.seek(0)
    fecha_actual = datetime.now()
    archivoPDF = f"Reporte_accesos_{session['Nombre']}_{fecha_actual.strftime('%Y_%m_%d')}.pdf"
    carpeta_descarga = "../static/downloads-pdf"
    ruta_descarga = os.path.join(os.path.dirname(os.path.abspath(__file__)), carpeta_descarga)

    if not os.path.exists(ruta_descarga):
        os.makedirs(ruta_descarga)
        os.chmod(ruta_descarga, 0o755)
    ruta_archivo = os.path.join(ruta_descarga, archivoPDF)
    with open(ruta_archivo, "wb") as f:
        f.write(buffer.read())
    return send_file(ruta_archivo, as_attachment=True)

def buscarAreaBD(search):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                querySQL = ("""
                        SELECT 
                            Area.ID,
                            Area.Nombre
                        FROM Area 
                        WHERE Area.Nombre LIKE %s 
                        ORDER BY Area.ID DESC
                    """)
                search_pattern = f"%{search}%"  # Agregar "%" alrededor del término de búsqueda
                mycursor.execute(querySQL, (search_pattern,))
                resultado_busqueda = mycursor.fetchall()
                return resultado_busqueda

    except Exception as e:
        print(f"Ocurrió un error en def buscarEmpleadoBD: {e}")
        return []


# Lista de Usuarios creados
def lista_usuariosBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "Select ID, Nombre, Contraseña, ID_Cargo, ID_Area from Usuario"
                cursor.execute(querySQL,)
                usuariosBD = cursor.fetchall()
        return usuariosBD
    except Exception as e:
        print(f"Error en lista_usuariosBD : {e}")
        return []
    
def lista_temperaturaBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "Select ID, fecha, hora, valor from Sensor_de_Temperatura"
                cursor.execute(querySQL,)
                temperaturaBD = cursor.fetchall()
        return temperaturaBD
    except Exception as e:
        print(f"Error en lista_temperaturaBD : {e}")
        return []

def lista_humoBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "Select ID, fecha, hora, valor from Sensor_de_Humo"
                cursor.execute(querySQL,)
                temperaturaBD = cursor.fetchall()
        return temperaturaBD
    except Exception as e:
        print(f"Error en lista_humoBD : {e}")
        return []

def tarjeta_rfidBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "Select ID, fecha, hora, Lectura from Tarjeta_rfid"
                cursor.execute(querySQL,)
                temperaturaBD = cursor.fetchall()
        return temperaturaBD
    except Exception as e:
        print(f"Error en tarjeta_rfidBD: {e}")
        return []

def lista_areasBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT ID, Nombre FROM Area"
                cursor.execute(querySQL)
                areasBD = cursor.fetchall()
        return areasBD
    except Exception as e:
        print(f"Error en lista_areas : {e}")
        return []


# Eliminar usuario
def eliminarUsuario(ID):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM Usuario WHERE ID=%s"
                cursor.execute(querySQL, (ID,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminarUsuario : {e}")
        return []    

def eliminarArea(ID):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM Area WHERE ID=%s"
                cursor.execute(querySQL, (ID,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminarArea : {e}")
        return []
    
def dataReportes():
    try:
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                SELECT Ingreso.ID, Usuario.Nombre AS Usuario_Nombre, Ingreso.Fecha, Ingreso.Hora, Area.Nombre AS Area_Nombre, Ingreso.Clave, Tarjeta_rfid.Lectura
                        FROM Ingreso
                        JOIN Usuario ON Usuario.ID = Ingreso.ID_Usuario
                        JOIN Area ON Usuario.ID_Area = Area.ID
                        JOIN Tarjeta_rfid ON Usuario.ID = Tarjeta_rfid.ID
                        ORDER BY Usuario.ID DESC
                """
                cursor.execute(querySQL)
                reportes = cursor.fetchall()
        return reportes
    except Exception as e:
        print(f"Error en dataReportes: {e}")
        return []


def lastAccessBD(ID):
    try:
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT Ingreso.ID, Usuario.Nombre, Ingreso.Fecha, Ingreso.Clave FROM Ingreso JOIN Usuario WHERE Usuario.ID = Ingreso.ID_Usuario AND Usuario.Nombre=%s ORDER BY Ingreso.Fecha DESC LIMIT 1"
                cursor.execute(querySQL,(ID,))
                reportes = cursor.fetchone()
                print(reportes)
        return reportes
    except Exception as e:
        print(f"Error en lastAcceso : {e}")
        return []
import random
import string

def crearClave():
    caracteres = string.ascii_letters + string.digits  # Letras mayúsculas, minúsculas y dígitos
    longitud = 6  # Longitud de la clave

    clave = ''.join(random.choice(caracteres) for _ in range(longitud))
    print("La clave generada es:", clave)
    return clave

##GUARDAR CLAVES GENERADAS EN AUDITORIA
from datetime import datetime

def guardarClaveAuditoria(clave_audi, ID):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                fecha_actual = datetime.now().strftime('%Y-%m-%d')
                hora_actual = datetime.now().strftime('%H:%M:%S')
                
                sql = "INSERT INTO Ingreso (fecha, Hora, ID_Usuario, Clave) VALUES (%s, %s, %s, %s)"
                valores = (fecha_actual, hora_actual, ID, clave_audi)
                mycursor.execute(sql, valores)
                conexion_MySQLdb.commit()
                resultado_insert = mycursor.rowcount
                return resultado_insert
    except Exception as e:
        print(f"Error en guardarClaveAuditoria: {e}")
        return None



    
def lista_rolesBD():
    try:
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT * FROM Cargo"
                cursor.execute(querySQL)
                cargos = cursor.fetchall()
                return cargos
    except Exception as e:
        print(f"Error en select cargos : {e}")
        return []
##CREAR AREA
def guardarArea(area_name):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                    sql = "INSERT INTO Area (Nombre) VALUES (%s)"
                    valores = (area_name,)
                    mycursor.execute(sql, valores)
                    conexion_MySQLdb.commit()
                    resultado_insert = mycursor.rowcount
                    return resultado_insert 
        
    except Exception as e:
        return f'Se produjo un error en crear Area: {str(e)}' 
    
##ACTUALIZAR AREA
def actualizarArea(area_id, area_name):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                sql = """UPDATE Area SET Nombre = %s WHERE ID = %s"""
                valores = (area_name, area_id)
                mycursor.execute(sql, valores)
                conexion_MySQLdb.commit()
                resultado_update = mycursor.rowcount
                return resultado_update 
        
    except Exception as e:
        return f'Se produjo un error al actualizar el área: {str(e)}'
    
def obtener_registros_temperatura():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                query = "SELECT * FROM Sensor_de_Temperatura"
                mycursor.execute(query)
                registros_temperatura = mycursor.fetchall()

                return registros_temperatura

    except Exception as e:
        print(f"Error en obtener_registros_temperatura: {e}")
        return None