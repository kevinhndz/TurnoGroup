from sqlalchemy.orm import Session
from backend.MetodosPago.repository import MetodoPagoRepository as repo
from core.exceptions import RecursoNoEncontradoError


class MetodoPagoService():

    @staticmethod
    def listar_metodos_pago_service(pagina_actual: int, limite: int, db: Session):
        total, lista_metodos_pago = repo.listar_metodos_pago(db, pagina_actual, limite)
        total_paginas = (total + limite - 1) // limite
        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": total_paginas,
            "data": lista_metodos_pago
        }

    @staticmethod
    def ver_metodo_pago_service(id: int, db: Session):
        look_up = repo.buscar_metodo_pago_por_id(db, id)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la opcion del sistema")
        return look_up
