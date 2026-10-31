from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from backend.Finanzas.repository import FinanzasRepository as repo
from backend.Suscripciones.service import SuscripcionService
from core.operaciones import exigir


class FinanzasService:
    @staticmethod
    def resumen_service(db, contexto, desde, hasta, periodo, solo_sucursal):
        empresa = contexto["id_empresa"]
        SuscripcionService.exigir_finanzas(db, empresa)
        exigir(
            hasta >= desde and (hasta - desde).days <= 366,
            "Consulta un periodo de hasta 366 dias",
        )
        negocio = repo.empresa(db, empresa)
        try:
            zona = ZoneInfo(negocio.zona_horaria)
        except ZoneInfoNotFoundError:
            exigir(False, "Configura una zona horaria valida para la empresa")
        inicio = (
            datetime.combine(desde, time.min, zona)
            .astimezone(timezone.utc)
            .replace(tzinfo=None)
        )
        fin = (
            datetime.combine(hasta + timedelta(days=1), time.min, zona)
            .astimezone(timezone.utc)
            .replace(tzinfo=None)
        )
        sucursal = contexto["id_sucursal"] if solo_sucursal else None
        exigir(not solo_sucursal or sucursal, "Selecciona una sucursal", 403)
        filas = repo.ventas(db, empresa, inicio, fin, sucursal)
        grupos = {}
        locales = {}
        for pedido in filas:
            fecha = (
                pedido.fecha_pago.replace(tzinfo=timezone.utc).astimezone(zona).date()
            )
            clave = (
                fecha.isoformat()
                if periodo == "dia"
                else (
                    f"{fecha.isocalendar().year}-S{fecha.isocalendar().week:02d}"
                    if periodo == "semana"
                    else (
                        fecha.strftime("%Y-%m") if periodo == "mes" else str(fecha.year)
                    )
                )
            )
            for tabla, llave in [(grupos, clave), (locales, str(pedido.id_sucursal))]:
                grupo = tabla.setdefault(
                    llave,
                    {
                        "pedidos": 0,
                        "ventas": Decimal("0"),
                        "descuentos": Decimal("0"),
                        "ventas_con_descuento": Decimal("0"),
                        "ventas_sin_descuento": Decimal("0"),
                    },
                )
                grupo["pedidos"] += 1
                grupo["ventas"] += pedido.total
                grupo["descuentos"] += pedido.descuento
                grupo[
                    (
                        "ventas_con_descuento"
                        if pedido.descuento > 0
                        else "ventas_sin_descuento"
                    )
                ] += pedido.total
        convertir = lambda datos: {
            k: str(v) if isinstance(v, Decimal) else v for k, v in datos.items()
        }
        return {
            "desde": desde,
            "hasta": hasta,
            "periodo": periodo,
            "moneda": negocio.codigo_moneda,
            "total_cobrado": str(sum((pedido.total for pedido in filas), Decimal("0"))),
            "pedidos": len(filas),
            "series": [{"periodo": k, **convertir(v)} for k, v in grupos.items()],
            "sucursales": [
                {"id_sucursal": int(k), **convertir(v)} for k, v in locales.items()
            ],
        }
