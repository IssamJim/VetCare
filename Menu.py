

def crear_menu(usuario: dict) -> dict:
    """
    Esta función recibe como parámetro un diccionario con los datos de un usuario y regresa un diccionario
    con las paginas disponibles para este.
    """
    tipo_usuario = usuario['tipo']
    menu_usuario = obtener_paginas_disponibles()
    return menu_usuario[tipo_usuario]


def obtener_paginas_disponibles() -> dict:
    """
    Esta función se encarga de regresar un diccionario con 3 llaves, para los 3 tipos de usuarios,
    donde sus valores son las paginas a las que pueden acceder.
    """
    # las paginas disponibles van a ser representadas por diccionarios que van a tener como llave el nombre
    # de la página y como valor un diccionario, que tendrá 2 llaves, la ruta y una variable booleana que servirá
    # para determinar que páginas van a estar incluidas en el menú y cuales no, esto es para páginas como por
    # ejemplo aquellas donde hay un JSON o páginas que se acceden dentro de alguna página, como por ejemplo
    # Modificar usuarios, que está dentro de la página Usuarios.
    paginas_disponibles_cliente = {'Agendar cita': {'ruta': "/agendar_cita", 'mostrar_en_menu': True},
                                   'Historial de recetas': {'ruta': "/historial_recetas", 'mostrar_en_menu': True},
                                   'Historial de atenciones': {'ruta': "/historial_atenciones", 'mostrar_en_menu': True},
                                   'Tabla citas': {'ruta': "/tabla_citas", 'mostrar_en_menu': False},
                                   'Atención': {'ruta': "/atencion/<id_atencion>", 'mostrar_en_menu': False},
                                   'Tabla recetas': {'ruta': "/tabla_recetas", 'mostrar_en_menu': False},
                                   'Generar PDF': {'ruta': "/generar_pdf/<documento>/<id_documento>", 'mostrar_en_menu': False},
                                   'Tabla atenciones': {'ruta': "/tabla_atenciones", 'mostrar_en_menu': False}}
    paginas_disponibles_usuario = {'Agendar cita': {'ruta': "/agendar_cita", 'mostrar_en_menu': True},
                                   'Historial de recetas': {'ruta': "/historial_recetas", 'mostrar_en_menu': True},
                                   'Historial de atenciones': {'ruta': "/historial_atenciones", 'mostrar_en_menu': True},
                                   'Agregar receta': {'ruta': "/agregar_receta", 'mostrar_en_menu': True},
                                   'Agregar atención': {'ruta': "/agregar_atencion", 'mostrar_en_menu': True},
                                   'Tabla citas': {'ruta': "/tabla_citas", 'mostrar_en_menu': False},
                                   'Modificar citas': {'ruta': "/modificar_cita/<cita>", 'mostrar_en_menu': False},
                                   'Atención agregada exitosamente': {'ruta': "/atencion_agregada_exitosamente/<id_atencion>", 'mostrar_en_menu': False},
                                   'Atención': {'ruta': "/atencion/<id_atencion>", 'mostrar_en_menu': False},
                                   'Receta agregada exitosamente': {'ruta': "/receta_agregada_exitosamente/<id_receta>", 'mostrar_en_menu': False},
                                   'Receta': {'ruta': "/receta/<id_receta>", 'mostrar_en_menu': False},
                                   'Generar PDF': {'ruta': "/generar_pdf/<documento>/<id_documento>", 'mostrar_en_menu': False},
                                   'Tabla recetas': {'ruta': "/tabla_recetas", 'mostrar_en_menu': False},
                                   'Tabla atenciones': {'ruta': "/tabla_atenciones", 'mostrar_en_menu': False}}
    paginas_disponibles_admin = {'Agendar cita': {'ruta': "/agendar_cita", 'mostrar_en_menu': True},
                                 'Historial de recetas': {'ruta': "/historial_recetas", 'mostrar_en_menu': True},
                                 'Historial de atenciones': {'ruta': "/historial_atenciones", 'mostrar_en_menu': True},
                                 'Agregar receta': {'ruta': "/agregar_receta", 'mostrar_en_menu': True},
                                 'Agregar atención': {'ruta': "/agregar_atencion", 'mostrar_en_menu': True},
                                 'Usuarios': {'ruta': "/usuarios", 'mostrar_en_menu': True},
                                 'Medicinas': {'ruta': "/medicinas", 'mostrar_en_menu': True},
                                 'Servicios': {'ruta': "/servicios", 'mostrar_en_menu': True},
                                 'Informe de ventas diarias': {'ruta': "/informe_diario/", 'mostrar_en_menu': True},
                                 'Informe de ventas mensuales': {'ruta': "/informe_mensual/", 'mostrar_en_menu': True},
                                 'Tabla usuarios': {'ruta': "/tabla_usuarios", 'mostrar_en_menu': False},
                                 'Modificar usuarios': {'ruta': "/modificar_usuario/<usuario>", 'mostrar_en_menu': False},
                                 'Agregar usuario': {'ruta': "/agregar_usuario", 'mostrar_en_menu': False},
                                 'Tabla medicinas': {'ruta': "/tabla_medicinas", 'mostrar_en_menu': False},
                                 'Modificar medicinas': {'ruta': "/modificar_medicina/<medicina>", 'mostrar_en_menu': False},
                                 'Agregar medicina': {'ruta': "/agregar_medicina", 'mostrar_en_menu': False},
                                 'Tabla citas': {'ruta': "/tabla_citas", 'mostrar_en_menu': False},
                                 'Modificar citas': {'ruta': "/modificar_cita/<cita>", 'mostrar_en_menu': False},
                                 'Tabla servicios': {'ruta': "/tabla_servicios", 'mostrar_en_menu': False},
                                 'Modificar servicios': {'ruta': "/modificar_servicio/<id_servicio>", 'mostrar_en_menu': False},
                                 'Atención agregada exitosamente': {'ruta': "/atencion_agregada_exitosamente/<id_atencion>", 'mostrar_en_menu': False},
                                 'Atención': {'ruta': "/atencion/<id_atencion>", 'mostrar_en_menu': False},
                                 'Receta agregada exitosamente': {'ruta': "/receta_agregada_exitosamente/<id_receta>", 'mostrar_en_menu': False},
                                 'Receta': {'ruta': "/receta/<id_receta>", 'mostrar_en_menu': False},
                                 'Generar PDF': {'ruta': "/generar_pdf/<documento>/<id_documento>", 'mostrar_en_menu': False},
                                 'Tabla recetas': {'ruta': "/tabla_recetas", 'mostrar_en_menu': False},
                                 'Tabla atenciones': {'ruta': "/tabla_atenciones", 'mostrar_en_menu': False}}

    menu_usuario = {'Cliente': paginas_disponibles_cliente,
                    'Usuario': paginas_disponibles_usuario, 'Administrador': paginas_disponibles_admin}
    return menu_usuario


def validar_ruta_disponible(ruta_a_acceder: str, paginas_disponibles: dict) -> bool:
    """
    Esta función recibe como parámetros la ruta a la que se va a acceder y las paginas a las que un determinado
    tipo de usuario tiene acceso, regresa True si el usuario tiene permisos para acceder a esa ruta, regresa False si no es así.
    """
    # se buscan las rutas disponibles, como el diccionario de paginas disponibles tiene como valores
    # diccionarios con llaves 'ruta' y 'mostrar_en_menu', de las cuales nos interesa 'ruta', por lo que obtenemos
    # esos diccionarios y los pasamos a listas para poder recorrerlos
    rutas_disponibles = list(paginas_disponibles.values())
    # print("Rutas: ", rutas_disponibles)
    for rutas in rutas_disponibles:
        '''
        rutas:
        {'ruta': "/agendar_cita", 'mostrar_en_menu': True},
        {'ruta': "/historial_recetas", 'mostrar_en_menu': True},
        {'ruta': "/historial_atencion", 'mostrar_en_menu': True}}
        rutas['ruta']:
        "/agendar_cita"
        "/historial_recetas"
        "/historial_atencion"
        '''
        # se obtiene cada ruta
        ruta = rutas['ruta']
        # esta validación es para casos especiales de rutas, donde tienen una parte dinámica, como:
        '''
        /agregar_usuario/<usuario>
        /modificar_usuario/<usuario>
        /agregar_medicina/<medicina>
        /modificar_medicina/<medicina>
        '''
        # aquí checamos si se trata de una de esas rutas
        if '<' in ruta:
            # de ser así, separamos esa ruta por el carácter "<"
            ruta = ruta.split("<")
            # ruta = ["/agregar_usuario/", "usuario>"]
            # y solo obtenemos la parte "izquierda" de la ruta
            # ruta = "/agregar_usuario/"
            ruta = ruta[0]
        # ahora checamos si la ruta a la que quiere acceder el usuario contiene a la ruta que se esté recorriendo,
        # no se hace una comparación directa con "==", por las rutas dinámicas:
        '''
        ruta_a_acceder = /agregar_usuario/luis123
        ruta = /agregar_usuario/  (después de aplicarle el proceso de split y tomar la parte izquierda)
        "/agregar_usuario/luis123".__contains__("/agregar_usuario/") == True
        y si la ruta_a_acceder = /usuarios/
        ruta = /usuarios (que es como se guarda en el diccionario de menús)
        "/usuarios/".__contains__("/usuarios") == True
        De modo que nos ahorramos tener que poner rutas con "/" al final (/usuarios/) y sin el (/usuarios) en el diccionario
        de menús, haciendo que 'ruta' : [], que esa llave ahora apunte a una lista de rutas.
        ruta_a_acceder = /medicinas
        ruta = /medicinas
        "/medicinas".__contains__("/medicinas") == True
        '''
        if ruta_a_acceder.__contains__(ruta):
            # print("Acceder a:", ruta_a_acceder, " con ruta: ", ruta)
            return True
    return False
