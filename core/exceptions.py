class DominioError (Exception):

    # Constructor
    def __init__(self, mensaje: str):
        self.mensaje = mensaje



class RecursoNoEncontradoError(DominioError):
    """Representa HTTP 404 - Registro no encontrado."""
    pass


class RecursoDuplicadoError(DominioError):
    """Representa HTTP 409 - Registro duplicado."""
    pass


class CredencialesInvalidasError(DominioError):
    """Representa HTTP 401 - Fallo al autenticarse en el login."""
    pass


class AccesoProhibidoError(DominioError):
    """Representa HTTP 403 - Permisos insuficientes o token expirado/inválido."""
    pass