from fastapi import FastAPI, APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from core.handlers import ExcepcionesGlobales as eg
from database.almacen import abrir_puerta_bd
from backend.Empresas import router as routerempresas

app = FastAPI()


app.include_router(routerempresas.router)

@app.get("/salud")
def salud(db: Session = Depends(abrir_puerta_bd)):
    db.execute(text("SELECT 1"))
    return {"servicio": "disponible", "base_datos": "conectada"}

eg.directorio(app)
