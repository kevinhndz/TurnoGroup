from fastapi import FastAPI, APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from core.handlers import ExcepcionesGlobales as eg
from database.almacen import abrir_puerta_bd
from backend.Empresas import router as routerempresas
from backend.Categorias import router as routercategorias
from backend.Productos import router as routerproductos
from backend.Usuarios import router as routerusuarios
from backend.Sucursales import router as routersucursales
from backend.VinculosLaborales import router as routervinculoslaborales
from backend.Mesas import router as routermesas
from backend.ConfiguracionImpuestos import router as routerimpuestos
from backend.Descuentos import router as routerdescuentos
from backend.CategoriasGastos import router as routercategoriasgastos
from backend.TiposServicio import router as routertiposservicio
from backend.MetodosPago import router as routermetodospago
from backend.ServiciosSucursales import router as routerserviciossucursales
from backend.PagosSucursales import router as routerpagossucursales

from backend.DisponibilidadProductos import router as routerdisponibilidadproductos

from backend.Sesiones import router as routersesiones
from backend.RecuperacionesClave import router as routerrecuperaciones
from backend.InvitacionesLaborales import router as routerinvitaciones
from core.schema import RespuestaError
from utils.autorizacion import autorizar_ruta, obtener_sesion

from backend.Pedidos.router import router as routerpedidos
from backend.Cajas.router import router as routercajas
from backend.Reservas.router import router as routerreservas
from backend.Finanzas.router import router as routerfinanzas
from backend.Suscripciones.router import router as routersuscripciones

app = FastAPI(dependencies=[Depends(autorizar_ruta)], docs_url=None, redoc_url=None, openapi_url=None, responses={
    404: {"model": RespuestaError, "description": "Registro no encontrado"},
    409: {"model": RespuestaError, "description": "Registro duplicado"},
    422: {"model": RespuestaError, "description": "Datos invalidos"},
})


app.include_router(routerpedidos)
app.include_router(routercajas)
app.include_router(routerreservas)
app.include_router(routerfinanzas)
app.include_router(routersuscripciones)
app.include_router(routerinvitaciones.router)
app.include_router(routersesiones.router)
app.include_router(routerrecuperaciones.router)
app.include_router(routerempresas.router)
app.include_router(routercategorias.router)
app.include_router(routerproductos.router)
app.include_router(routerusuarios.router)
app.include_router(routersucursales.router)
app.include_router(routervinculoslaborales.router)
app.include_router(routermesas.router)
app.include_router(routerimpuestos.router)
app.include_router(routerdescuentos.router)
app.include_router(routercategoriasgastos.router)
app.include_router(routertiposservicio.router)
app.include_router(routermetodospago.router)
app.include_router(routerserviciossucursales.router)
app.include_router(routerpagossucursales.router)

app.include_router(routerdisponibilidadproductos.router)

@app.get("/salud")
def salud(db: Session = Depends(abrir_puerta_bd)):
    db.execute(text("SELECT 1"))
    return {"servicio": "disponible", "base_datos": "conectada"}

eg.directorio(app)


@app.get("/openapi.json", include_in_schema=False)
def esquema_privado():
    return app.openapi()


@app.get("/docs", include_in_schema=False)
def documentacion_privada():
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Turno Group")


@app.get("/redoc", include_in_schema=False)
def redoc_privado():
    from fastapi.openapi.docs import get_redoc_html
    return get_redoc_html(openapi_url="/openapi.json", title="Turno Group")
