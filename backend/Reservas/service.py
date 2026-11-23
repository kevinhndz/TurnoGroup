from sqlalchemy.exc import SQLAlchemyError

from backend.Cajas.repository import CajaRepository
from backend.Reservas.repository import ReservaRepository as repo
from backend.Reservas.tabla import Reservas
from core.operaciones import ahora, alcance, exigir, paginar


class ReservaService:
    @staticmethod
    def respuesta(reserva):
        campos = {}

        for campo_actual in [
            "id",
            "id_mesa",
            "cliente",
            "telefono",
            "personas",
            "inicio",
            "fin",
            "estado",
            "nota",
            "id_usuario",
        ]:
            campos[campo_actual] = getattr(reserva, campo_actual)

        return campos

    @staticmethod
    def guardar_service(json, db, contexto, id=None):
        try:
            empresa, sucursal = alcance(contexto)
            CajaRepository.bloquear_sucursal(db, empresa, sucursal)
            exigir(
                repo.habilitado(db, sucursal),
                "Las reservas no estan habilitadas en esta sucursal",
                403,
            )
            exigir(json.inicio > ahora(), "La reserva debe comenzar en el futuro")
            # El bloqueo de la mesa serializa las reservas del mismo horario.
            mesa = repo.mesa(db, json.id_mesa, sucursal)
            exigir(mesa is not None, "No se encontro la mesa", 404)
            exigir(
                mesa.capacidad is None or json.personas <= mesa.capacidad,
                "La cantidad de personas supera la capacidad de la mesa",
            )
            look_up = repo.buscar(db, id, empresa, sucursal) if id else None

            if id:
                exigir(look_up is not None, "No se encontro la reserva", 404)
                exigir(
                    look_up.estado == "Confirmada",
                    "Esta reserva ya fue atendida o cancelada",
                    409,
                )
            exigir(
                not repo.cruces(db, json.id_mesa, json.inicio, json.fin, id),
                "La mesa ya esta reservada en ese horario",
                409,
            )

            if look_up:
                for campo, valor in json.model_dump().items():
                    setattr(look_up, campo, valor)
            else:
                look_up = Reservas(
                    id_empresa=empresa,
                    id_sucursal=sucursal,
                    id_usuario=contexto["usuario"].id,
                    **json.model_dump(),
                )
                repo.agregar(db, look_up)
            repo.guardar_cambios(db)
            respuesta = ReservaService.respuesta(look_up)
            repo.guardar_cambios(db)
            db.commit()

            return respuesta
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def accion_service(id, estado, db, contexto):
        try:
            empresa, sucursal = alcance(contexto)
            look_up = repo.buscar(db, id, empresa, sucursal)
            exigir(look_up is not None, "No se encontro la reserva", 404)
            exigir(
                look_up.estado == "Confirmada", "La reserva ya no esta confirmada", 409
            )
            look_up.estado = estado
            respuesta = ReservaService.respuesta(look_up)
            repo.guardar_cambios(db)
            db.commit()

            return respuesta
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def listar_service(db, contexto, pagina, limite, estado, filtros=None):
        empresa, sucursal = alcance(contexto)
        exigir(
            repo.habilitado(db, sucursal),
            "Las reservas no estan habilitadas en esta sucursal",
            403,
        )

        return paginar(
            repo.listar(db, empresa, sucursal, estado, filtros),
            pagina,
            limite,
            ReservaService.respuesta,
        )

    @staticmethod
    def ver_service(id, db, contexto):
        empresa, sucursal = alcance(contexto)
        look_up = repo.buscar(db, id, empresa, sucursal)
        exigir(look_up is not None, "No se encontro la reserva", 404)

        return ReservaService.respuesta(look_up)
