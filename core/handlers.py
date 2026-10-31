from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError, IntegrityError
from fastapi.exceptions import RequestValidationError
from core.exceptions import (
    RecursoNoEncontradoError, 
    RecursoDuplicadoError,
    CredencialesInvalidasError,
    AccesoProhibidoError,

)


class ExcepcionesGlobales:

    @staticmethod
    def base_datos_no_disponible(request: Request, exc: OperationalError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "No se puede acceder a la base de datos"}
        )

    @staticmethod
    def recurso_no_encontrado(request: Request, exc: RecursoNoEncontradoError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.mensaje}
        )

    @staticmethod
    def recurso_duplicado(request: Request, exc: RecursoDuplicadoError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": exc.mensaje}
        )

    @staticmethod
    def credenciales_invalidas(request: Request, exc: CredencialesInvalidasError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": exc.mensaje}
        )

    @staticmethod
    def acceso_prohibido(request: Request, exc: AccesoProhibidoError):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": exc.mensaje}
        )



    @staticmethod
    def datos_invalidos(request: Request, exc: RequestValidationError):
        errores = []
        for error in exc.errors():
            mensaje = "Valor no valido para este campo"
            if error["type"] == "missing":
                mensaje = "Campo requerido"
            if error["type"] == "extra_forbidden":
                mensaje = "Campo no permitido"
            errores.append({
                "campo": ".".join(str(parte) for parte in error["loc"]),
                "mensaje": mensaje
            })
        return JSONResponse(status_code=422, content={
            "detail": "Los datos enviados no son validos", "errores": errores
        })

    @staticmethod
    def restriccion_base_datos(request: Request, exc: IntegrityError):
        codigo = getattr(exc.orig, "sqlstate", None)
        nombre = getattr(exc.orig, "sqlite_errorname", "")
        if codigo == "23505" or nombre in ("SQLITE_CONSTRAINT_UNIQUE", "SQLITE_CONSTRAINT_PRIMARYKEY"):
            return JSONResponse(status_code=409, content={"detail": "Ya existe un registro con esos datos"})
        if codigo in ("23502", "23503", "23514") or nombre in (
            "SQLITE_CONSTRAINT_NOTNULL", "SQLITE_CONSTRAINT_FOREIGNKEY", "SQLITE_CONSTRAINT_CHECK"
        ):
            return JSONResponse(status_code=422, content={"detail": "Los datos enviados no son validos"})
        return JSONResponse(status_code=500, content={"detail": "No se pudo guardar el registro"})

    @classmethod
    def directorio(cls, app: FastAPI) -> None:
        app.add_exception_handler(OperationalError, cls.base_datos_no_disponible)
        app.add_exception_handler(RequestValidationError, cls.datos_invalidos)
        app.add_exception_handler(IntegrityError, cls.restriccion_base_datos)
        app.add_exception_handler(RecursoNoEncontradoError, cls.recurso_no_encontrado)
        app.add_exception_handler(RecursoDuplicadoError, cls.recurso_duplicado)
        app.add_exception_handler(CredencialesInvalidasError, cls.credenciales_invalidas)
        app.add_exception_handler(AccesoProhibidoError, cls.acceso_prohibido)
      
        
        """
        
# FLUJO DE EXCEPCIONES:
# 1. En service ocurre un error y se hace raise de una excepcion (ej. RecursoNoEncontradoError).
#  2. Se instancia la clase y su mensaje se guarda en el atributo 'mensaje'.
# 3. El raise interrumpe el flujo normal y FastAPI lo intercepta en pleno vuelo.
# 4. FastAPI revisa su directorio (registrado en app con add_exception_handler) 
#   5.  y busca en ExcepcionesGlobales la funcion asociada a ese error.
# 6. Se ejecuta la funcion estatica correspondiente, la cual empaqueta 
#   7. el atributo 'mensaje' dentro de un JSONResponse con su codigo HTTP y lo devuelve al cliente.
    
        """
