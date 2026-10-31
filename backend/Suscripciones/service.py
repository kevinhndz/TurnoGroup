from backend.Suscripciones.repository import SuscripcionRepository as repo
from core.operaciones import ahora, exigir


class SuscripcionService:
    @staticmethod
    def vigente(suscripcion):
        return bool(
            suscripcion
            and (
                (suscripcion.estado == "Prueba" and suscripcion.fin_prueba > ahora())
                or (
                    suscripcion.estado == "Activa"
                    and suscripcion.proximo_cobro
                    and suscripcion.proximo_cobro > ahora()
                )
            )
        )

    @staticmethod
    def consultar_service(db, id_empresa):
        look_up = repo.buscar_suscripcion(db, id_empresa)
        exigir(look_up is not None, "No se encontro la suscripcion", 404)
        locales = repo.contar_sucursales(db, id_empresa)
        return {
            "id": look_up.id,
            "estado": (
                look_up.estado if SuscripcionService.vigente(look_up) else "Vencida"
            ),
            "inicio_prueba": look_up.inicio_prueba,
            "fin_prueba": look_up.fin_prueba,
            "proximo_cobro": look_up.proximo_cobro,
            "finanzas_habilitadas": look_up.finanzas_habilitadas,
            "sucursales_activas": locales,
            "precio_por_sucursal_usd": "100.00",
            "complemento_finanzas_usd": (
                "30.00" if look_up.finanzas_habilitadas else "0.00"
            ),
            "total_mensual_usd": str(
                locales * 100 + (30 if look_up.finanzas_habilitadas else 0)
            ),
            "proveedor": "Paddle",
            "integracion_pendiente": True,
        }

    @staticmethod
    def cambiar_plan_service(json, db, id_empresa):
        look_up = repo.buscar_suscripcion(db, id_empresa, True)
        exigir(look_up is not None, "No se encontro la suscripcion", 404)
        exigir(
            look_up.estado == "Prueba" and look_up.fin_prueba > ahora(),
            "Los cambios de un plan de pago requieren la integracion de Paddle",
            409,
        )
        look_up.finanzas_habilitadas = json.finanzas_habilitadas
        db.commit()
        return SuscripcionService.consultar_service(db, id_empresa)

    @staticmethod
    def exigir_finanzas(db, id_empresa):
        look_up = repo.buscar_suscripcion(db, id_empresa)
        exigir(
            SuscripcionService.vigente(look_up) and look_up.finanzas_habilitadas,
            "El modulo Finanzas no esta habilitado en tu plan",
            403,
        )
