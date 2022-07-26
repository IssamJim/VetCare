from flask import Blueprint, redirect, render_template, request, session, jsonify
from Otros import guardar_diccionario, lee_diccionario_csv, ordenar_por_fecha_hora_desc, crear_lista_objetos


informes_blueprint = Blueprint('informes_blueprint', __name__)


archivo_atenciones = "./files/atenciones.csv"
archivo_usuarios = "./files/usuarios.csv"


@informes_blueprint.route("/informe_diario/", methods=['GET', 'POST'])
def informe_diario():
    diccionario_usuarios = lee_diccionario_csv(
        archivo_usuarios, "nombre_corto")
    diccionario_atenciones = lee_diccionario_csv(archivo_atenciones, "id")
    if request.method == "GET":
        return render_template("informe_diario.html", atenciones=diccionario_atenciones)
    else:
        if request.method == "POST":
            # se obtiene el dia que se haya puesto en el formulario
            dia = request.form['fecha']
            lista_ventas, sumatoria = generar_lista_ventas_diarias(
                diccionario_atenciones, dia)
            if len(lista_ventas) == 0:
                return render_template("informe_diario.html", atenciones=diccionario_atenciones, ventas_encontradas=False, dia=dia)
            lista_ventas_ordenadas = ordenar_por_fecha_hora_desc(
                lista_ventas)
            # si se encontraron ventas
            return render_template("informe_diario.html", atenciones=diccionario_atenciones, ventas_encontradas=True, ventas=lista_ventas_ordenadas, mostrar_tabla_busqueda=True, sumatoria=sumatoria, dia=dia)


@informes_blueprint.route("/informe_diario/<dia>")
def informe_diario_dia(dia):
    diccionario_atenciones = lee_diccionario_csv(archivo_atenciones, "id")
    lista_ventas, sumatoria = generar_lista_ventas_diarias(
        diccionario_atenciones, dia)
    if len(lista_ventas) == 0:
        return render_template("informe_diario_dia.html", ventas=lista_ventas, sumatoria=sumatoria, dia=dia, ventas_encontradas=False)
    lista_ventas_ordenadas = ordenar_por_fecha_hora_desc(
        lista_ventas)
    return render_template("informe_diario_dia.html", ventas=lista_ventas_ordenadas, sumatoria=sumatoria, dia=dia, ventas_encontradas=True)


def generar_lista_ventas_diarias(diccionario_atenciones: dict, dia: str):
    """
    Esta función recibe como parámetro un diccionario de atenciones y un dia dado,
    para ese dia dado genera una lista de atenciones/ventas y una sumatoria de los valores
    subtotal, iva y total, los cuales son retornados.
    """
    lista_ventas = []
    suma_subtotales = 0
    suma_ivas = 0
    suma_totales = 0
    # se van agregando las ventas de ese dia
    for id, atencion in diccionario_atenciones.items():
        if atencion['fecha'] == dia:
            lista_ventas.append(atencion)
            # se van acumulando los valores de subtotales, ivas y totales
            suma_subtotales += float(atencion['subtotal'])
            suma_ivas += float(atencion['iva'])
            suma_totales += float(atencion['total'])
    sumatoria = {'suma_subtotales': round(suma_subtotales, 2),
                 'suma_ivas': round(suma_ivas, 2), 'suma_totales': round(suma_totales, 2)}
    return lista_ventas, sumatoria


def generar_lista_ventas_mensuales(diccionario_atenciones: dict, mes: str, anio: str):
    """
    Esta función recibe como parámetro un diccionario de atenciones, un mes y anio dado,
    para ese mes y anio dado genera una lista de atenciones/ventas y una sumatoria de los valores
    subtotal, iva y total, los cuales son retornados.
    """
    lista_ventas = []
    suma_subtotales = 0
    suma_ivas = 0
    suma_totales = 0
    # se van agregando las ventas de ese mes
    for id, atencion in diccionario_atenciones.items():
        fecha = atencion['fecha']
        datos_fecha = fecha.split("-")  # 0 anio - 1 mes - 2 dia
        # mes_dict es el mes que se va obtiendo en cada iteración y es el que se compara con el mes que está como parámetro
        mes_dict = datos_fecha[1]
        anio_dict = datos_fecha[0]
        if mes_dict == mes and anio_dict == anio:
            lista_ventas.append(atencion)
            # se van acumulando los valores de subtotales, ivas y totales
            suma_subtotales += float(atencion['subtotal'])
            suma_ivas += float(atencion['iva'])
            suma_totales += float(atencion['total'])
    sumatoria = {'suma_subtotales': round(suma_subtotales, 2),
                 'suma_ivas': round(suma_ivas, 2), 'suma_totales': round(suma_totales, 2)}
    # se regresa la lista de ventas y las sumatorias de subtotales, ivas y totales
    return lista_ventas, sumatoria


@informes_blueprint.route("/informe_mensual/", methods=['GET', 'POST'])
def informe_mensual():
    diccionario_usuarios = lee_diccionario_csv(
        archivo_usuarios, "nombre_corto")
    diccionario_atenciones = lee_diccionario_csv(archivo_atenciones, "id")
    meses = {'Enero': '01', 'Febrero': '02', 'Marzo': '03', 'Abril': '04', 'Mayo': '05', 'Junio': '06',
             'Julio': '07', 'Agosto': '08', 'Septiembre': '09', 'Octubre': '10', 'Noviembre': '11', 'Diciembre': '12'}
    if request.method == "GET":
        return render_template("informe_mensual.html", atenciones=diccionario_atenciones, meses=meses)
    else:
        if request.method == "POST":
            # se obtiene el mes que se haya puesto en el formulario
            mes = request.form['mes']
            anio = request.form['anio']
            numero_mes = meses[mes]
            lista_ventas, sumatoria = generar_lista_ventas_mensuales(
                diccionario_atenciones, numero_mes, anio)
            if len(lista_ventas) == 0:
                return render_template("informe_mensual.html", atenciones=diccionario_atenciones, ventas_encontradas=False, mes=mes, anio=anio, meses=meses)
            lista_ventas_ordenadas = ordenar_por_fecha_hora_desc(
                lista_ventas)
            # si se encontraron ventas
            return render_template("informe_mensual.html", atenciones=diccionario_atenciones, ventas_encontradas=True, ventas=lista_ventas_ordenadas, mostrar_tabla_busqueda=True, sumatoria=sumatoria, mes=mes, anio=anio, meses=meses)


@informes_blueprint.route("/informe_mensual/<mes_anio>")
def informe_mensual_mes(mes_anio):
    meses = {'Enero': '01', 'Febrero': '02', 'Marzo': '03', 'Abril': '04', 'Mayo': '05', 'Junio': '06',
             'Julio': '07', 'Agosto': '08', 'Septiembre': '09', 'Octubre': '10', 'Noviembre': '11', 'Diciembre': '12'}
    # aquí se separa el mes, del año, porque así formamos la ruta para generar el pdf
    try:
        datos_mes_anio = mes_anio.split("-")
        mes = datos_mes_anio[0]
        anio = datos_mes_anio[1]
    except:
        mes = "No encontrado"
        anio = "No encontrado"
        return render_template("informe_mensual_mes.html", atenciones=diccionario_atenciones, ventas_encontradas=False, mes=mes, anio=anio)
    diccionario_atenciones = lee_diccionario_csv(archivo_atenciones, "id")
    mes_numero = meses[mes]
    lista_ventas, sumatoria = generar_lista_ventas_mensuales(
        diccionario_atenciones, mes_numero, anio)
    if len(lista_ventas) == 0:
        return render_template("informe_mensual_mes.html", atenciones=diccionario_atenciones, ventas_encontradas=False, mes=mes, anio=anio)
    lista_ventas_ordenadas = ordenar_por_fecha_hora_desc(
        lista_ventas)
    return render_template("informe_mensual_mes.html", atenciones=diccionario_atenciones, ventas_encontradas=True, ventas=lista_ventas_ordenadas, sumatoria=sumatoria, mes=mes, anio=anio)
