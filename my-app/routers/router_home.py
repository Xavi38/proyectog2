from controllers.funciones_login import *
from app import app
from flask import render_template, request, flash, redirect, url_for, session,  jsonify
from mysql.connector.errors import Error


# Importando cenexión a BD
from controllers.funciones_home import *

@app.route('/lista-de-areas', methods=['GET'])
def lista_areas():
    if 'conectado' in session:
        return render_template('public/usuarios/lista_areas.html', areas=lista_areasBD(), dataLogin=dataLoginSesion())
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route("/lista-de-usuarios", methods=['GET'])
def usuarios():
    if 'conectado' in session:
        return render_template('public/usuarios/lista_usuarios.html',  resp_usuariosBD=lista_usuariosBD(), dataLogin=dataLoginSesion(), areas=lista_areasBD(), cargos = lista_rolesBD())
    else:
        return redirect(url_for('inicioCpanel'))

@app.route("/sensor-de-temperatura", methods=['GET'])
def sensor_temperatura():
    if 'conectado' in session:
        return render_template('public/usuarios/sensor_temperatura.html', temperatura=lista_temperaturaBD(), dataLogin=dataLoginSesion())
    else:
        return redirect(url_for('inicioCpanel'))

@app.route("/sensor-de-humo", methods=['GET'])
def sensor_humo():
    if 'conectado' in session:
        return render_template('public/usuarios/sensor_humo.html', humo=lista_humoBD(), dataLogin=dataLoginSesion())
    else:
        return redirect(url_for('inicioCpanel'))

@app.route("/diseño-data", methods=['GET'])
def diseño_data():
    if 'conectado' in session:
        return render_template('public/usuarios/diseño_data.html', dataLogin=dataLoginSesion())
    else:
        return redirect(url_for('inicioCpanel'))

@app.route("/tarjeta-rfid", methods=['GET'])
def tarjeta_rfid():
    if 'conectado' in session:
        return render_template('public/usuarios/tarjeta_rfid.html', lectura=tarjeta_rfidBD(), dataLogin=dataLoginSesion())
    else:
        return redirect(url_for('inicioCpanel'))

#Ruta especificada para eliminar un usuario
@app.route('/borrar-usuario/<string:ID>', methods=['GET'])
def borrarUsuario(ID):
    resp = eliminarUsuario(ID)
    if resp:
        flash('El Usuario fue eliminado correctamente', 'success')
        return redirect(url_for('usuarios'))
    
    
@app.route('/borrar-area/<string:ID>/', methods=['GET'])
def borrarArea(ID):
    resp = eliminarArea(ID)
    if resp:
        flash('El Empleado fue eliminado correctamente', 'success')
        return redirect(url_for('lista_areas'))
    else:
        flash('Hay usuarios que pertenecen a esta área', 'error')
        return redirect(url_for('lista_areas'))


@app.route("/descargar-informe-accesos/", methods=['GET'])
def reporteBD():
    if 'conectado' in session:
        return generarReporteExcel()
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
@app.route("/reporte-accesos", methods=['GET'])
def reporteAccesos():
    if 'conectado' in session:
        userData = dataLoginSesion()
        return render_template('public/perfil/reportes.html',  reportes=dataReportes(),resp_usuariosBD=lista_usuariosBD(),areas=lista_areasBD() ,lectura=tarjeta_rfidBD(),lastAccess=lastAccessBD(userData.get('Nombre')), dataLogin=dataLoginSesion())

@app.route("/interfaz-clave", methods=['GET','POST'])
def claves():
    return render_template('public/usuarios/generar_clave.html', dataLogin=dataLoginSesion())
    
@app.route('/generar-y-guardar-clave/<string:ID>', methods=['GET','POST'])
def generar_clave(ID):
    print(ID)
    clave_generada = crearClave()  # Llama a la función para generar la clave
    print(f"ID: {ID}, Clave generada: {clave_generada}")
    guardarClaveAuditoria(clave_generada,ID)
    return clave_generada
#CREAR AREA
@app.route('/crear-area', methods=['GET','POST'])
def crearArea():
    if request.method == 'POST':
        area_name = request.form['Nombre']  # Asumiendo que 'nombre_area' es el nombre del campo en el formulario
        resultado_insert = guardarArea(area_name)
        if resultado_insert:
            # Éxito al guardar el área
            flash('El Area fue creada correctamente', 'success')
            return redirect(url_for('lista_areas'))
            
        else:
            # Manejar error al guardar el área
            return "Hubo un error al guardar el área."
    return render_template('public/usuarios/lista_areas')

##ACTUALIZAR AREA
@app.route('/actualizar-area', methods=['POST'])
def updateArea():
    if request.method == 'POST':
        Nombre = request.form['Nombre']  # Asumiendo que 'nuevo_nombre' es el nombre del campo en el formulario
        ID = request.form['ID']
        resultado_update = actualizarArea(ID, Nombre)
        if resultado_update:
           # Éxito al actualizar el área
            flash('El actualizar fue creada correctamente', 'success')
            return redirect(url_for('lista_areas'))
        else:
            # Manejar error al actualizar el área
            return "Hubo un error al actualizar el área."

    return redirect(url_for('lista_areas'))
