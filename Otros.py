import csv
import datetime


def lee_diccionario_csv(archivo: str, llave_parametro: str) -> dict:
    '''Se pasa como parametro un archivo CSV y una llave que puede ser:
    "nombre_corto", "nombre", "email" u alguna otra, lee el archivo CSV y 
    regresa un diccionario donde las llaves son los valores del CSV determinados 
    por la llave que se dió como parametro y los valores son los datos de las demás columnas
    '''
    diccionario = {}
    try:
        # el encoding tuvo que ser cambiado a latin-1, porque algunos valores que se guardaban podían contener acentos o algunos
        # otros carácteres que UTF-8 no asimilaba bien y producía errores al tratar de mostrar por ejemplo el listado de medicinas.
        with open(archivo, 'r', encoding='latin-1') as fh:
            csv_reader = csv.DictReader(fh)
            for renglon in csv_reader:
                llave = renglon[llave_parametro]
                diccionario[llave] = renglon
    except IOError:
        print(f"No se pudo leer el archivo {archivo}")
    return diccionario


def obten_campos(diccionario: dict) -> list:
    """
    Genera el encabezado para el archivo CSV, mediante un diccionario
    """
    lista = []
    llaves = list(diccionario.keys())
    k = llaves[0]
    nuevo_diccionario = diccionario[k]
    lista_campos = list(nuevo_diccionario.keys())
    lista.extend(lista_campos)
    return lista


def guardar_diccionario(archivo: str, diccionario: dict) -> None:
    """
    Guarda un diccionario en un archivo .CSV como la lista de usuarios
    """
    with open(archivo, 'w') as fh:
        # se obtienen los campos del encabezado
        lista_campos = obten_campos(diccionario)
        dw = csv.DictWriter(fh, lista_campos)
        # se escribe el encabezado
        dw.writeheader()
        # estos renglones son los usuarios
        renglones = []
        for llave, valor_d in diccionario.items():
            # este diccionario va a contener todos los datos de un usuario
            d = {}
            for key, value in valor_d.items():
                d[key] = value
            renglones.append(d)
        # se guardan todos los usuarios
        dw.writerows(renglones)


def crear_lista_objetos(archivo: str) -> list:
    """
    Esta función es muy parecida a la de lee_diccionario_csv(), sin embargo su diferencia radica en que mientrás que lee_diccionario_csv()
    regresa un diccionario de diccionarios que tienen llaves y como valores otros diccionarios, esta función regresa un diccionario
    donde no hay 'llaves primarias' como por ejemplo un diccionario de mascotas, donde no hay un identificador exclusivo.
    '"""
    lista_objetos = []
    try:
        with open(archivo, 'r', encoding='latin-1') as fh:
            csv_reader = csv.DictReader(fh)
            for objeto in csv_reader:
                lista_objetos.append(objeto)
    except IOError:
        print(f"No se pudo leer el archivo {archivo}")
    return lista_objetos


def guardar_lista_objetos(archivo: str, lista_objetos: list) -> None:
    """
    Parecida a guardar_diccionario(), al igual que con la función crear_lista_objetos(), en lugar de guardar un diccionario
    que tiene 'llaves primarias', este va a guardar a aquellos que no las tengan como el diccionario de mascotas.
    """
    with open(archivo, 'w') as fh:
        # se obtienen los campos del encabezado
        primer_diccionario = lista_objetos[0]
        lista_campos = list(primer_diccionario.keys())
        dw = csv.DictWriter(fh, lista_campos)
        # se escribe el encabezado
        dw.writeheader()
        # estos renglones son
        renglones = []
        for objeto in lista_objetos:
            # este diccionario va a contener todos los datos de
            d = {}
            for key, value in objeto.items():
                d[key] = value
            renglones.append(d)
        # se guardan todos los
        dw.writerows(renglones)


def ordenar_por_fecha_hora_desc(lista: list) -> list:
    """
    Esta funcín recibe como parametro una lista de diccionarios, ya sea una lista de atenciones, recetas... (pero que tengan las llaves
    'fecha' y 'hora') y ordena esa lista por fecha y hora descendente mediante un ordenamiento de burbuja, regresa una lista ordenada
    """
    # doble for para el ordenamiento burbuja
    for i in range(1, len(lista)):
        for j in range(0, len(lista) - i):
            # se van a comparar la fecha que está a la "izquierda" o una posición antes del valor que le sigue al que se va a comparar
            fecha_izquierda = lista[j]['fecha']
            hora_izquierda = lista[j]['hora']
            # se convierte la fecha a datetime.datetime para poder hacer comparaciones
            fecha_convertida_izquierda = convertir_a_fecha_hora(
                fecha_izquierda, hora_izquierda)
            fecha_derecha = lista[j + 1]['fecha']
            hora_derecha = lista[j + 1]['hora']
            fecha_convertida_derecha = convertir_a_fecha_hora(
                fecha_derecha, hora_derecha)
            # si la fecha que está ordenada antes que la fecha que le sigue es mayor (ocurre después), entonces se cambian posiciones
            if fecha_convertida_izquierda > fecha_convertida_derecha:
                temp = lista[j]
                lista[j] = lista[j + 1]
                lista[j + 1] = temp
    return lista


def convertir_a_fecha_hora(fecha_str: str, hora_str: str) -> datetime.datetime:
    """
    Esta función recibe como parámetro una fecha y una hora en formato string y une ambos datos
    en un objeto datetime.datetime, el cual regresa.
    """
    datos_hora = hora_str.split(":")  # 0 hora : 1 minuto
    datos_fecha = fecha_str.split(
        "-")  # 0 anio - 1 mes - 2 dia
    datos_fecha = [int(elemento)
                   for elemento in datos_fecha]
    datos_hora = [int(elemento)
                  for elemento in datos_hora]
    fecha_convertida = datetime.datetime(
        year=datos_fecha[0], month=datos_fecha[1], day=datos_fecha[2], hour=datos_hora[0], minute=datos_hora[1])
    return fecha_convertida
