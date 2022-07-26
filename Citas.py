from flask import Blueprint, redirect, render_template, request, session, jsonify
from Otros import guardar_diccionario, lee_diccionario_csv, crear_lista_objetos, guardar_lista_objetos
from Usuarios import crear_diccionario_cliente_mascota
import csv
from passlib.hash import sha256_crypt


citas_blueprint = Blueprint('citas_blueprint', __name__)

archivo_usuarios = "./files/usuarios.csv"
archivo_mascotas = "./files/mascotas.csv"
archivo_citas = "./files/citas.csv"
archivo_servicios = "./files/servicios.csv"


@citas_blueprint.route("/agendar_cita/", methods=['GET', 'POST'])
@citas_blueprint.route("/agendar_cita", methods=['GET', 'POST'])
def citas():
    diccionario_usuarios = lee_diccionario_csv(
        archivo_usuarios, "nombre_corto")
    diccionario_cliente_mascota = crear_diccionario_cliente_mascota(
        archivo_mascotas)
    diccionario_correos = lee_diccionario_csv(archivo_usuarios, "email")
    diccionario_servicios = lee_diccionario_csv(archivo_servicios, "id")
    if request.method == 'GET':
        return render_template("agendar_cita.html", usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascota, usuarios=diccionario_usuarios, servicios=diccionario_servicios, mensaje="")
    else:
        if request.method == 'POST':
            # 4 formularios, 1 para cliente, otros 3 para usuario/administrador que son agendar cita, agrega usuario/mascota y agregar mascota a un usuario ya registrado
            if 'agendar' in request.form:
                # cliente
                if request.form['agendar'] == "Agendar":
                    fecha_cita = request.form['fecha']
                    hora_cita = request.form['hora']
                    nombre_mascota = request.form['nombre_mascota']
                    tipo_mascota = request.form['tipo_mascota']
                    # lo que se obtiene es el id del servicio, que se va a relacionar con el id del archivo 'servicios.csv'
                    id_servicio = request.form['id_servicio']
                    if id_servicio not in diccionario_servicios:
                        return render_template('agendar_cita.html', usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascota, usuarios=diccionario_usuarios, servicios=diccionario_servicios, mensaje="Ese servicio no existe, elige o inserta una ID válida")
                    lista_citas = crear_lista_objetos(archivo_citas)
                    lista_mascotas = crear_lista_objetos(archivo_mascotas)
                    # esta id va a ser útil para identificar a cada cita y formar las url de modificar, se va ir asignando automáticamente
                    # conforme vaya creciendo la lista de citas
                    cita = {'id': len(lista_citas), 'nombre_cliente': session['usuario'], 'nombre_mascota': nombre_mascota,
                            'fecha': fecha_cita, 'hora': hora_cita, 'id_servicio': id_servicio}
                    mascota = {'nombre': nombre_mascota,
                               'tipo': tipo_mascota, 'duenio': session['usuario']}
                    lista_citas.append(cita)
                    lista_mascotas.append(mascota)
                    # y se guardan los cambios en el archivo csv
                    guardar_lista_objetos(archivo_citas, lista_citas)
                    guardar_lista_objetos(archivo_mascotas, lista_mascotas)
                    # se actualiza el diccionario
                    diccionario_cliente_mascota = crear_diccionario_cliente_mascota(
                        archivo_mascotas)
                    return render_template('agendar_cita.html', usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascota, usuarios=diccionario_usuarios, servicios=diccionario_servicios, mensaje="Cita agregada con éxito")
                    # usuario/administrador
                elif request.form['agendar'] == "Agendar cita":
                    cliente_mascota = request.form['cliente_mascota']
                    # en el formulario, donde se selecciona al cliente y mascota, el valor que obtenemos
                    # de ahí tiene la forma: "nombre_corto_cliente -> nombre_mascota", por lo que hay que separar
                    # ambos datos con un .split(), pero como el usuario tiene la libertad de escribir lo que sea en ese
                    # input, necesitamos prevenir un posible crasheo de la página cuando el usuario introduzca un valor
                    # que no tenga esa forma, usando este try
                    # de igual manera en todos los sitios donde se pueda agregar un cliente o mascota, se valida que sus nombres
                    # no contengan la secuencia " -> "
                    try:
                        datos = cliente_mascota.split(" -> ")
                        nombre_corto_cliente = datos[0]
                        nombre_mascota = datos[1]
                    except:
                        return render_template('agendar_cita.html', usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascota, usuarios=diccionario_usuarios, servicios=diccionario_servicios, mensaje="Selecciona un cliente y mascota válidos ('nombre_corto_cliente -> nombre_mascota')")
                    # se valida si el usuario existe
                    if nombre_corto_cliente not in diccionario_usuarios:
                        return render_template('agendar_cita.html', usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascota, usuarios=diccionario_usuarios, servicios=diccionario_servicios, mensaje="Ese cliente no existe")
                    # se obtienen a las mascotas del cliente
                    mascotas_cliente = diccionario_cliente_mascota[nombre_corto_cliente]
                    usuario_tiene_esa_mascota = False
                    # se recorren las mascotas del cliente para ver si tiene a la mascota especificada en el formulario
                    for mascota in mascotas_cliente:
                        if mascota['nombre'] == nombre_mascota:
                            usuario_tiene_esa_mascota = True
                            break
                    if usuario_tiene_esa_mascota == False:
                        return render_template('agendar_cita.html', usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascota, usuarios=diccionario_usuarios, servicios=diccionario_servicios, mensaje=f"Ese cliente no tiene una mascota llamada {nombre_mascota}, agrega esa mascota con el botón 'Agregar mascota'")
                    fecha_cita = request.form['fecha']
                    hora_cita = request.form['hora']
                    id_servicio = request.form['id_servicio']
                    if id_servicio not in diccionario_servicios:
                        return render_template('agendar_cita.html', usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascota, usuarios=diccionario_usuarios, servicios=diccionario_servicios, mensaje="Ese servicio no existe, elige o inserta una ID válida")
                    lista_citas = crear_lista_objetos(archivo_citas)
                    cita = {'id': len(lista_citas), 'nombre_cliente': nombre_corto_cliente, 'nombre_mascota': nombre_mascota,
                            'fecha': fecha_cita, 'hora': hora_cita, 'id_servicio': id_servicio}
                    lista_citas.append(cita)
                    guardar_lista_objetos(archivo_citas, lista_citas)
                    return render_template('agendar_cita.html', usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascota, usuarios=diccionario_usuarios, servicios=diccionario_servicios, mensaje="Cita agregada con éxito")

            # usuario/administrador
            # este es para agregar usuario y mascota
            elif 'agregar_usuario_mascota' in request.form:
                # se obtienen los datos del cliente y su mascota
                nombre_corto_cliente = request.form['nombre_corto']
                nombre_cliente = request.form['nombre']
                email = request.form['email']
                # por defecto es un cliente el que se agrega
                tipo = "Cliente"
                password = sha256_crypt.hash(request.form['password'])
                nombre_mascota = request.form['nombre_mascota']
                tipo_mascota = request.form['tipo_mascota']
                # hay que validar que el username y correo no estén registrados ya
                if nombre_corto_cliente in diccionario_usuarios:
                    return render_template("agendar_cita.html", usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascota, usuarios=diccionario_usuarios, servicios=diccionario_servicios, mensaje="Ese username ya está en uso, intenta con otro")
                if email in diccionario_correos:
                    return render_template("agendar_cita.html", usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascota, usuarios=diccionario_usuarios, servicios=diccionario_servicios, mensaje="Ese correo ya está en uso, intenta con otro")
                # hay que validar también que el username, ni el nombre de mascota contengan " -> ", porque daría problemas con la parte de seleccion de usuario/mascota.
                if " -> " in nombre_corto_cliente or " -> " in nombre_mascota:
                    return render_template("agendar_cita.html", usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascota, usuarios=diccionario_usuarios, servicios=diccionario_servicios, mensaje="Ni el nombre de usuario, ni el de mascota pueden contener esta secuencia: ' -> '")
                # con los datos obtenidos del formulario, se agrega a ese usuario en el diccionario de usuarios y luego se guarda en el archivo "usuarios.csv"
                diccionario_usuarios[nombre_corto_cliente] = {
                    'nombre_corto': nombre_corto_cliente, 'nombre': nombre_cliente, 'email': email, 'password': password, 'tipo': tipo}
                # y se guardan los cambios en el archivo csv
                guardar_diccionario(archivo_usuarios,
                                    diccionario_usuarios)
                # también se guarda a la mascota
                mascota = {'nombre': nombre_mascota,
                           'tipo': tipo_mascota, 'duenio': nombre_corto_cliente}
                mascotas = crear_lista_objetos(archivo_mascotas)
                mascotas.append(mascota)
                guardar_lista_objetos(archivo_mascotas, mascotas)
                diccionario_cliente_mascota = crear_diccionario_cliente_mascota(
                    archivo_mascotas)
                return render_template("agendar_cita.html", usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascota, usuarios=diccionario_usuarios, servicios=diccionario_servicios, mensaje="Cliente y mascota agregados con éxito")
            # usuario/administrador
            # este es para agregar una mascota a un usuario
            elif 'agregar_mascota' in request.form:
                nombre_corto_cliente = request.form['username_cliente']
                nombre_mascota = request.form['nombre_mascota']
                tipo_mascota = request.form['tipo_mascota']
                # validamos que el usuario no haya puesto un cliente que no aparezca en las opciones
                if nombre_corto_cliente not in diccionario_usuarios:
                    return render_template("agendar_cita.html", usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascota, usuarios=diccionario_usuarios, servicios=diccionario_servicios,  mensaje="Ese cliente no existe")
                if " -> " in nombre_mascota:
                    return render_template("agendar_cita.html", usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascota, usuarios=diccionario_usuarios, servicios=diccionario_servicios, mensaje="El nombre de la mascota no puede contener esta secuencia: ' -> '")
                mascota = {'nombre': nombre_mascota,
                           'tipo': tipo_mascota, 'duenio': nombre_corto_cliente}
                mascotas = crear_lista_objetos(archivo_mascotas)
                mascotas.append(mascota)
                guardar_lista_objetos(archivo_mascotas, mascotas)
                diccionario_cliente_mascota = crear_diccionario_cliente_mascota(
                    archivo_mascotas)
                return render_template("agendar_cita.html", usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascota, usuarios=diccionario_usuarios, servicios=diccionario_servicios, mensaje=f"Mascota agregada con éxito a {nombre_corto_cliente}")


@citas_blueprint.route("/tabla_citas")
def tabla_citas():
    if request.method == 'GET':
        diccionario_usuarios = lee_diccionario_csv(
            archivo_usuarios, "nombre_corto")
        diccionario_servicios = lee_diccionario_csv(
            archivo_servicios, "id")
        usuario = diccionario_usuarios[session['usuario']]
        lista = []
        # se obtiene la lista de las citas de todos los clientes
        lista_objetos = crear_lista_objetos(
            archivo_citas)
        lista_citas = []
        # si el usuario es un Cliente, en el JSON solo debemos de mandar las citas que son solo de él
        if usuario['tipo'] == "Cliente":
            for cita in lista_objetos:
                if cita['nombre_cliente'] == usuario['nombre_corto']:
                    lista_citas.append(cita)
        # este podría ser un else directamente, pero por legibilidad, este elif checa si se trata de un Usuario o un Administrador,
        # en ambos casos se van a mostrar todas las citas de todos los clientes.
        elif usuario['tipo'] == "Usuario" or usuario['tipo'] == "Administrador":
            lista_citas = lista_objetos
        for cita in lista_citas:
            #
            # para evitar problemas de mutabilidad y no alterar la lista de citas, se hace una copia de cada cita.
            cita_a_guardar = cita.copy()
            # de igual modo, se le agrega este otro valor que va a ser una de las columnas de la tabla de citas, es por esto que no se queria mutar a la lista de citas original
            cita_a_guardar[
                'url_modificacion'] = f'<a href="/modificar_cita/{cita_a_guardar["id"]}">Modificar</a>'
            servicio = diccionario_servicios[cita['id_servicio']]
            cita_a_guardar['servicio'] = servicio['tipo_servicio'] + \
                " - " + servicio['servicio']
            lista.append(cita_a_guardar)
        return jsonify(lista)


@citas_blueprint.route("/modificar_cita/<cita_id>", methods=['GET', 'POST'])
def modificar(cita_id):
    diccionario_citas = lee_diccionario_csv(
        archivo_citas, "id")
    diccionario_servicios = lee_diccionario_csv(archivo_servicios, "id")
    # por si se trata de acceder e esta página buscando mediante la barra de navegación directamente, hay que checar si esa cita está registrada en el sistema
    if cita_id not in diccionario_citas:
        return render_template('modificar_cita.html', cita_existente=False, servicios=diccionario_servicios)
    else:
        if request.method == "GET":
            return render_template('modificar_cita.html', cita_existente=True, datos_cita=diccionario_citas[cita_id], servicios=diccionario_servicios)
        else:
            if request.method == "POST":
                # los datos de id, nombre_cliente y nombre_mascota van a ser inmodificables en el formulario, debido a que si uno de esos valores
                # cambia, pueden afectar la consistencia de los datos con los demás archivos, también porque así se simula que
                # al modificar una cita, un cliente le pida a un usuario que cambie la fecha, hora o el servicio, lo que si es posible
                # hacer y puede ser común
                id = request.form['id']
                nombre_cliente = request.form['nombre_cliente']
                nombre_mascota = request.form['nombre_mascota']
                fecha = request.form['fecha']
                hora = request.form['hora']
                id_servicio = request.form['id_servicio']
                # con los datos obtenidos del formulario, se modifica el diccionario de citas, especificamente los valores de la cita
                # con llave 'id'
                diccionario_citas[id] = {
                    'id': id, 'nombre_cliente': nombre_cliente, 'nombre_mascota': nombre_mascota, 'fecha': fecha, 'hora': hora, 'id_servicio': id_servicio}
                # y se guardan los cambios en el archivo csv
                guardar_diccionario(archivo_citas,
                                    diccionario_citas)
                # redireccionamos a donde está la lista de medicinas
                return redirect('/agendar_cita/')
