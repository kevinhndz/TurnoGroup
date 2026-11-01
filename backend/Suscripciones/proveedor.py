from core.config import revision
from core.operaciones import exigir


TARJETAS_PRUEBA = {
    "visa": ("Visa", "4242"),
    "mastercard": ("Mastercard", "4444"),
    "amex": ("American Express", "0005"),
}


def exigir_simulacion():
    # El adaptador de Paddle debe completar checkout y webhooks antes de habilitarse.
    exigir(revision.FACTURACION_MODO == "simulado", "El proveedor de facturacion no esta habilitado", 503)


def datos_tarjeta_prueba(tipo):
    exigir_simulacion()
    return TARJETAS_PRUEBA[tipo]
