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

app = FastAPI()


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

@app.get("/salud")
def salud(db: Session = Depends(abrir_puerta_bd)):
    db.execute(text("SELECT 1"))
    return {"servicio": "disponible", "base_datos": "conectada"}

eg.directorio(app)
