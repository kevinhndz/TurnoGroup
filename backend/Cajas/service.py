from decimal import Decimal
from backend.Cajas.repository import CajaRepository as repo
from backend.Cajas.tabla import Cajas
from core.operaciones import ahora, moneda, exigir, alcance, paginar


class CajaService:
    @staticmethod
    def respuesta(db, caja):
        totales = {
            "efectivo": Decimal("0"),
            "transferencia": Decimal("0"),
            "tarjeta": Decimal("0"),
        }
        pagos = repo.pagos(db, caja.id)
        for pedido, metodo in pagos:
            totales[metodo] += pedido.total
        esperado = moneda(caja.monto_inicial + totales["efectivo"])
        return {
            "id": caja.id,
            "id_usuario": caja.id_usuario,
            "fecha_apertura": caja.fecha_apertura,
            "fecha_cierre": caja.fecha_cierre,
            "monto_inicial": str(caja.monto_inicial),
            "efectivo_esperado": str(
                caja.efectivo_esperado if caja.fecha_cierre else esperado
            ),
            "efectivo_contado": (
                str(caja.efectivo_contado)
                if caja.efectivo_contado is not None
                else None
            ),
            "diferencia": str(caja.diferencia) if caja.diferencia is not None else None,
            "cobros": len(pagos),
            "total_cobrado": str(sum(totales.values())),
            "pagos_por_metodo": {k: str(v) for k, v in totales.items()},
            "nota": caja.nota,
        }

    @staticmethod
    def abrir_service(json, db, contexto):
        empresa, sucursal = alcance(contexto)
        exigir(
            repo.bloquear_sucursal(db, empresa, sucursal),
            "No se encontro la sucursal",
            404,
        )
        exigir(
            repo.buscar_abierta(db, empresa, sucursal) is None,
            "Ya hay una caja abierta en esta sucursal",
            409,
        )
        nueva_caja = Cajas(
            id_empresa=empresa,
            id_sucursal=sucursal,
            id_usuario=contexto["usuario"].id,
            fecha_apertura=ahora(),
            monto_inicial=json.monto_inicial,
        )
        db.add(nueva_caja)
        db.flush()
        respuesta = CajaService.respuesta(db, nueva_caja)
        db.commit()
        return respuesta

    @staticmethod
    def cerrar_service(id, json, db, contexto):
        empresa, sucursal = alcance(contexto)
        look_up = repo.buscar_caja(db, id, empresa, sucursal)
        exigir(look_up is not None, "No se encontro la caja", 404)
        exigir(
            look_up.id_usuario == contexto["usuario"].id,
            "Solo el cajero que abrio la caja puede cerrarla",
            403,
        )
        exigir(look_up.fecha_cierre is None, "La caja ya esta cerrada", 409)
        resumen = CajaService.respuesta(db, look_up)
        look_up.efectivo_esperado = Decimal(resumen["efectivo_esperado"])
        look_up.efectivo_contado = json.efectivo_contado
        look_up.diferencia = moneda(json.efectivo_contado - look_up.efectivo_esperado)
        look_up.nota = json.nota
        look_up.fecha_cierre = ahora()
        respuesta = CajaService.respuesta(db, look_up)
        db.commit()
        return respuesta

    @staticmethod
    def actual_service(db, contexto):
        empresa, sucursal = alcance(contexto)
        look_up = repo.buscar_abierta(db, empresa, sucursal)
        return CajaService.respuesta(db, look_up) if look_up else None

    @staticmethod
    def listar_service(db, contexto, pagina, limite):
        empresa, sucursal = alcance(contexto)
        return paginar(
            repo.listar(db, empresa, sucursal),
            pagina,
            limite,
            lambda fila: CajaService.respuesta(db, fila),
        )
