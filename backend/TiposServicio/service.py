from sqlalchemy.orm import Session
from backend.TiposServicio.repository import TipoServicioRepository as repo
from core.exceptions import RecursoNoEncontradoError


class TipoServicioService():

    @staticmethod
    def listar_tipos_servicio_service(pagina_actual: int, limite: int, db: Session):
        total, lista_tipos_servicio = repo.listar_tipos_servicio(db, pagina_actual, limite)
        total_paginas = (total + limite - 1) // limite
        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": total_paginas,
            "data": lista_tipos_servicio
        }

    @staticmethod
    def ver_tipo_servicio_service(id: int, db: Session):
        look_up = repo.buscar_tipo_servicio_por_id(db, id)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la opcion del sistema")
        return look_up
