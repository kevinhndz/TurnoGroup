from fastapi import FastAPI, APIRouter
from core.handlers import ExcepcionesGlobales as eg
from backend.Empresas import router as routerempresas

app = FastAPI()


app.include_router(routerempresas.router)
eg.directorio(app) # Registra los manejadores de tus excepciones de dominio.
