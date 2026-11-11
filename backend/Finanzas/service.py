from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from backend.Finanzas.repository import FinanzasRepository as repo
from backend.Suscripciones.service import SuscripcionService
from core.operaciones import exigir


class FinanzasService:
    @staticmethod
    def resumen_service(db, contexto, desde, hasta, periodo, solo_sucursal, filas=None):
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
        if filas is None:
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

    @staticmethod
    def dashboard_service(db, contexto, periodo, anio, solo_sucursal, desde=None, hasta=None):
        from collections import defaultdict
        from decimal import ROUND_DOWN
        from datetime import date

        empresa = contexto["id_empresa"]
        exigir(contexto["rol"] == "Gerente" and empresa, "No estas autorizado", 403)
        SuscripcionService.exigir_finanzas(db, empresa)
        negocio = repo.empresa(db, empresa)
        try:
            zona = ZoneInfo(negocio.zona_horaria)
        except ZoneInfoNotFoundError:
            exigir(False, "Configura una zona horaria valida para la empresa")
        hoy = datetime.now(zona).date()
        anio = anio or hoy.year
        rangos = {
            "dia": (hoy, hoy),
            "semana": (hoy - timedelta(days=hoy.weekday()), hoy),
            "mes": (hoy.replace(day=1), hoy),
            "anio": (hoy.replace(month=1, day=1), hoy),
        }
        exigir((desde is None) == (hasta is None), "Indica desde y hasta para un periodo personalizado")
        desde, hasta = (desde, hasta) if desde else rangos[periodo]
        exigir(hasta >= desde and (hasta - desde).days <= 366, "Consulta un periodo de hasta 366 dias")
        def limites(a, b):
            return (datetime.combine(a, time.min, zona).astimezone(timezone.utc).replace(tzinfo=None), datetime.combine(b + timedelta(days=1), time.min, zona).astimezone(timezone.utc).replace(tzinfo=None))
        inicio, fin = limites(desde, hasta)
        sucursal = contexto["id_sucursal"] if solo_sucursal else None
        exigir(not solo_sucursal or sucursal, "Selecciona una sucursal", 403)
        filas = repo.ventas(db, empresa, inicio, fin, sucursal)
        respuesta = FinanzasService.resumen_service(db, contexto, desde, hasta, "dia", solo_sucursal, filas)
        duracion = (hasta - desde).days + 1
        previo_inicio, previo_fin = limites(desde - timedelta(days=duracion), desde - timedelta(days=1))
        previas = repo.ventas(db, empresa, previo_inicio, previo_fin, sucursal)
        anterior = sum((item.total for item in previas), Decimal("0"))
        total = sum((item.total for item in filas), Decimal("0"))
        series = {item["periodo"]: item for item in respuesta["series"]}
        respuesta["series"] = [series.get((desde + timedelta(days=indice)).isoformat(), {"periodo": (desde + timedelta(days=indice)).isoformat(), "pedidos": 0, "ventas": "0.00", "descuentos": "0.00", "ventas_con_descuento": "0.00", "ventas_sin_descuento": "0.00"}) for indice in range(duracion)]
        categorias = defaultdict(lambda: {"ventas": Decimal("0"), "unidades": 0})
        detalles = defaultdict(list)
        for item, categoria in repo.detalles_ventas(db, empresa, inicio, fin, sucursal):
            detalles[item.id_pedido].append((item, categoria or "Sin categoría"))
        for pedido in filas:
            lineas = detalles[pedido.id]
            base = sum((item.precio_unitario * item.cantidad for item, _ in lineas), Decimal("0"))
            exactos = [pedido.total * item.precio_unitario * item.cantidad / base if base else Decimal("0") for item, _ in lineas]
            importes = [valor.quantize(Decimal("0.01"), rounding=ROUND_DOWN) for valor in exactos]
            centavos = int((pedido.total - sum(importes, Decimal("0"))) * 100)
            for indice in sorted(range(len(lineas)), key=lambda i: exactos[i] - importes[i], reverse=True)[:max(0, centavos)]:
                importes[indice] += Decimal("0.01")
            for (item, categoria), importe in zip(lineas, importes):
                categorias[categoria]["ventas"] += importe
                categorias[categoria]["unidades"] += item.cantidad
        horas = {"actual": [0] * 24, "anterior": [0] * 24}
        for clave, pedidos in (("actual", filas), ("anterior", previas)):
            for item in pedidos:
                horas[clave][item.fecha_pago.replace(tzinfo=timezone.utc).astimezone(zona).hour] += 1
        inicio_anio, fin_anio = limites(date(anio, 1, 1), date(anio, 12, 31))
        anual = [Decimal("0")] * 12
        for item in repo.ventas(db, empresa, inicio_anio, fin_anio, sucursal):
            anual[item.fecha_pago.replace(tzinfo=timezone.utc).astimezone(zona).month - 1] += item.total
        locales = {item.id: item for item in repo.sucursales(db, empresa)}
        for item in respuesta["sucursales"]:
            local = locales.get(item["id_sucursal"])
            item["nombre"] = local.nombre if local else "Sucursal"
            item["direccion"] = local.direccion if local else ""
        respuesta.update({
            "actualizado": datetime.now(timezone.utc).isoformat(), "zona_horaria": negocio.zona_horaria,
            "promedio_pedido": str((total / len(filas)).quantize(Decimal("0.01"))) if filas else "0.00",
            "anterior": str(anterior), "variacion": str(((total - anterior) / anterior * 100).quantize(Decimal("0.1"))) if anterior else None,
            "categorias": [{"nombre": nombre, "ventas": str(valor["ventas"]), "unidades": valor["unidades"]} for nombre, valor in sorted(categorias.items(), key=lambda item: item[1]["ventas"], reverse=True)],
            "horas": horas, "anio": anio, "anio_actual": hoy.year,
            "anual": [str(valor) for valor in anual], "total_anual": str(sum(anual, Decimal("0"))),
            "promedio_mensual": str((sum(anual, Decimal("0")) / (hoy.month if anio == hoy.year else 12)).quantize(Decimal("0.01"))),
            "periodos": {clave: str(valor) for clave, valor in repo.totales_periodos(db, empresa, sucursal, {clave: limites(*rango) for clave, rango in rangos.items()}).items()},
        })
        return respuesta
