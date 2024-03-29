
from app import app
from flask import render_template, request, flash, redirect, url_for, session

# Importando mi conexión a BD
from conexion.conexionBD import connectionBD

# Para encriptar contraseña generate_password_hash
from werkzeug.security import check_password_hash

# Importando controllers para el modulo de login
from controllers.funciones_login import *
from controllers.funciones_home import *
PATH_URL_LOGIN = "/public/login"


@app.route('/', methods=['GET'])
def inicio():
    if 'conectado' in session:
        return render_template('public/base_cpanel.html', dataLogin=dataLoginSesion())
    else:
        return render_template(f'{PATH_URL_LOGIN}/base_login.html')


@app.route('/mi-perfil/<string:ID>', methods=['GET'])
def perfil(ID):
    if 'conectado' in session:
        
        return render_template(f'public/perfil/perfil.html', info_perfil_session=info_perfil_session(ID), dataLogin=dataLoginSesion(), areas=lista_areasBD(), cargos=lista_rolesBD())
    else:
        return redirect(url_for('inicio'))


# Crear cuenta de usuario
@app.route('/register-user', methods=['GET'])
def cpanelRegisterUser():
        return render_template(f'{PATH_URL_LOGIN}/auth_register.html',dataLogin = dataLoginSesion(),areas=lista_areasBD(), cargos=lista_rolesBD())


@app.route('/register-target', methods=['GET'])
def tarjeta():
        return render_template(f'{PATH_URL_LOGIN}/target_register.html',dataLogin = dataLoginSesion(),lectura=tarjeta_rfidBD())

# Recuperar cuenta de usuario
@app.route('/recovery-password', methods=['GET'])
def cpanelRecoveryPassUser():
    if 'conectado' in session:
        return redirect(url_for('inicio'))
    else:
        return render_template(f'{PATH_URL_LOGIN}/auth_forgot_password.html')


# Crear cuenta de usuario
@app.route('/saved-register', methods=['POST'])
def cpanelRegisterUserBD():
    if request.method == 'POST' and 'Nombre' in request.form and 'pass_user' in request.form:
        try:
            Nombre = request.form['Nombre']
            Contraseña = request.form['Contraseña']
            pass_user = request.form['pass_user']
            ID_Cargo = request.form['ID_Cargo']
            ID_Area = request.form['ID_Area']

            resultData = recibeInsertRegisterUser(Nombre, Contraseña, pass_user, ID_Cargo, ID_Area)

            if resultData != 0:
                flash('La cuenta fue creada correctamente.', 'success')
                return redirect(url_for('usuarios'))
            else:
                flash('La cuenta no fue creada correctamente. Verifica los datos ingresados.', 'error')
                return redirect(url_for('usuarios'))
        
        except Exception as e:
            error_message = f'Error al intentar crear la cuenta: {e}'
            flash(error_message, 'error')
            print(error_message)  # Imprime el error en la consola para obtener detalles durante el desarrollo
            return redirect(url_for('usuarios'))
    else:
        flash('El método HTTP es incorrecto', 'error')
        return redirect(url_for('usuarios'))

@app.route('/saved-target', methods=['POST'])
def cpanelRegisterTargetBD():
    if request.method == 'POST' and 'ID' in request.form:
        try:
            ID = request.form['ID']
            Fecha = request.form['Fecha']
            Hora = request.form['Hora']
            Lectura = request.form['Lectura']

            resultData = recibeInsertRegisterTarget(ID, Fecha, Hora, Lectura)

            if resultData != 0:
                flash('La tarjeta nueva fue creada correctamente.', 'success')
                return redirect(url_for('inicio'))
            else:
                flash('La tarjeta nueva  no fue creada correctamente. Verifica los datos ingresados.', 'error')
                return redirect(url_for('inicio'))
        
        except Exception as e:
            error_message = f'Error al intentar crear la cuenta: {e}'
            flash(error_message, 'error')
            print(error_message)  # Imprime el error en la consola para obtener detalles durante el desarrollo
            return redirect(url_for('inicio'))
    else:
        flash('El método HTTP es incorrecto', 'error')
        return redirect(url_for('usuarios'))
    
# Actualizar datos de mi perfil
@app.route("/actualizar-datos-perfil/<int:ID>", methods=['POST'])
def actualizarPerfil(ID):
    if request.method == 'POST':
        if 'conectado' in session:
            respuesta = procesar_update_perfil(request.form,ID)
            if respuesta == 1:
                flash('Los datos fuerón actualizados correctamente.', 'success')
                return redirect(url_for('inicio'))
            elif respuesta == 0:
                flash(
                    'La contraseña actual esta incorrecta, por favor verifique.', 'error')
                return redirect(url_for('perfil',ID=ID))
            elif respuesta == 2:
                flash('Ambas claves deben se igual, por favor verifique.', 'error')
                return redirect(url_for('perfil',ID=ID))
            elif respuesta == 3:
                flash('La Clave actual es obligatoria.', 'error')
                return redirect(url_for('perfil',ID=ID))
            else: 
                flash('Clave actual incorrecta', 'error')
                return redirect(url_for('perfil',ID=ID))
        else:
            flash('primero debes iniciar sesión.', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


# Validar sesión
@app.route('/login', methods=['GET', 'POST'])
def loginCliente():
    if 'conectado' in session:
        return redirect(url_for('inicio'))
    else:
        if request.method == 'POST' and 'Nombre' in request.form and 'pass_user' in request.form:

            Nombre = request.form['Nombre']
            pass_user = str(request.form['pass_user'])
            conexion_MySQLdb = connectionBD()
            print(conexion_MySQLdb)
            cursor = conexion_MySQLdb.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM Usuario WHERE Nombre = %s", [Nombre])
            account = cursor.fetchone()

            if account:
                if check_password_hash(account['Password'], pass_user):
                    # Crear datos de sesión, para poder acceder a estos datos en otras rutas
                    session['conectado'] = True
                    session['ID'] = account['ID']
                    session['Nombre'] = account['Nombre']
                    session['ID_Cargo'] = account['ID_Cargo']
                    session['ID_Area'] = account['ID_Area']

                    flash('la sesión fue correcta.', 'success')
                    return redirect(url_for('inicio'))
                else:
                    # La cuenta no existe o el nombre de usuario/contraseña es incorrecto
                    flash('datos incorrectos por favor revise.', 'error')
                    return render_template(f'{PATH_URL_LOGIN}/base_login.html')
            else:
                flash('el usuario no existe, por favor verifique.', 'error')
                return render_template(f'{PATH_URL_LOGIN}/base_login.html')
        else:
            flash('primero debes iniciar sesión.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/base_login.html')


@app.route('/closed-session',  methods=['GET'])
def cerraSesion():
    if request.method == 'GET':
        if 'conectado' in session:
            # Eliminar datos de sesión, esto cerrará la sesión del usuario
            session.pop('conectado', None)
            session.pop('ID', None)
            session.pop('Nombre', None)
            session.pop('email', None)
            flash('tu sesión fue cerrada correctamente.', 'success')
            return redirect(url_for('inicio'))
        else:
            flash('recuerde debe iniciar sesión.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/base_login.html')
