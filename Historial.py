from flask import Blueprint, redirect, render_template, request, session, jsonify
from Otros import guardar_diccionario, lee_diccionario_csv, ordenar_por_fecha_hora_desc, crear_lista_objetos
from Usuarios import crear_diccionario_cliente_mascota


historiales_blueprint = Blueprint('historiales_blueprint', __name__)

archivo_atenciones = "./files/atenciones.csv"
archivo_mascotas = "./files/mascotas.csv"
archivo_usuarios = "./files/usuarios.csv"
archivo_recetas = "./files/recetas.csv"


@historiales_blueprint.route("/historial_recetas", methods=['GET', 'POST'])
def historial_recetas():
    diccionario_usuarios = lee_diccionario_csv(
        archivo_usuarios, "nombre_corto")
    diccionario_cliente_mascotas = crear_diccionario_cliente_mascota(
        archivo_mascotas)
    diccionario_recetas = lee_diccionario_csv(archivo_recetas, "id")
    if request.method == "GET":
        return render_template("historial_recetas.html", usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascotas, lista_recetas=[], mostrar_tabla_busqueda=False, mensaje="")
    else:
        if request.method == "POST":
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
                return render_template("historial_recetas.html", usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascotas, lista_recetas=[], mostrar_tabla_busqueda=True, mensaje="Selecciona un cliente y mascota válidos ('nombre_corto_cliente -> nombre_mascota')")
            # se valida si el usuario existe
            if nombre_corto_cliente not in diccionario_usuarios:
                return render_template("historial_recetas.html", usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascotas, lista_recetas=[], mostrar_tabla_busqueda=False, mensaje="Ese cliente no existe")
            # se obtienen a las mascotas del cliente
            mascotas_cliente = diccionario_cliente_mascotas[nombre_corto_cliente]
            usuario_tiene_esa_mascota = False
            # se recorren las mascotas del cliente para ver si tiene a la mascota especificada en el formulario
            for mascota in mascotas_cliente:
                if mascota['nombre'] == nombre_mascota:
                    usuario_tiene_esa_mascota = True
                    break
            if usuario_tiene_esa_mascota == False:
                return render_template("historial_recetas.html", usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascotas, lista_recetas=[], mostrar_tabla_busqueda=False, mensaje=f"Ese cliente no tiene una mascota llamada {nombre_mascota}")
            # formamos la lista de recetas para el cliente y mascota seleccionados, la cual vamos a mandar al template para formar otra tabla
            lista_recetas_cliente_mascota = []
            for id, receta in diccionario_recetas.items():
                # checamos que los datos de busqueda de cliente y mascota sean los mismos a los que vamos recorriendo, para agregarlos
                if receta['cliente'] == nombre_corto_cliente and receta['mascota'] == nombre_mascota:
                    lista_recetas_cliente_mascota.append(receta)
            # la lista de recetas hecha anteriormente, es ordenada por fecha y hora descendente
            lista_ordenada = ordenar_por_fecha_hora_desc(
                lista_recetas_cliente_mascota)
            # le mandamos los datos para llenar la tabla con usuario y mascota especificos
            return render_template("historial_recetas.html", usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascotas, lista_recetas=lista_ordenada, mostrar_tabla_busqueda=True, mensaje=f"")


@historiales_blueprint.route("/historial_atenciones", methods=['GET', 'POST'])
def historial_atenciones():
    diccionario_usuarios = lee_diccionario_csv(
        archivo_usuarios, "nombre_corto")
    diccionario_cliente_mascotas = crear_diccionario_cliente_mascota(
        archivo_mascotas)
    diccionario_atenciones = lee_diccionario_csv(archivo_atenciones, "id")
    if request.method == "GET":
        return render_template("historial_atenciones.html", usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascotas, lista_atenciones=[], mostrar_tabla_busqueda=False, mensaje="")
    else:
        if request.method == "POST":
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
                return render_template("historial_atenciones.html", usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascotas, lista_atenciones=[], mostrar_tabla_busqueda=True, mensaje="Selecciona un cliente y mascota válidos ('nombre_corto_cliente -> nombre_mascota')")
            # se valida si el usuario existe
            if nombre_corto_cliente not in diccionario_usuarios:
                return render_template("historial_atenciones.html", usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascotas, lista_atenciones=[], mostrar_tabla_busqueda=False, mensaje="Ese cliente no existe")
            # se obtienen a las mascotas del cliente
            mascotas_cliente = diccionario_cliente_mascotas[nombre_corto_cliente]
            usuario_tiene_esa_mascota = False
            # se recorren las mascotas del cliente para ver si tiene a la mascota especificada en el formulario
            for mascota in mascotas_cliente:
                if mascota['nombre'] == nombre_mascota:
                    usuario_tiene_esa_mascota = True
                    break
            if usuario_tiene_esa_mascota == False:
                return render_template("historial_atenciones.html", usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascotas, lista_atenciones=[], mostrar_tabla_busqueda=False, mensaje=f"Ese cliente no tiene una mascota llamada {nombre_mascota}")
            # formamos la lista de atenciones para el cliente y mascota seleccionados, la cual vamos a mandar al template para formar otra tabla
            lista_atenciones_cliente_mascota = []
            for id, atencion in diccionario_atenciones.items():
                # checamos que los datos de busqueda de cliente y mascota sean los mismos a los que vamos recorriendo, para agregarlos
                if atencion['cliente'] == nombre_corto_cliente and atencion['mascota'] == nombre_mascota:
                    lista_atenciones_cliente_mascota.append(atencion)
            # la lista de atenciones hecha anteriormente, es ordenada por fecha y hora descendente
            lista_ordenada = ordenar_por_fecha_hora_desc(
                lista_atenciones_cliente_mascota)
            # le mandamos los datos para llenar la tabla con usuario y mascota especificos
            return render_template("historial_atenciones.html", usuario=diccionario_usuarios[session['usuario']], clientes_mascotas=diccionario_cliente_mascotas, lista_atenciones=lista_ordenada, mostrar_tabla_busqueda=True, mensaje=f"")
