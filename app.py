from flask import Flask, redirect, render_template, request, session, url_for
from Otros import lee_diccionario_csv
from Login import login_blueprint
from Usuarios import usuarios_blueprint
from Recetas import recetas_blueprint
from Citas import citas_blueprint
from Atencion import atenciones_blueprint
from Historial import historiales_blueprint
from Informes import informes_blueprint
from Menu import crear_menu, validar_ruta_disponible
from flask_weasyprint import render_pdf

app = Flask(__name__)
# esto permite que se pueda rutear a otras partes de la página en distintos archivos .py, para que no
# se encuentre toda la parte del ruteo en un solo archivo
app.register_blueprint(login_blueprint)
app.register_blueprint(usuarios_blueprint)
app.register_blueprint(recetas_blueprint)
app.register_blueprint(citas_blueprint)
app.register_blueprint(atenciones_blueprint)
app.register_blueprint(historiales_blueprint)
app.register_blueprint(informes_blueprint)


# Para utilizar las cookies del session
app.secret_key = "huNos1bzR92pTQ7j"

archivo_usuarios = "./files/usuarios.csv"
# before_request permite ejecutar una función antes de que se cumpla una petición


@app.before_request
def checar_login():
    """
    Esta función se encarga de checar que el usuario esté loggeado para
    poder visitar las distintas páginas del sitio, si no está logeado y no busca
    acceder a la página de login, entonces es redirigido hacia esa página.
    También se va a encargar de validar los permisos de un usuario para acceder a una cierta página, esto es por si el usuario
    no usa el menú directamente y hace la busqueda en la barra de navegación.
    También se va a encargar de crear el menu para todos los tipos de usuarios y guardarlos en session, para que el template
    "base.html" los pueda usar y el menu esté presente en todas las paginas del sitio
    """
    # si el usuario está logeado
    if 'usuario' in session:
        diccionario_usuarios = lee_diccionario_csv(
            "./files/usuarios.csv", "nombre_corto")
        usuario_actual = diccionario_usuarios[session['usuario']]
        menu_usuario = crear_menu(usuario_actual)
        # se agrega este otro valor al diccionario, si el usuario está logeado
        menu_usuario['Cerrar sesión'] = {
            'ruta': "/logout/", 'mostrar_en_menu': True}
    else:
        # si no está logeado, lo unico que verá en el menú es esta opción
        menu_usuario = {'Ingresar': {
            'ruta': "/login/", 'mostrar_en_menu': True}}
    # se guarda el menu en la sesión
    session['menu'] = menu_usuario
    # request.endpoint != 'login_blueprint.login' or request.endpoint != 'index' hace referencia a que si no se
    # quiere acceder a la página de login
    # ruteada por el blueprint que es creado en el modulo Login.py o a la pagina de inicio, pero si a otra página, entonces el usuario tiene que estar logeado,
    # si no es así, es redirigido a la página de login
    paginas_permitidas_sin_login = [
        'login_blueprint.login', 'login_blueprint.registrarse', 'index', 'login_blueprint.recuperar_contrasenia', 'login_blueprint.logout', 'login_blueprint.introducir_codigo_recuperacion', 'static', 'favicon']
    # if 'usuario' not in session and (request.endpoint != 'login_blueprint.login' and request.endpoint != 'index' and request.endpoint != 'login_blueprint.recuperar_contrasenia'):
    # El request.endpoint != 'static' es importante porque el before_request también toma en cuenta las rutas de los recursos en la carpeta /static,
    # por lo que cuando no hay cookies de este sistema en el mnavegador, session['ruta'] = va a tomar el valor de un recurso en static
    # y va a redireccionar a el cuando el usuario se logee, un comportamiento que no es adecuado

    """
    IMPORTANTISIMO:
    Cuando se estaba haciendo lo de generar pdf, este se generaba con la pantalla de login y una parte extrania del index, 
    el error era rarísimo, porque los usuarios podían acceder a la ruta de generar_pdf, lo que provocaba este error era
    que la librería que usamos para generar los PDF, WeasyPrint, aún no tiene funcionalidades como las cookies o la autenticación,
    según su propia página:
    WeasyPrint can read normal files, HTTP, FTP and data URIs.
    It will follow HTTP redirects but more advanced features like cookies and authentication are currently not supported, although a custom URL fetcher can help.
    Entonces cuando se ingresaba a alguna página de genera_pdf, esta no llevaba las cookies con ella, por lo que la cookies que usamos para
    detectar si un usuario está logeado ('usuario'), no se encontraba en session en las páginas de generar_pdf, lo que ocasionaba que el if de
    abajo se cumpliera y redireccionara hasta login y el pdf generado era una cosa extrania.
    Es por eso que se le agrega la validación de checar si el endpoint (funciones de vista) no está entre las paginas de donde se saca el PDF con
    render_pdf()
    """
    # print("path: ", request.path)
    paginas_pdf = ["atenciones_blueprint.atencion",
                   "recetas_blueprint.receta", "informes_blueprint.informe_diario_dia", "informes_blueprint.informe_mensual_mes"]
    if request.endpoint not in paginas_pdf and 'usuario' not in session and request.endpoint not in paginas_permitidas_sin_login:
        # se guarda la vista que el usuario queria ver antes de ser redireccionado al login
        session['ruta'] = request.path
        # print("Endpoint: ", request.endpoint)
        # print("session-ruta: ", session['ruta'])
        # redirige a la función de login, que se encuentra en el blueprint de login en el modulo Login.py
        return redirect(url_for('login_blueprint.login'))
    # Con el if anterior ya validamos que el usuario tiene que estar logeado para acceder a todas las paginas, exceptuando algunas como el index,
    # ahora tenemos que validar que cuando ya esté logeado solo tenga acceso a las paginas que le corresponden.
    # print("endpoint: ", request.endpoint)
    # print("path: ", request.endpoint)
    if 'usuario' in session:
        diccionario_usuarios = lee_diccionario_csv(
            archivo_usuarios, "nombre_corto")
        usuario = diccionario_usuarios[session['usuario']]
        # se obtienen las paginas asociadas a ese tipo de usuario
        paginas_permitidas_usuario = crear_menu(usuario)
        ruta_a_acceder = request.path
        # aqui validamos si el usuario tiene acceso a la ruta a la que quiere entrar, si  no tiene permisos, se redirige al template
        # correspondiente, si está logeado y tiene permisos para acceder a esa ruta, entonces accede sin problemas.
        # De igual modo se checa si el usuario busca acceder a paginas que ya estaban permitidas sin tener que logearse.
        # IMPORTANTE es también validar que la ruta que se esté buscando no sea la de "/no_tienes_permisos", porque si no se crearía
        # una situación circular, que provocaria muchas redirecciones y haría que la aplicación no funcione, esto pasa porque
        # el usuario al tratar de acceder a una pagina a la que no tiene permisos es redireccionado a "/no_tienes_permisos", pero antes
        # de ser redireccionado allí, se ejecuta esta función before_request() y si no se valida lo mencionado anteriormente, entonces
        # estaría siendo redireccionado constantemente a la pagina de "/no_tienes_permisos"
        # también se pone el None, por si la página es un 404 o algún caso extraño como que el endpoint para /logout/ es detectado,
        # pero para /logout, no, posiblemente porque /logout redirecciona hacia /logout/ automaticamente, lo que puede causar algun tipo
        # de fallo en el endpoint
        if request.endpoint not in paginas_permitidas_sin_login and request.endpoint != None and request.path != "/no_tienes_permisos":
            acceso = validar_ruta_disponible(
                ruta_a_acceder, paginas_permitidas_usuario)
            # print("Acceso: ", acceso)
            if acceso == False:
                return redirect("/no_tienes_permisos")


@app.route("/")
@app.route("/index")
@app.route("/index/")
def index():
    # si el usuario está logeado
    if 'usuario' in session:
        diccionario_usuarios = lee_diccionario_csv(
            "./files/usuarios.csv", "nombre_corto")
        usuario_actual = diccionario_usuarios[session['usuario']]
    else:
        # se va a mandar un semidiccionario para el template de index con estos valores si el usuario no está logeado
        usuario_actual = {'tipo': "", 'nombre_corto': "Invitado"}
    return render_template(
        'index.html',  usuario=usuario_actual)


# esta vista va a enlazarse con todas las rutas donde se pueda generar un PDF.
# documento es el tipo como atencion, receta, etc.. e id_documento es la id que se va a usar
# para buscar las atenciones, recetas, etc.. relacionadas en sus respectivos archivos csv
@app.route("/generar_pdf/<documento>/<id_documento>", methods=['GET'])
def generar_pdf(documento, id_documento):
    if documento == "atencion":
        url_base = f"/atencion/{id_documento}"
    elif documento == "receta":
        url_base = f"/receta/{id_documento}"
    elif documento == "informe_diario":
        # id_documento = dia de ventas
        url_base = f"/informe_diario/{id_documento}"
    # documento == "informe_mensual"
    else:
        url_base = f"/informe_mensual/{id_documento}"
    return render_pdf(url_base)


@app.route("/no_tienes_permisos")
def no_tienes_permisos():
    return render_template("no_tienes_permisos.html")


@app.route("/favicon.ico")
def favicon():
    """
    Este ruteo es para evitar un GET con código de error 404 cada que se pida este icono
    """
    # se envia el archivo de icono al navegador
    return app.send_static_file('favicon.ico')


# para tener una página de error 404 personalizada
@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)
