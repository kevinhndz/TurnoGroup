from fastapi import Depends, Request, HTTPException
from sqlalchemy.orm import Session
from core.config import revision
from database.almacen import abrir_puerta_bd
from backend.Sesiones.service import SesionService

ROLES_EMPRESA = ("Gerente", "Administrador", "Mesero")


RUTAS_CON_PERMISO = {
    ('GET','/pedidos/operaciones/{clave_operacion}'),
    ('GET', '/bitacora/'),
    ('GET', '/pedidos/mesas'),
    ('POST', '/mesas/preparar'),
    ('GET', '/pedidos/catalogo'),
    ('POST', '/invitaciones-laborales/registrar'),
    ('POST', '/productos/importar'),
    ('POST', '/productos/{id}/imagen'),
    ('GET', '/productos/{id}/imagen'),
    ('GET', '/pedidos/'),
    ('POST', '/pedidos/'),
    ('POST', '/pedidos/cotizar'),
    ('GET', '/pedidos/{id}'),
    ('PATCH', '/pedidos/{id}'),
    ('POST', '/pedidos/{id}/cobrar'),
    ('POST', '/pedidos/{id}/entregar'),
    ('POST', '/pedidos/{id}/cancelar'),
    ('GET', '/reservas/'),
    ('POST', '/reservas/'),
    ('GET', '/reservas/{id}'),
    ('PATCH', '/reservas/{id}'),
    ('POST', '/reservas/{id}/atender'),
    ('POST', '/reservas/{id}/cancelar'),
    ('GET', '/cajas/'),
    ('POST', '/cajas/'),
    ('GET', '/cajas/actual'),
    ('POST', '/cajas/{id}/cerrar'),
    ('GET', '/finanzas/ventas'),
    ('GET', '/suscripciones/actual'),
    ('PATCH', '/suscripciones/plan'),
    ('POST', '/usuarios/registro-negocio'),
    ('DELETE', '/disponibilidad-productos/{id_producto}/{id_sucursal}'),
    ('DELETE', '/vinculos-laborales/{id}/sucursales/{id_sucursal}'),
    ('GET', '/categorias-gastos/'),
    ('GET', '/categorias-gastos/{id}'),
    ('GET', '/categorias/'),
    ('GET', '/categorias/{id}'),
    ('GET', '/configuracion-impuestos/'),
    ('GET', '/configuracion-impuestos/{id}'),
    ('GET', '/descuentos/'),
    ('GET', '/descuentos/{id}'),
    ('GET', '/disponibilidad-productos/'),
    ('GET', '/disponibilidad-productos/{id_producto}/{id_sucursal}'),
    ('GET', '/docs'),
    ('GET', '/empresas/'),
    ('GET', '/empresas/{id}'),
    ('GET', '/invitaciones-laborales/'),
    ('GET', '/invitaciones-laborales/{id}'),
    ('GET', '/mesas/'),
    ('GET', '/mesas/{id}'),
    ('GET', '/metodos-pago/'),
    ('GET', '/metodos-pago/{id}'),
    ('GET', '/openapi.json'),
    ('GET', '/pagos-sucursales/'),
    ('GET', '/pagos-sucursales/{id_sucursal}/{id_metodo_pago}'),
    ('GET', '/productos/'),
    ('GET', '/productos/{id}'),
    ('GET', '/redoc'),
    ('GET', '/salud'),
    ('GET', '/servicios-sucursales/'),
    ('GET', '/servicios-sucursales/{id_sucursal}/{id_tipo_servicio}'),
    ('GET', '/sesiones/actual'),
    ('GET', '/sesiones/vinculos'),
    ('GET', '/sucursales/'),
    ('GET', '/sucursales/{id}'),
    ('GET', '/tipos-servicio/'),
    ('GET', '/tipos-servicio/{id}'),
    ('GET', '/usuarios/'),
    ('GET', '/usuarios/{id}'),
    ('GET', '/vinculos-laborales/'),
    ('GET', '/vinculos-laborales/{id}'),
    ('GET', '/vinculos-laborales/{id}/sucursales'),
    ('PATCH', '/categorias-gastos/{id}'),
    ('PATCH', '/categorias/{id}'),
    ('PATCH', '/configuracion-impuestos/{id}'),
    ('PATCH', '/descuentos/{id}'),
    ('PATCH', '/disponibilidad-productos/{id_producto}/{id_sucursal}'),
    ('PATCH', '/empresas/{id}'),
    ('PATCH', '/mesas/{id}'),
    ('PATCH', '/pagos-sucursales/{id_sucursal}/{id_metodo_pago}'),
    ('PATCH', '/productos/{id}'),
    ('PATCH', '/servicios-sucursales/{id_sucursal}/{id_tipo_servicio}'),
    ('PATCH', '/sesiones/contexto'),
    ('PATCH', '/sucursales/{id}'),
    ('PATCH', '/usuarios/{id}'),
    ('PATCH', '/usuarios/{id}/rol-plataforma'),
    ('PATCH', '/vinculos-laborales/{id}'),
    ('POST', '/categorias-gastos/'),
    ('POST', '/categorias-gastos/{id}/desactivar'),
    ('POST', '/categorias/'),
    ('POST', '/categorias/{id}/desactivar'),
    ('POST', '/configuracion-impuestos/'),
    ('POST', '/configuracion-impuestos/{id}/desactivar'),
    ('POST', '/descuentos/'),
    ('POST', '/descuentos/{id}/desactivar'),
    ('POST', '/disponibilidad-productos/'),
    ('POST', '/empresas/'),
    ('POST', '/empresas/{id}/desactivar'),
    ('POST', '/invitaciones-laborales/'),
    ('POST', '/invitaciones-laborales/aceptar'),
    ('POST', '/invitaciones-laborales/{id}/revocar'),
    ('POST', '/mesas/'),
    ('POST', '/mesas/{id}/desactivar'),
    ('POST', '/pagos-sucursales/'),
    ('POST', '/pagos-sucursales/{id_sucursal}/{id_metodo_pago}/desactivar'),
    ('POST', '/productos/'),
    ('POST', '/productos/{id}/desactivar'),
    ('POST', '/recuperaciones-clave/restablecer'),
    ('POST', '/recuperaciones-clave/solicitar'),
    ('POST', '/servicios-sucursales/'),
    ('POST', '/servicios-sucursales/{id_sucursal}/{id_tipo_servicio}/desactivar'),
    ('POST', '/sesiones/cerrar'),
    ('POST', '/sesiones/iniciar'),
    ('POST', '/sesiones/renovar'),
    ('POST', '/sesiones/revocar-todas'),
    ('POST', '/sucursales/'),
    ('POST', '/sucursales/{id}/desactivar'),
    ('POST', '/usuarios/'),
    ('POST', '/usuarios/{id}/desactivar'),
    ('POST', '/vinculos-laborales/'),
    ('POST', '/vinculos-laborales/{id}/sucursales'),
}


def revisar_solicitud_sesion(request: Request):
    if revision.COOKIE_SEGURA and request.url.scheme != "https":
        raise HTTPException(400, "Esta operacion requiere HTTPS")
    origen = request.headers.get("origin")
    if origen and origen not in revision.ORIGENES_PERMITIDOS:
        raise HTTPException(403, "Origen no permitido")
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        if request.headers.get("X-Solicitud") != "TurnoGroup":
            raise HTTPException(403, "Falta el encabezado X-Solicitud")


def obtener_sesion(request: Request, db: Session = Depends(abrir_puerta_bd)):
    revisar_solicitud_sesion(request)
    if not hasattr(request.state, "sesion_validada"):
        request.state.sesion_validada = SesionService.consultar_sesion_service(request.cookies.get("sesion_turnogroup"), db)
    sesion,usuario=request.state.sesion_validada
    if usuario.rol_plataforma=='Superadministrador':
        db.info['actor_bitacora']={'empresa':None,'sucursal':None,'usuario':usuario.id,'plataforma':True}
    return request.state.sesion_validada


def obtener_contexto(request: Request, db: Session = Depends(abrir_puerta_bd)):
    if hasattr(request.state, "contexto"):
        return request.state.contexto
    sesion, usuario = obtener_sesion(request, db)
    contexto = SesionService.obtener_contexto_service(sesion, usuario, db)
    db.info['actor_bitacora'] = {'empresa':contexto['id_empresa'],'sucursal':contexto['id_sucursal'],'usuario':usuario.id,'plataforma':usuario.rol_plataforma=='Superadministrador'}
    request.state.contexto = contexto
    return contexto


def obtener_empresa(contexto: dict = Depends(obtener_contexto)) -> int:
    if contexto["id_empresa"] is None or contexto["rol_plataforma"] == "Superadministrador":
        raise HTTPException(403, "Selecciona un vinculo autorizado")
    return contexto["id_empresa"]


def obtener_sucursal(contexto: dict = Depends(obtener_contexto)) -> int:
    if contexto["id_sucursal"] is None:
        raise HTTPException(403, "Selecciona una sucursal autorizada")
    return contexto["id_sucursal"]


def obtener_sucursal_catalogo(contexto: dict = Depends(obtener_contexto)):
    if contexto["rol"] == "Gerente":
        return None
    return obtener_sucursal(contexto)


def el_vigilante(contexto: dict = Depends(obtener_contexto)) -> dict:
    return contexto


def permiso_admin(json: dict = Depends(el_vigilante)) -> dict:
    if json["rol"] not in ("Gerente", "Administrador"):
        raise HTTPException(403, "No estas autorizado")
    return json


def permiso_usuario(json: dict = Depends(el_vigilante)) -> dict:
    if json["rol"] not in ROLES_EMPRESA:
        raise HTTPException(403, "No estas autorizado")
    return json


def autorizar_ruta(request: Request, db: Session = Depends(abrir_puerta_bd)):
    ruta = request.scope["route"].path
    metodo = request.method
    if (metodo, ruta) not in RUTAS_CON_PERMISO:
        obtener_sesion(request, db)
        raise HTTPException(403, "Esta ruta no tiene permisos definidos")
    if ruta == "/salud" and metodo == "GET":
        return
    if (ruta, metodo) in {
        ("/sesiones/iniciar", "POST"), ("/invitaciones-laborales/registrar", "POST"), ("/recuperaciones-clave/solicitar", "POST"),
        ("/recuperaciones-clave/restablecer", "POST")
    }:
        revisar_solicitud_sesion(request)
        return
    if ruta == "/usuarios/registro-negocio" and metodo == "POST" and revision.ALTA_PUBLICA_HABILITADA:
        revisar_solicitud_sesion(request)
        return

    sesion, usuario = obtener_sesion(request, db)
    superadministrador = usuario.rol_plataforma == "Superadministrador"
    if ruta.startswith("/sesiones/") or ruta in ("/docs", "/redoc", "/openapi.json"):
        return
    if ruta.startswith("/usuarios"):
        id_usuario = request.path_params.get("id")
        if ruta.endswith("/rol-plataforma") and not superadministrador:
            raise HTTPException(403, "No estas autorizado")
        if superadministrador or str(id_usuario) == str(usuario.id):
            return
        raise HTTPException(403, "No estas autorizado")
    if ruta == "/invitaciones-laborales/aceptar" and not superadministrador:
        return
    if superadministrador and ruta == '/bitacora/' and metodo == 'GET':
        return
    if superadministrador:
        if ruta.startswith("/empresas") or ruta.startswith(("/tipos-servicio/", "/metodos-pago/")):
            return
        if ruta == "/vinculos-laborales/" and metodo == "POST":
            return
        raise HTTPException(403, "La plataforma no opera empresas de clientes")

    contexto = obtener_contexto(request, db)
    rol = contexto["rol"]
    empresa = contexto["id_empresa"]
    if ruta == "/empresas/" and metodo == "POST":
        if rol in (None, "Gerente"):
            return
        raise HTTPException(403, "No estas autorizado")
    if empresa is None:
        raise HTTPException(403, "Selecciona un vinculo autorizado")
    if "id_empresa" in request.query_params and request.query_params["id_empresa"] != str(empresa):
        raise HTTPException(403, "La empresa solicitada no esta autorizada")

    if "id_sucursal" in request.query_params and request.query_params["id_sucursal"] != str(contexto["id_sucursal"]):
        raise HTTPException(404, "No se encontro el recurso")

    modulo = ruta.split("/")[1]
    if empresa is not None and modulo != "suscripciones":
        from backend.Suscripciones.repository import SuscripcionRepository
        from backend.Suscripciones.service import SuscripcionService
        suscripcion = SuscripcionRepository.buscar_suscripcion(db, empresa)
        if not SuscripcionService.vigente(suscripcion):
            raise HTTPException(403, "La suscripcion no esta vigente. El gerente debe revisar la facturacion")

    if modulo == 'bitacora' and rol in ROLES_EMPRESA:
        return
    if modulo in ("pedidos", "reservas"):
        obtener_sucursal(contexto)
        if rol in ROLES_EMPRESA:
            return
    elif modulo == "cajas":
        obtener_sucursal(contexto)
        if rol in ROLES_EMPRESA:
            return
    elif modulo in ("finanzas", "suscripciones"):
        if rol == "Gerente":
            return
    elif modulo == "empresas":
        if "id" in request.path_params and str(request.path_params["id"]) != str(empresa):
            raise HTTPException(404, "No se encontro la empresa")
        if metodo == "GET" or rol == "Gerente":
            return
    elif modulo in ("invitaciones-laborales", "vinculos-laborales", "configuracion-impuestos", "categorias-gastos"):
        if rol == "Gerente" and not (modulo == "vinculos-laborales" and metodo == "POST" and ruta == "/vinculos-laborales/"):
            return
    elif modulo in ("categorias", "productos", "descuentos"):
        if metodo == "GET" or rol == "Gerente":
            return
    elif modulo in ("tipos-servicio", "metodos-pago"):
        if metodo == "GET":
            return
    elif modulo == "sucursales":
        if metodo != "GET" and rol != "Gerente":
            raise HTTPException(403, "No estas autorizado")
        if rol != "Gerente" and "id" in request.path_params and str(request.path_params["id"]) != str(contexto["id_sucursal"]):
            raise HTTPException(404, "No se encontro la sucursal")
        return
    elif modulo in ("mesas", "servicios-sucursales", "pagos-sucursales", "disponibilidad-productos"):
        if metodo != "GET" and rol != "Gerente" and not (modulo == "disponibilidad-productos" and rol == "Administrador" and metodo == "PATCH"):
            raise HTTPException(403, "No estas autorizado")
        sucursal = obtener_sucursal(contexto)
        solicitado = request.path_params.get("id_sucursal", request.query_params.get("id_sucursal"))
        if solicitado is not None and str(solicitado) != str(sucursal):
            raise HTTPException(404, "No se encontro el recurso")
        return
    raise HTTPException(403, "No estas autorizado")
