# Importandopaquetes desde flask
from flask import session, flash

# Importando conexion a BD
from conexion.conexionBD import connectionBD
# Para  validar contraseña
from werkzeug.security import check_password_hash

import re
# Para encriptar contraseña generate_password_hash
from werkzeug.security import generate_password_hash


def recibeInsertRegisterUser(Nombre, Contraseña, pass_user, ID_Cargo, ID_Area ):
    respuestaValidar = validarDataRegisterLogin(
        Nombre, Contraseña, pass_user)

    if (respuestaValidar):
        nueva_password = generate_password_hash(pass_user, method='scrypt')
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                    sql = """
                    INSERT INTO Usuario (Nombre, Contraseña, Password, ID_Cargo, ID_Area)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    valores = (Nombre, Contraseña, nueva_password, ID_Cargo, ID_Area)
                    mycursor.execute(sql, valores)
                    conexion_MySQLdb.commit()
                    resultado_insert = mycursor.rowcount
                    return resultado_insert
        except Exception as e:
            print(f"Error en el Insert users: {e}")
            return []
    else:
        return False


# Validando la data del Registros para el login
def validarDataRegisterLogin(Nombre, Contraseña,pass_user):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT * FROM usuarios WHERE Nombre = %s"
                cursor.execute(querySQL, (Nombre,))
                userBD = cursor.fetchone()  # Obtener la primera fila de resultados

                if userBD is not None:
                    flash('el registro no fue procesado ya existe la cuenta', 'error')
                    return False
                elif not Nombre or not Contraseña or not pass_user:
                    flash('por favor llene los campos del formulario.', 'error')
                    return False
                else:
                    # La cuenta no existe y los datos del formulario son válidos, puedo realizar el Insert
                    return True
    except Exception as e:
        print(f"Error en validarDataRegisterLogin : {e}")
        return []


def info_perfil_session(ID):
    print(id)
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "Select ID, Nombre, Contraseña, ID_Cargo, ID_Area from usuario where ID = %s"
                cursor.execute(querySQL, (ID,))
                info_perfil = cursor.fetchall()
        return info_perfil
    except Exception as e:
        print(f"Error en info_perfil_session : {e}")
        return []


def procesar_update_perfil(data_form,ID):
    # Extraer datos del diccionario data_form
    ID = ID
    Nombre = data_form['Nombre']
    Contraseña = data_form['Contraseña']


    new_pass_user = data_form['new_pass_user']


    if session['ID_Cargo'] == 1 :
        try:
            nueva_password = generate_password_hash(
                new_pass_user, method='scrypt')
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                    querySQL = """
                        UPDATE usuario
                        SET
                            Nombre= %s,
                            Contraseña = %s,
                            ID_Cargo = %s,
                            ID_Area = %s,
                        WHERE ID = %s
                    """
                    params = (Nombre,nueva_password, ID_Cargo, ID_Area, ID)
                    cursor.execute(querySQL, params)
                    conexion_MySQLdb.commit()
            return 1
        except Exception as e:
            print(
                f"Ocurrió en procesar_update_perfil: {e}")
            return []
    
    pass_actual = data_form['pass_actual']
    repetir_pass_user = data_form['repetir_pass_user']

    print(" HOLA "+ID_Cargo)

    if not pass_actual and not new_pass_user and not repetir_pass_user:
            return updatePefilSinPass(ID, Nombre, Contraseña , ID_Cargo, ID_Area)

    with connectionBD() as conexion_MySQLdb:
        with conexion_MySQLdb.cursor(dictionary=True) as cursor:
            querySQL = """SELECT * FROM usuario WHERE Nombre = %s"""
            cursor.execute(querySQL, (Nombre,))
            account = cursor.fetchone()
            if account:
                
                if check_password_hash(account['Password'], pass_actual):
                    # Verificar si new_pass_user y repetir_pass_user están vacías
                        if new_pass_user != repetir_pass_user:
                            return 2
                        else:
                            try:
                                nueva_password = generate_password_hash(
                                    new_pass_user, method='scrypt')
                                with connectionBD() as conexion_MySQLdb:
                                    with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                                        querySQL = """
                                            UPDATE usuario
                                            SET
                                                Nombre= %s,
                                                Contraseña = %s,
                                                ID_Cargo = %s,
                                                ID_Area = %s,
                                            WHERE ID = %s
                                        """
                                        params = (Nombre,nueva_password, ID_Cargo, ID_Area, ID)
                                        cursor.execute(querySQL, params)
                                        conexion_MySQLdb.commit()
                                return cursor.rowcount or []
                            except Exception as e:
                                print(
                                    f"Ocurrió en procesar_update_perfil: {e}")
                                return []
            else:
                return 0



def updatePefilSinPass(ID, Nombre, Contraseña, ID_Cargo, ID_Area):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                    UPDATE usuario
                    SET
                        Nombre= %s,
                        Contraseña = %s,
                        ID_Cargo = %s,
                        ID_Area = %s,
                    WHERE ID = %s
                """
                params = (Nombre,Contraseña, ID_Cargo, ID_Area, ID)
                cursor.execute(querySQL, params)
                conexion_MySQLdb.commit()
        return cursor.rowcount
    except Exception as e:
        print(f"Ocurrió un error en la funcion updatePefilSinPass: {e}")
        return []


def dataLoginSesion():
    inforLogin = {
        "ID": session['ID'],
        "Nombre": session['Nombre'],
        "ID_Cargo": session['ID_Cargo'],
        "ID_Area": session['ID_Area']
    }
    return inforLogin
