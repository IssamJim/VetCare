from flask import Blueprint, redirect, render_template, request, session, jsonify
from Otros import guardar_diccionario, lee_diccionario_csv, ordenar_por_fecha_hora_desc, crear_lista_objetos
from Usuarios import crear_diccionario_cliente_mascota


atenciones_blueprint = Blueprint('atenciones_blueprint', __name__)

archivo_atenciones = "./files/atenciones.csv"
archivo_servicios = "./files/servicios.csv"
archivo_mascotas = "./files/mascotas.csv"
archivo_usuarios = "./files/usuarios.csv"


@atenciones_blueprint.route("/servicios", methods=['GET', 'POST'])
@atenciones_blueprint.route("/servicios/", methods=['GET', 'POST'])
def servicios():
    if request.method == "GET":
        return render_template("servicios.html", mensaje="")
    else:
        if request.method == "POST":
            diccionario_servicios = lee_diccionario_csv(
                archivo_servicios, "id")
            # el id de los servicios se incrementa automáticamente
            id = len(diccionario_servicios)
            tipo_servicio = request.form['tipo_servicio']
            servicio = request.form['servicio']
            # se agrega el nuevo servicio
            diccionario_servicios[id] = {
                'id': id, 'tipo_servicio': tipo_servicio, 'servicio': servicio}
            # se guarda el servicio
            guardar_diccionario(archivo_servicios, diccionario_servicios)
            return render_template("servicios.html", mensaje="Servicio agregado con éxito")


@atenciones_blueprint.route("/tabla_servicios")
def tabla_servicios():
    if request.method == 'GET':
        lista = []
        diccionario_servicios = lee_diccionario_csv(
            archivo_servicios, "id")
        for id, servicio in diccionario_servicios.items():
            # para evitar problemas de mutabilidad
            servicio_a_guardar = servicio.copy()
            servicio_a_guardar[
                'url_modificacion'] = f'<a href="/modificar_servicio/{id}">Modificar</a>'
            lista.append(servicio_a_guardar)
        return jsonify(lista)


@atenciones_blueprint.route("/modificar_servicio/<id_servicio>", methods=['GET', 'POST'])
def modificar_servicio(id_servicio):
    diccionario_servicios = lee_diccionario_csv(
        archivo_servicios, "id")
    # por si se trata de acceder e esta página buscando mediante la barra de navegación directamente, hay que checar si ese servicio está registrada en el sistema
    if id_servicio not in diccionario_servicios:
        return render_template('modificar_servicio.html', servicio_existente=False)
    else:
        if request.method == "GET":
            return render_template('modificar_servicio.html', servicio_existente=True, datos_servicio=diccionario_servicios[id_servicio])
        else:
            if request.method == "POST":
                # la id es la única inmodificable
                id = request.form['id']
                tipo_servicio = request.form['tipo_servicio']
                servicio = request.form['servicio']
                # con los datos obtenidos del formulario, se modifica el diccionario de servicios, especificamente los valores del servicio
                # con llave 'id'
                diccionario_servicios[id] = {
                    'id': id, 'tipo_servicio': tipo_servicio, 'servicio': servicio}
                # y se guardan los cambios en el archivo csv
                guardar_diccionario(archivo_servicios,
                                    diccionario_servicios)
                # redireccionamos a la lista de servicios
                return redirect('/servicios/')


@atenciones_blueprint.route("/agregar_atencion", methods=['GET', 'POST'])
@atenciones_blueprint.route("/agregar_atencion/", methods=['GET', 'POST'])
def agregar_atencion():
    diccionario_cliente_mascota = crear_diccionario_cliente_mascota(
        archivo_mascotas)
    diccionario_usuarios = lee_diccionario_csv(
        archivo_usuarios, "nombre_corto")
    if request.method == "GET":
        return render_template("agregar_atencion.html", mensaje="",
                               clientes_mascotas=diccionario_cliente_mascota)
    else:
        if request.method == "POST":
            cliente_mascota = request.form['cliente_mascota']
            try:
                datos = cliente_mascota.split(" -> ")
                nombre_corto_cliente = datos[0]
                nombre_mascota = datos[1]
            except:
                return render_template("agregar_atencion.html", clientes_mascotas=diccionario_cliente_mascota, mensaje="Selecciona un cliente y mascota válidos ('nombre_corto_cliente -> nombre_mascota')")
            # se valida si el usuario existe
            if nombre_corto_cliente not in diccionario_usuarios:
                return render_template("agregar_atencion.html", clientes_mascotas=diccionario_cliente_mascota, mensaje="Ese cliente no existe")
            # se obtienen a las mascotas del cliente
            mascotas_cliente = diccionario_cliente_mascota[nombre_corto_cliente]
            usuario_tiene_esa_mascota = False
            # se recorren las mascotas del cliente para ver si tiene a la mascota especificada en el formulario
            for mascota in mascotas_cliente:
                if mascota['nombre'] == nombre_mascota:
                    usuario_tiene_esa_mascota = True
                    break
            if usuario_tiene_esa_mascota == False:
                return render_template("agregar_atencion.html", clientes_mascotas=diccionario_cliente_mascota, mensaje=f"Ese cliente no tiene una mascota llamada {nombre_mascota}")
            # si los datos son válidos, se continua con lo de abajo
            fecha = request.form['fecha']
            hora = request.form['hora']
            diagnostico = request.form['diagnostico']
            subtotal = request.form['subtotal']
            iva = request.form['iva']
            total = request.form['total']
            # aquí vamos a dejar en formato decimal los 3 datos, por si no lo estaban, o si el subtotal se puso sin decimales
            # también lo ponemos dentro de un try por si por alguna razón, después de las validaciones hechas en el template, en el javascript y aquí,
            # falle algo
            try:
                subtotal = round(float(subtotal), 2)
                iva = round(float(iva), 2)
                total = round(float(total), 2)
            except:
                return render_template("agregar_atencion.html", clientes_mascotas=diccionario_cliente_mascota, mensaje=f"El valor del subtotal es inválido")
            diccionario_atenciones = lee_diccionario_csv(
                archivo_atenciones, "id")
            id = len(diccionario_atenciones)
            diccionario_atenciones[id] = {'id': id, 'cliente': nombre_corto_cliente,
                                          'mascota': nombre_mascota, 'fecha': fecha, 'hora': hora, 'diagnostico': diagnostico, 'subtotal': subtotal, 'iva': iva, 'total': total}
            guardar_diccionario(archivo_atenciones, diccionario_atenciones)
            # se redirecciona a la pagina donde puede generar el PDF o agregar mas atenciones
            return redirect(f"/atencion_agregada_exitosamente/{id}")


@atenciones_blueprint.route("/atencion_agregada_exitosamente/<id_atencion>", methods=['GET'])
def atencion_agregada_exitosamente(id_atencion):
    return render_template("atencion_agregada_exitosamente.html", id_atencion=id_atencion)


# el proposito de esta vista al igual que otras como /receta/id_receta, es generar un HTML listo para generarse en PDF
@atenciones_blueprint.route("/atencion/<id_atencion>")
def atencion(id_atencion):
    diccionario_atenciones = lee_diccionario_csv(
        archivo_atenciones, "id")
    if id_atencion not in diccionario_atenciones:
        return render_template("atencion.html", atencion_existente=False, atencion_a_buscar={})
    atencion_busqueda = diccionario_atenciones[id_atencion]
    return render_template("atencion.html", atencion_existente=True, atencion_a_buscar=atencion_busqueda)


@atenciones_blueprint.route("/tabla_atenciones")
def tabla_atenciones():
    if request.method == 'GET':
        diccionario_usuarios = lee_diccionario_csv(
            archivo_usuarios, "nombre_corto")
        diccionario_atenciones = lee_diccionario_csv(
            archivo_atenciones, "id")
        usuario = diccionario_usuarios[session['usuario']]
        lista = []
        # se obtiene la lista de las atenciones de todos los clientes
        lista_objetos = crear_lista_objetos(
            archivo_atenciones)
        lista_atenciones = []
        # si el usuario es un Cliente, en el JSON solo debemos de mandar las atenciones que son solo de él
        if usuario['tipo'] == "Cliente":
            for atencion in lista_objetos:
                if atencion['cliente'] == usuario['nombre_corto']:
                    lista_atenciones.append(atencion)
        # este podría ser un else directamente, pero por legibilidad, este elif checa si se trata de un Usuario o un Administrador,
        # en ambos casos se van a mostrar todas las atenciones de todos los clientes.
        elif usuario['tipo'] == "Usuario" or usuario['tipo'] == "Administrador":
            lista_atenciones = lista_objetos
        for atencion in lista_atenciones:
            #
            # para evitar problemas de mutabilidad y no alterar la lista de atenciones, se hace una copia de cada atencion.
            atencion_a_guardar = atencion.copy()
            # de igual modo, se le agrega este otro valor que va a ser una de las columnas de la tabla de atenciones, es por esto que no se queria mutar a la lista de atenciones original
            atencion_a_guardar[
                'url_generar_pdf'] = f'<a href="/generar_pdf/atencion/{atencion_a_guardar["id"]}" target="_blank">Generar PDF</a>'
            lista.append(atencion_a_guardar)
        # la lista de atenciones hecha anteriormente, es ordenada por fecha y hora descendente
        lista_ordenada = ordenar_por_fecha_hora_desc(
            lista)
        return jsonify(lista_ordenada)
