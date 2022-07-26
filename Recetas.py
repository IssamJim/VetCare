from flask import Blueprint, redirect, render_template, request, session, jsonify
from Otros import guardar_diccionario, lee_diccionario_csv, crear_lista_objetos, ordenar_por_fecha_hora_desc
from Usuarios import crear_diccionario_cliente_mascota


archivo_medicinas = "./files/medicinas.csv"
archivo_mascotas = "./files/mascotas.csv"
archivo_usuarios = "./files/usuarios.csv"
archivo_recetas = "./files/recetas.csv"

recetas_blueprint = Blueprint('recetas_blueprint', __name__)


@recetas_blueprint.route("/tabla_medicinas")
def tabla_medicinas():
    if request.method == 'GET':
        lista = []
        diccionario_medicinas = lee_diccionario_csv(
            archivo_medicinas, "nombre")
        for nombre, medicina in diccionario_medicinas.items():
            # Del diccionario de medicinas se extraen cada una de las medicinas y se agregan a los los datos que vamos a mostrar en el listado de medicinas para el administrador
            # para evitar problemas de mutabilidad y no alterar el diccionario, se hace una copia de éste.
            medicina_a_guardar = medicina.copy()
            # de igual modo, se le agrega este otro valor que va a ser una de las columnas de la tabla de medicinas, es por esto que no se queria mutar al diccionario de medicinas original
            medicina_a_guardar[
                'url_modificacion'] = f'<a href="/modificar_medicina/{nombre}">Modificar</a>'
            lista.append(medicina_a_guardar)
        # print(diccionario_medicinas.items())
        # print(diccionario_medicinas)
        return jsonify(lista)


@recetas_blueprint.route("/medicinas")
@recetas_blueprint.route("/medicinas/")
def medicinas():
    diccionario_medicinas = lee_diccionario_csv(
        archivo_medicinas, "nombre")
    return render_template("medicinas.html", medicinas=diccionario_medicinas)


@recetas_blueprint.route("/agregar_medicina", methods=['GET', 'POST'])
def agregar_medicina():
    if request.method == "GET":
        return render_template('agregar_medicina.html', mensaje="")
    else:
        diccionario_medicinas = lee_diccionario_csv(
            archivo_medicinas, "nombre")
        if request.method == "POST":
            # aquí tenemos que validar que no haya una medicina con un nombre igual, ya que éste será el identificador de cada medicina.
            nombre = request.form['nombre']
            # se valida que no haya ya una medicina con ese nombre
            if nombre in diccionario_medicinas:
                return render_template('agregar_medicina.html', mensaje="Ya hay una medicina con ese mismo nombre, intenta con otro nombre")
            descripcion = request.form['descripcion']
            presentacion = request.form['presentacion']
            medida = request.form['medida']
            # con los datos obtenidos del formulario, se agrega esa medicina al diccionario de medicinas
            diccionario_medicinas[nombre] = {
                'nombre': nombre, 'descripcion': descripcion, 'tipo_presentacion': presentacion, 'tipo_medida': medida}
            # y se guardan los cambios en el archivo csv
            guardar_diccionario(archivo_medicinas,
                                diccionario_medicinas)
            # redireccionamos a donde está la lista de medicinas
            return redirect('/medicinas/')


@recetas_blueprint.route("/modificar_medicina/<medicina>", methods=['GET', 'POST'])
def modificar(medicina):
    diccionario_medicinas = lee_diccionario_csv(
        archivo_medicinas, "nombre")
    # por si se trata de acceder e esta página buscando mediante la barra de navegación directamente, hay que checar si esa medicina está registrada en el sistema
    if medicina not in diccionario_medicinas:
        return render_template('modificar_medicina.html', medicina_existente=False)
    else:
        if request.method == "GET":
            return render_template('modificar_medicina.html', medicina_existente=True, datos_medicina=diccionario_medicinas[medicina])
        else:
            if request.method == "POST":
                nombre = request.form['nombre']
                descripcion = request.form['descripcion']
                presentacion = request.form['presentacion']
                medida = request.form['medida']
                # con los datos obtenidos del formulario, se modifica el diccionario de medicinas, especificamente los valores de la medicina
                # con llave 'nombre'
                diccionario_medicinas[nombre] = {
                    'nombre': nombre, 'descripcion': descripcion, 'tipo_presentacion': presentacion, 'tipo_medida': medida}
                # y se guardan los cambios en el archivo csv
                guardar_diccionario(archivo_medicinas,
                                    diccionario_medicinas)
                # redireccionamos a donde está la lista de medicinas
                return redirect('/medicinas/')


@recetas_blueprint.route("/agregar_receta", methods=['GET', 'POST'])
@recetas_blueprint.route("/agregar_receta/", methods=['GET', 'POST'])
def agregar_receta():
    receta = ""
    diccionario_medicinas = lee_diccionario_csv(archivo_medicinas, "nombre")
    diccionario_cliente_mascota = crear_diccionario_cliente_mascota(
        archivo_mascotas)
    diccionario_usuarios = lee_diccionario_csv(
        archivo_usuarios, "nombre_corto")
    if request.method == "GET":
        return render_template("agregar_receta.html", medicinas=diccionario_medicinas, clientes_mascotas=diccionario_cliente_mascota, receta_actual="")
    else:
        if request.method == "POST":
            cliente_mascota = request.form['cliente_mascota']
            fecha = request.form['fecha']
            hora = request.form['hora']
            # la forma en la que se ponen las medicinas en el template de agregar_receta, es que el usuario tiene
            # la libertad de agregar todas las que quiera, por los que se van creando varios inputs dinamicamente,
            # es por eso que como no conocemos cuantas haya puesto y que request.form es un diccionario, podemos
            # recorrerlo para obtener todos los input
            medicinas_agregadas = {}
            for llave, valor in request.form.items():
                # en el templata con ayuda de javascript ibamos aniadiendo ids y names a los diferentes inputs de las
                # medicinas con la forma: medicina(numero) y cantidad(numero), por lo que hay que llecar las llaves/ids/names,
                # de los inputs que empiezen con 'medicina' y 'cantidad'
                if llave.startswith("medicina"):
                    # separamos el id/name, tiene la forma: "medicina01" y queremos obtener el id "01" por ejemplo
                    separacion_medicina_id = llave.split("medicina")
                    id = separacion_medicina_id[1]
                    # obtenemos la llave para acceder al valor del checkbox que indica si se cancela una medicina o no
                    llave_cancelar_medicina = f'cancelar_medicina{id}'
                    # para un checkbox se require usar el get
                    valor_cancelar_medicina = request.form.get(
                        llave_cancelar_medicina)
                    # si no se canceló la medicina o si se especificó la medicina, se agrega
                    # se checa que no se haya seleccionado el checkbox de cancelar y que se haya especificado una medicina en el input asociado
                    # debido a que los dinámicos no son required
                    print("checkbox: ", valor_cancelar_medicina)
                    if (valor_cancelar_medicina != "medicina_cancelada") or (request.form[llave] == "" or request.form[llave] == None):
                        # aprovechando que tenemos la id de la medicina, esa misma id la usamos para obtener la cantidad asociada
                        # a esa medicina, como los campos de los inputs dinamicos no son required, porque se generaban problemas al tratar
                        # de borrar una medicina en la receta, es por eso que optamos por usar un checkbox para ignorar las medicinas que se cancelen
                        # como lo que se mencionó en la clase del 27/04/2022
                        llave_cantidad = f'cantidad{id}'
                        cantidad = request.form[llave_cantidad]
                        # como los campos de los inputs dinamicos no son required, hay que checar si la cantidad no se especificó
                        if cantidad == "" or cantidad == None:
                            cantidad = "cantidad no especificada en "
                        # también checamos que la medicina agregado esté registrada, porque en los datalist se puede escribir, además de seleccionar
                        if valor in diccionario_medicinas:
                            # si está, se agrega
                            medicinas_agregadas[id] = {
                                'medicina': valor, 'cantidad': cantidad}
            receta = ""
            for id, medicina in medicinas_agregadas.items():
                receta += f"-{medicina['medicina']} {medicina['cantidad']}{diccionario_medicinas[medicina['medicina']]['tipo_medida']}, "
            # se puede dar el caso en que no se agregue alguna medicina dinámica y solo se llene la primera medicina que es obligatoria,
            # pero que esa medicina no se encuentre registrada, ya sea por que el usario no seleccionó entre la lista de medicinas disponibles
            # en el datalist y solo escribió algún nombre de medicina que no esté registrado
            if receta == "":
                return render_template("agregar_receta.html", medicinas=diccionario_medicinas, clientes_mascotas=diccionario_cliente_mascota, receta_actual=receta, mensaje="Selecciona medicinas registradas en el sistema, por favor")
            # anteriormente las medicinas se concatenaban con ", ", por lo que cuando se agregue la ultima, al final va a quedar ", ",
            # es por eso que aquí quitamos esa parte del final
            if receta.endswith(", "):
                # se quitan los ultimos 2 caracteres, la coma y el espacio en blanco
                receta = receta[:-2]
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
                return render_template("agregar_receta.html", medicinas=diccionario_medicinas, clientes_mascotas=diccionario_cliente_mascota, receta_actual=receta, mensaje="Selecciona un cliente y mascota válidos ('nombre_corto_cliente -> nombre_mascota')")
            # se valida si el usuario existe
            if nombre_corto_cliente not in diccionario_usuarios:
                return render_template("agregar_receta.html", medicinas=diccionario_medicinas, clientes_mascotas=diccionario_cliente_mascota, receta_actual=receta, mensaje="Ese cliente no existe")
            # se obtienen a las mascotas del cliente
            mascotas_cliente = diccionario_cliente_mascota[nombre_corto_cliente]
            usuario_tiene_esa_mascota = False
            # se recorren las mascotas del cliente para ver si tiene a la mascota especificada en el formulario
            for mascota in mascotas_cliente:
                if mascota['nombre'] == nombre_mascota:
                    usuario_tiene_esa_mascota = True
                    break
            if usuario_tiene_esa_mascota == False:
                return render_template("agregar_receta.html", medicinas=diccionario_medicinas, clientes_mascotas=diccionario_cliente_mascota, receta_actual=receta, mensaje=f"Ese cliente no tiene una mascota llamada {nombre_mascota}")
            diccionario_recetas = lee_diccionario_csv(
                archivo_recetas, "id")
            id = len(diccionario_recetas)
            diccionario_recetas[id] = {'id': id, 'cliente': nombre_corto_cliente,
                                       'mascota': nombre_mascota, 'receta': receta, 'fecha': fecha, 'hora': hora}
            guardar_diccionario(archivo_recetas, diccionario_recetas)
            # se redirecciona a la pagina donde puede generar el PDF o agregar mas atenciones
            return redirect(f"/receta_agregada_exitosamente/{id}")


@recetas_blueprint.route("/receta_agregada_exitosamente/<id_receta>", methods=['GET'])
def receta_agregada_exitosamente(id_receta):
    return render_template("receta_agregada_exitosamente.html", id_receta=id_receta)


@recetas_blueprint.route("/receta/<id_receta>")
def receta(id_receta):
    diccionario_recetas = lee_diccionario_csv(
        archivo_recetas, "id")
    if id_receta not in diccionario_recetas:
        return render_template("receta.html", receta_existente=False, receta_a_buscar={})
    receta_busqueda = diccionario_recetas[id_receta]
    return render_template("receta.html", receta_existente=True, receta_a_buscar=receta_busqueda)


@recetas_blueprint.route("/tabla_recetas")
def tabla_recetas():
    if request.method == 'GET':
        diccionario_usuarios = lee_diccionario_csv(
            archivo_usuarios, "nombre_corto")
        diccionario_recetas = lee_diccionario_csv(
            archivo_recetas, "id")
        usuario = diccionario_usuarios[session['usuario']]
        lista = []
        # se obtiene la lista de las recetas de todos los clientes
        lista_objetos = crear_lista_objetos(
            archivo_recetas)
        lista_recetas = []
        # si el usuario es un Cliente, en el JSON solo debemos de mandar las recetas que son solo de él
        if usuario['tipo'] == "Cliente":
            for receta in lista_objetos:
                if receta['cliente'] == usuario['nombre_corto']:
                    lista_recetas.append(receta)
        # este podría ser un else directamente, pero por legibilidad, este elif checa si se trata de un Usuario o un Administrador,
        # en ambos casos se van a mostrar todas las recetas de todos los clientes.
        elif usuario['tipo'] == "Usuario" or usuario['tipo'] == "Administrador":
            lista_recetas = lista_objetos
        for receta in lista_recetas:
            #
            # para evitar problemas de mutabilidad y no alterar la lista de recetas, se hace una copia de cada receta.
            receta_a_guardar = receta.copy()
            # de igual modo, se le agrega este otro valor que va a ser una de las columnas de la tabla de recetas, es por esto que no se queria mutar a la lista de recetas original
            receta_a_guardar[
                'url_generar_pdf'] = f'<a href="/generar_pdf/receta/{receta_a_guardar["id"]}" target="_blank">Generar PDF</a>'
            lista.append(receta_a_guardar)
        # la lista de recetas hecha anteriormente, es ordenada por fecha y hora descendente
        lista_ordenada = ordenar_por_fecha_hora_desc(
            lista)
        return jsonify(lista_ordenada)
