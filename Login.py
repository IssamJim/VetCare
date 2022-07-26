from flask import Blueprint, redirect, render_template, request, session
from passlib.hash import sha256_crypt
from Otros import guardar_diccionario, lee_diccionario_csv
from Menu import crear_menu, validar_ruta_disponible
import smtplib
from email.message import EmailMessage
import random

# este valor es importante, porque es parte de lo que mandamos como enlace en el correo de recuperación, como este proyecto
# debería de estarse ejecutando localmente, debería de redireccionar correctamente, es así debido a que no se alojó la página en un servidor no local
host = "http://127.0.0.1:5000"
archivo_usuarios = "./files/usuarios.csv"
# se crea el blueprint para el modulo de Login
# Se utiliza para estructurar la aplicación Flask
# en diferentes componentes, lo que hace que la estructuración de la aplicación se base en diferentes funciones.
# Referencia: https://dev.to/paurakhsharma/flask-rest-api-part-2-better-structure-with-blueprint-and-flask-restful-2n93
# https://realpython.com/flask-blueprint/
login_blueprint = Blueprint('login_blueprint', __name__)

# en lugar de app, se usa login_blueprint


@login_blueprint.route('/login', methods=['GET', 'POST'])
@login_blueprint.route('/login/', methods=['GET', 'POST'])
def login():
    diccionario_usuarios = lee_diccionario_csv(
        archivo_usuarios, "nombre_corto")
    # primero se checa si el usuario ya está logeado
    if 'usuario' in session:
        # los toast son como mensajes decorados que ofrece bootstrap, estos datos van a llenar su estructura en el template
        mostrar_toast = True
        mensaje = f'Ya has accedido con tu cuenta {diccionario_usuarios[session["usuario"]]["nombre_corto"]}.'
        asunto_mensaje = "Ya has accedido"
        icono = "/static/images/icono_exito.png"
        return render_template('login.html', logeado=True, mostrar_toast=mostrar_toast, mensaje=mensaje, asunto_mensaje=asunto_mensaje, icono=icono)
    else:
        # si solo se está accediendo a la página de login
        if request.method == 'GET':
            mostrar_toast = False
            return render_template('login.html', mostrar_toast=mostrar_toast)
        else:
            # si se presionó el botón enviar del formulario en la página de login
            if request.method == 'POST':
                # se obtiene el nombre de usuario dado en el formulario
                nombre_usuario = request.form['username']
                if nombre_usuario in diccionario_usuarios:
                    # password guardado en el archivo usuarios.csv, se accede mediante la llave del nombre de usuario (nombre_corto) y
                    # la 'subllave' password
                    password_db = diccionario_usuarios[nombre_usuario]['password']
                    # se obtiene el password del usuario dado en el formulario
                    password_formulario = request.form['password']
                    # se verifica que ambas contraseñas coincidan, la del formulario y la que se encuentra en el archivo usuarios.csv
                    verificado = sha256_crypt.verify(
                        password_formulario, password_db)
                    # si la contraseña es correcta
                    if (verificado == True):
                        # se guarda en las cookies el nombre de usuario
                        session['usuario'] = nombre_usuario
                        # si el usuario trataba de acceder a una ruta antes de ser redirigido al login, se le redirecciona a esa ruta
                        if 'ruta' in session:
                            ruta = session['ruta']
                            # para mejorar la "calidad" del usuario en el sitio, hay que verificar si el usuario podía acceder
                            # a la ruta que especificó justo antes de ser redireccionado al login
                            usuario = diccionario_usuarios[session['usuario']]
                            paginas_disponibles = crear_menu(usuario)
                            acceso = validar_ruta_disponible(
                                ruta, paginas_disponibles)
                            if acceso == False:
                                # si no tenia permisos para acceder a esa ruta antes de ser redireccionado al login, entonces es redirigo al index, ya logeado, esto es así, por que si no sería redireccionado
                                # a la página de /no_tienes_permisos por la función before_request() en app.py, lo que podría confundir al
                                # usuario
                                return redirect("/")
                            # si el usuario si tenia permisos entonces, despues de logearse es redirigido a esa ruta.
                            # se hace uso del metodo .pop(), con 2 parametros, el primero es la llave que se busca eliminar junto a su valor y el segundo
                            # parametro es por si no llega a encontrar esa llave, ya que este método regresa un valor, si no llega a encontrar esa llave
                            # regresa None y se evita una excepción
                            # se 'limpia' la ruta
                            session.pop('ruta', None)
                            return redirect(ruta)
                        # si el usuario no trató de acceder a alguna página en la que requiriera logearse, entonces se redirecciona a la página de inicio
                        else:
                            return redirect("/")
                    # si la contraseña es incorrecta
                    else:
                        mostrar_toast = True
                        mensaje = f'El password de {nombre_usuario} no corresponde'
                        asunto_mensaje = "Contraseña incorrecta"
                        icono = "/static/images/icono_fracaso.png"
                        return render_template('login.html', mostrar_toast=mostrar_toast, mensaje=mensaje, asunto_mensaje=asunto_mensaje, icono=icono)
                # si el usuario no es encontrado en el archivo usuarios.csv
                else:
                    mostrar_toast = True
                    mensaje = f'El Usuario {nombre_usuario} no existe'
                    asunto_mensaje = "No se encontró a ese usuario"
                    icono = "/static/images/icono_fracaso.png"
                    return render_template('login.html', mostrar_toast=mostrar_toast, mensaje=mensaje, asunto_mensaje=asunto_mensaje, icono=icono)


@login_blueprint.route('/logout', methods=['GET'])
@login_blueprint.route('/logout/', methods=['GET'])
def logout():
    """
    Esta función sirve para cerrar sesión, borra la llave de 'usuario' del 'diccionario' session, de modo que uno de los valores
    que define si el usuario está logeado (session['usuario]) es eliminado
    """
    if request.method == 'GET':
        session.clear()
        return redirect("/login/")


@login_blueprint.route('/recuperar_contrasenia', methods=['GET', 'POST'])
@login_blueprint.route('/recuperar_contrasenia/', methods=['GET', 'POST'])
def recuperar_contrasenia():
    diccionario_correos = lee_diccionario_csv(archivo_usuarios, "email")
    # primero se tiene que checar si el usuario está logeado a una cuenta cuando esté haciendo esto, porque cuando
    # se cierra sesión, las cookies se borran, y algunas de ellas influyen en este proceso como el codigo de verificacion
    # y la variable booleana que indican si el usuario está tratando de recuperar su contraseña
    if 'usuario' in session:
        # se cierra la sesión
        return redirect('/logout/')
    # si no está logeado
    else:
        if request.method == 'GET':
            mostrar_toast = False
            return render_template('recuperar_contrasenia.html', mostrar_toast=mostrar_toast)
        else:
            if request.method == 'POST':
                correo_destinatario = request.form['correo']
                if correo_destinatario in diccionario_correos:
                    mandar_correo_recuperacion(correo_destinatario)
                    mostrar_toast = True
                    mensaje = 'Sigue las instrucciones que se han enviado al correo que proporcionaste para recuperar tu contraseña.'
                    asunto_mensaje = "Correo enviado"
                    icono = "/static/images/icono_exito.png"
                    return render_template('recuperar_contrasenia.html', mostrar_toast=mostrar_toast, mensaje=mensaje, asunto_mensaje=asunto_mensaje, icono=icono)
                else:
                    mostrar_toast = True
                    mensaje = f'El correo "{correo_destinatario}" no se encuentra registrado'
                    asunto_mensaje = "Correo no encontrado"
                    icono = "/static/images/icono_fracaso.png"
                    return render_template('recuperar_contrasenia.html', mostrar_toast=mostrar_toast, mensaje=mensaje, asunto_mensaje=asunto_mensaje, icono=icono)


def mandar_correo_recuperacion(correo_destinatario: str) -> None:
    diccionario_correos = lee_diccionario_csv(archivo_usuarios, "email")
    mensaje = EmailMessage()
    asunto_del_mensaje = "Recuperación de contraseña"
    correo_remitente = "vetcaresystem@gmail.com"
    contrasenia_correo_remitente = "vetcare1289"
    mensaje['Subject'] = asunto_del_mensaje
    mensaje['From'] = correo_remitente
    mensaje['To'] = correo_destinatario
    # se va a generar un codigo de 6 cifras que es común verlo en algunas páginas que tienen un proceso de recuperación de contraseñas similares
    codigo_recuperacion = random.randint(100000, 999999)
    # se guarda en las cookies ese codigo de recuperacion
    session['codigo_recuperacion'] = codigo_recuperacion
    # tambien se va a guardar esta variable booleana, para checar si el usuario está recuperando su contraseña
    session['recuperando_contrasenia'] = True
    nombre_usuario = diccionario_correos[correo_destinatario]["nombre_corto"]
    # Aquí se pone el contenido del mensaje, que también puede ser un html
    mensaje.set_content(
        f'<!DOCTYPE html><html><head></head><body><h4>Hola, {nombre_usuario}</h4><p>Para recuperar tu contraseña, introduce el siguiente código de recuperación:</p></br><h3>{codigo_recuperacion}</h3><p>En el siguiente enlace:</p></br><a href="{host}/introducir_codigo_recuperacion/{nombre_usuario}">Cambiar mi contraseña</a></br><p>Si tu no iniciaste este proceso, ignora este correo y no pasará nada</p></br><p>Saludos,</p></br><p>-El equipo de VetCare</p></body></html>', subtype='html')
    # el servidor de correo electronico desde donde se va a enviar el mensaje va a ser Gmail
    correo_smtp = "smtp.gmail.com"
    # el puerto común utilizado para este servicio es el 587
    servidor = smtplib.SMTP(correo_smtp, '587')
    # se hace una conexión con el servidor y haciendolo de manera segura con el modo TLS
    servidor.ehlo()
    servidor.starttls()
    # se hace un login al servidor
    servidor.login(correo_remitente, contrasenia_correo_remitente)
    # se envia el correo
    servidor.send_message(mensaje)
    # se cierra la conexión con el servidor
    servidor.quit()


@login_blueprint.route('/introducir_codigo_recuperacion/<usuario>', methods=['GET', 'POST'])
def introducir_codigo_recuperacion(usuario):
    diccionario_usuarios = lee_diccionario_csv(
        archivo_usuarios, "nombre_corto")
    if request.method == 'GET':
        if usuario in diccionario_usuarios:
            if 'recuperando_contrasenia' in session:
                mostrar_toast = False
                return render_template('introducir_codigo_recuperacion.html', mensaje="", recuperando_contrasenia=True, mostrar_toast=mostrar_toast)
            else:
                mostrar_toast = True
                mensaje = f'El usuario {usuario} no ha iniciado el proceso de recuperación de contraseña.'
                asunto_mensaje = "Proceso no iniciado"
                icono = "/static/images/icono_fracaso.png"
                return render_template('introducir_codigo_recuperacion.html', recuperando_contrasenia=False, mostrar_toast=mostrar_toast, mensaje=mensaje, asunto_mensaje=asunto_mensaje, icono=icono)
        else:
            mostrar_toast = True
            mensaje = f"El usuario {usuario} no existe"
            asunto_mensaje = "Usuario inexistente"
            icono = "/static/images/icono_fracaso.png"
            return render_template('introducir_codigo_recuperacion.html', recuperando_contrasenia=False, mostrar_toast=mostrar_toast, mensaje=mensaje, asunto_mensaje=asunto_mensaje, icono=icono)
    else:
        # solo se puede dar este caso si el usuario está recuperando su contraseña, debido a que el boton de recuperar contraseña está deshabilitado hasta que se cumplan las
        # condiciones de que debe de existir ese usuario y que haya iniciado el proceso de recuperacion de contraseña
        if request.method == 'POST':
            codigo_recuperacion = int(request.form['codigo_recuperacion'])
            contrasenia = request.form['nueva_contrasenia']
            confirmacion_contrasenia = request.form['nueva_contrasenia_confirmacion']
            if codigo_recuperacion == session['codigo_recuperacion']:
                if contrasenia == confirmacion_contrasenia:
                    # se sobreescribe la contraseña anterior por la nueva contraseña encriptada en el diccionario de usuarios
                    diccionario_usuarios[usuario]['password'] = sha256_crypt.hash(
                        contrasenia)
                    # se guarda el diccionario con esa actualización de contraseña
                    guardar_diccionario(
                        archivo_usuarios, diccionario_usuarios)
                    # se "resetean" estos valores de las cookies, porque ya no se encuentra recuperando contrasenia
                    session.pop('recuperando_contrasenia', None)
                    # la llave del codigo de recuperacion se borra por seguridad, hasta un nuevo intento de recuperacion de contraseña
                    session.pop('codigo_recuperacion', None)
                    return redirect('/login/')
                else:
                    mostrar_toast = True
                    mensaje = f'Las dos contraseñas no coinciden'
                    asunto_mensaje = "Contraseñas no coinciden"
                    icono = "/static/images/icono_fracaso.png"
                    return render_template('introducir_codigo_recuperacion.html', mostrar_toast=mostrar_toast, mensaje=mensaje, recuperando_contrasenia=True, asunto_mensaje=asunto_mensaje, icono=icono)
            else:
                mostrar_toast = True
                mensaje = f'Código de recuperación incorrecto'
                asunto_mensaje = "Código incorrecto"
                icono = "/static/images/icono_fracaso.png"
                return render_template('introducir_codigo_recuperacion.html', mostrar_toast=mostrar_toast, mensaje=mensaje, recuperando_contrasenia=True, asunto_mensaje=asunto_mensaje, icono=icono)


@login_blueprint.route('/registrarse', methods=['GET', 'POST'])
@login_blueprint.route('/registrarse/', methods=['GET', 'POST'])
def registrarse():
    diccionario_usuarios = lee_diccionario_csv(
        archivo_usuarios, "nombre_corto")
    if request.method == "GET":
        return render_template('registrarse.html', mensaje="")
    else:
        if request.method == "POST":
            diccionario_correos = lee_diccionario_csv(
                archivo_usuarios, "email")
            nombre_corto = request.form['nombre_corto']
            nombre = request.form['nombre']
            email = request.form['email']
            password = sha256_crypt.hash(request.form['password'])
            # Un usuario que se registre, por defecto va a ser de tipo cliente
            tipo = "Cliente"
            # una de las validaciones que tenemos que hacer es que no se coloque un email que ya esté regitrado por otro usuario, por lo que
            # hay que checar eso
            # aquí se checa si el correo ya está registrado
            if email in diccionario_correos:
                mostrar_toast = True
                mensaje = "Ese correo ya ha sido registrado por otro usuario, intenta con otro correo"
                asunto_mensaje = "Correo ya registrado"
                icono = "/static/images/icono_fracaso.png"
                return render_template('registrarse.html', mostrar_toast=mostrar_toast, mensaje=mensaje, asunto_mensaje=asunto_mensaje, icono=icono)
            # si no se cumple la condición anterior, entonces se continua a lo de abajo
            # también se valida que el nombre_corto/username no esté ya en uso
            if nombre_corto in diccionario_usuarios:
                mostrar_toast = True
                mensaje = "Ese nombre corto ya ha sido registrado por otro usuario, intenta con otro username"
                asunto_mensaje = "Username ya registrado"
                icono = "/static/images/icono_fracaso.png"
                return render_template('registrarse.html', mostrar_toast=mostrar_toast, mensaje=mensaje, asunto_mensaje=asunto_mensaje, icono=icono)
            # esta validación es para evitar problemas en la parte de agendar citas, ya que esta secuencia se usa para un .split()
            if " -> " in nombre_corto:
                mostrar_toast = True
                mensaje = "El nombre de usuario no puede contener la siguiente secuencia: ' -> '"
                asunto_mensaje = "Secuencia inválida"
                icono = "/static/images/icono_fracaso.png"
                return render_template('registrarse.html', mostrar_toast=mostrar_toast, mensaje=mensaje, asunto_mensaje=asunto_mensaje, icono=icono)
            # con los datos obtenidos del formulario, se agrega a ese usuario en el diccionario de usuarios y luego se guarda en el archivo "usuarios.csv"
            diccionario_usuarios[nombre_corto] = {
                'nombre_corto': nombre_corto, 'nombre': nombre, 'email': email, 'password': password, 'tipo': tipo}
            # y se guardan los cambios en el archivo csv
            guardar_diccionario(archivo_usuarios,
                                diccionario_usuarios)
            # redireccionamos a index y asignamos la sesion de que el usuario ya se ha logeado.
            session['usuario'] = nombre_corto
            return redirect('/')


if __name__ == "__main__":
    texto_cript = sha256_crypt.hash("luis1234")
    print(texto_cript)
