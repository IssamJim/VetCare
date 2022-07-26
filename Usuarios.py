from flask import Blueprint, redirect, render_template, request, session, jsonify
from Otros import guardar_diccionario, lee_diccionario_csv
from passlib.hash import sha256_crypt
import csv


class Usuario:
    def __init__(self, nombre_corto, nombre, email, tipo):
        self.nombre_corto = nombre_corto
        self.nombre = nombre
        self.email = email
        self.tipo = tipo

    def __str__(self):
        return f'Usuario: {self.nombre_corto}, nombre: {self.nombre}, correo: {self.email}'


archivo_usuarios = "./files/usuarios.csv"

usuarios_blueprint = Blueprint('usuarios_blueprint', __name__)


@usuarios_blueprint.route('/usuarios')
@usuarios_blueprint.route('/usuarios/')
def usuarios():
    diccionario_usuarios = lee_diccionario_csv(
        archivo_usuarios, "nombre_corto")
    return render_template('usuarios.html', usuarios=diccionario_usuarios)


@usuarios_blueprint.route("/tabla_usuarios")
def tabla_usuarios():
    if request.method == 'GET':
        lista = []
        diccionario_usuarios = lee_diccionario_csv(
            archivo_usuarios, "nombre_corto")
        for nombre_corto, usuario in diccionario_usuarios.items():
            # Del diccionario de usuarios extraemos los datos que vamos a mostrar en el listado de usuarios para el administrador,
            # no mandamos directamente el diccionario 'usuario' porque en el JSON estaría incluida la password, aunque esté encriptada,
            # puede ser inseguro
            nombre = usuario['nombre']
            email = usuario['email']
            tipo = usuario['tipo']
            usuario_temp = Usuario(nombre_corto, nombre, email, tipo)
            # se utiliza la función vars() para convertir el objeto en un diccionario, porque parece que jsonify no puede serializar
            # objetos, solo diccionarios
            usuario_dict = vars(usuario_temp)
            usuario_dict['url_modificacion'] = f'<a href="/modificar_usuario/{nombre_corto}">Modificar</a>'
            lista.append(usuario_dict)
        return jsonify(lista)


@usuarios_blueprint.route("/agregar_usuario", methods=['GET', 'POST'])
def agregar_usuario():
    if request.method == "GET":
        return render_template('agregar_usuario.html', mensaje="")
    else:
        diccionario_usuarios = lee_diccionario_csv(
            archivo_usuarios, "nombre_corto")
        diccionario_correos = lee_diccionario_csv(archivo_usuarios, "email")
        if request.method == "POST":
            # aquí tenemos que validar que no haya un usuario con un mismo nombre_corto ni que tampoco ya haya un correo registrado en algun usuario,
            # por lo que necesitamos validar esos 2 puntos
            nombre_corto = request.form['nombre_corto']
            # se valida que no haya ya un usuario con ese nombre
            if nombre_corto in diccionario_usuarios:
                return render_template('agregar_usuario.html', mensaje="Ya hay un usuario con ese mismo username, intenta con otro username")
            # validar esto para la parte de citas, ya que se usa un split() con esa secuencia
            if " -> " in nombre_corto:
                return render_template('agregar_usuario.html', mensaje="El nombre de usuario no puede contener la secuencia: ' -> '")
            nombre = request.form['nombre']
            email = request.form['email']
            if email in diccionario_correos:
                return render_template('agregar_usuario.html', mensaje="Ya hay un usuario que tiene ese correo registrado, intenta con otro correo")
            # si no se cumplió ninguna de las 2 condiciones anteriores, entonces se puede seguir con el proceso de agregado
            # directamente se encripta la contraseña
            password = sha256_crypt.hash(request.form['password'])
            tipo = request.form['tipo']
            # con los datos obtenidos del formulario, se agrega ese usuario al diccionario de usuarios
            diccionario_usuarios[nombre_corto] = {
                'nombre_corto': nombre_corto, 'nombre': nombre, 'email': email, 'password': password, 'tipo': tipo}
            # y se guardan los cambios en el archivo csv
            guardar_diccionario(archivo_usuarios,
                                diccionario_usuarios)
            # redireccionamos a donde está la lista de usuarios
            return redirect('/usuarios/')


@usuarios_blueprint.route("/modificar_usuario/<usuario>", methods=['GET', 'POST'])
def modificar(usuario):
    diccionario_usuarios = lee_diccionario_csv(
        archivo_usuarios, "nombre_corto")
    # por si se trata de acceder e esta página buscando mediante la barra de navegación directamente, hay que checar si ese usuario está registrado en el sistema
    if usuario not in diccionario_usuarios:
        return render_template('modificar_usuario.html', usuario_existente=False)
    else:
        if request.method == "GET":
            return render_template('modificar_usuario.html', usuario_existente=True, datos_usuario=diccionario_usuarios[usuario], mensaje="")
        else:
            if request.method == "POST":
                diccionario_correos = lee_diccionario_csv(
                    archivo_usuarios, "email")
                # en el template de 'modificar_usuario.html', en los distintos campos se tiene el atributo required, para que forzosamente
                # se tenga que introducir un dato y no se deje en blanco alguno de los campos, además podemos ahorrarnos las validaciones
                # de los emails por ejemplo en una parte, ya que eso se tendría que hacer de forma más avanzada posiblemente con Javascript
                # el unico valor que no se va a modificar es el nombre_corto porque es el que funge como la "llave primaria" en el diccionario,
                # y es el que distingue a los usuarios, también se evita una posible duplicación de usuarios si se llegara a colocar un username
                # que ya está registrado
                nombre_corto = request.form['nombre_corto']
                nombre = request.form['nombre']
                email = request.form['email']
                # una de las validaciones que tenemos que hacer es que no se coloque un email que ya esté regitrado por otro usuario, por lo que
                # hay que checar eso
                correo_actual_usuario = diccionario_usuarios[nombre_corto]['email']
                # aquí se checa si el correo ya está registrado, pero también verifica si el correo actual del usuario no es igual al proporcionado
                # en el formulario, de este modo, si cuando se está modificando a un usuario, el correo no se modifica, sepa que es porque es su correo
                # y no el de otro usuario, por lo que la modificación se completaría correctamente y no se recargaría la página mostrando el mensaje del if de abajo
                if email in diccionario_correos and correo_actual_usuario != email:
                    return render_template('modificar_usuario.html', usuario_existente=True, datos_usuario=diccionario_usuarios[usuario], mensaje="Ese correo ya ha sido registrado por otro usuario, intenta con otro correo")
                # si no se cumple la condición anterior, entonces se continua a lo de abajo
                tipo = request.form['tipo']
                # la contraseña la obtenemos directamente del diccionario de usuarios
                password = diccionario_usuarios[nombre_corto]['password']
                # con los datos obtenidos del formulario, se modifica el diccionario de usuarios, especificamente los valores del usuario
                # con llave 'nombre_corto'
                diccionario_usuarios[nombre_corto] = {
                    'nombre_corto': nombre_corto, 'nombre': nombre, 'email': email, 'password': password, 'tipo': tipo}
                # y se guardan los cambios en el archivo csv
                guardar_diccionario(archivo_usuarios,
                                    diccionario_usuarios)
                # redireccionamos a donde está la lista de usuarios
                return redirect('/usuarios/')


def crear_diccionario_cliente_mascota(archivo_mascotas: str) -> dict:
    """
    Esta función recibe como parámetro un archivo de mascotas y se encarga de retornar un diccionario, donde las llaves son los username de los clientes
    y los valores son todas sus mascotas (junto con todos los datos de esas mascotas)
    """
    diccionario_cliente_mascota = {}
    try:
        with open(archivo_mascotas, 'r', encoding='latin-1') as fh:
            csv_reader = csv.DictReader(fh)
            for mascota in csv_reader:
                llave_cliente = mascota['duenio']
                if llave_cliente not in diccionario_cliente_mascota:
                    diccionario_cliente_mascota[llave_cliente] = [mascota]
                else:
                    diccionario_cliente_mascota[llave_cliente].append(mascota)
    except IOError:
        print(f"No se pudo leer el archivo {archivo_mascotas}")
    return diccionario_cliente_mascota
