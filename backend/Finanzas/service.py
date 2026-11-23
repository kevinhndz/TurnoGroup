from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from decimal import ROUND_DOWN, Decimal
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

        def convertir(datos):
            campos = {}

            for k_actual, v_actual in datos.items():
                campos[k_actual] = (
                    str(v_actual) if isinstance(v_actual, Decimal) else v_actual
                )

            return campos

        elementos_4 = []

        for k_actual_2, v_actual_2 in grupos.items():
            elementos_4.append({"periodo": k_actual_2, **convertir(v_actual_2)})
        elementos_5 = []

        for k_actual_3, v_actual_3 in locales.items():
            elementos_5.append(
                {"id_sucursal": int(k_actual_3), **convertir(v_actual_3)}
            )
        total_calculado = Decimal("0")

        for pedido_actual in filas:
            total_calculado += pedido_actual.total

        return {
            "desde": desde,
            "hasta": hasta,
            "periodo": periodo,
            "moneda": negocio.codigo_moneda,
            "total_cobrado": str(total_calculado),
            "pedidos": len(filas),
            "series": elementos_4,
            "sucursales": elementos_5,
        }

    @staticmethod
    def dashboard_service(
        db, contexto, periodo, anio, solo_sucursal, desde=None, hasta=None
    ):
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
        exigir(
            (desde is None) == (hasta is None),
            "Indica desde y hasta para un periodo personalizado",
        )
        desde, hasta = (desde, hasta) if desde else rangos[periodo]
        exigir(
            hasta >= desde and (hasta - desde).days <= 366,
            "Consulta un periodo de hasta 366 dias",
        )

        def limites(a, b):
            return (
                datetime.combine(a, time.min, zona)
                .astimezone(timezone.utc)
                .replace(tzinfo=None),
                datetime.combine(b + timedelta(days=1), time.min, zona)
                .astimezone(timezone.utc)
                .replace(tzinfo=None),
            )

        inicio, fin = limites(desde, hasta)
        sucursal = contexto["id_sucursal"] if solo_sucursal else None
        exigir(not solo_sucursal or sucursal, "Selecciona una sucursal", 403)
        filas = repo.ventas(db, empresa, inicio, fin, sucursal)
        respuesta = FinanzasService.resumen_service(
            db, contexto, desde, hasta, "dia", solo_sucursal, filas
        )
        duracion = (hasta - desde).days + 1
        previo_inicio, previo_fin = limites(
            desde - timedelta(days=duracion), desde - timedelta(days=1)
        )
        previas = repo.ventas(db, empresa, previo_inicio, previo_fin, sucursal)
        total_calculado_2 = Decimal("0")

        for item_actual in previas:
            total_calculado_2 += item_actual.total
        anterior = total_calculado_2
        total_calculado_3 = Decimal("0")

        for item_actual_2 in filas:
            total_calculado_3 += item_actual_2.total
        total = total_calculado_3
        campos_2 = {}

        for item_actual_4 in respuesta["series"]:
            campos_2[item_actual_4["periodo"]] = item_actual_4
        series = campos_2
        elementos = []

        for indice_actual in range(duracion):
            elementos.append(
                series.get(
                    (desde + timedelta(days=indice_actual)).isoformat(),
                    {
                        "periodo": (desde + timedelta(days=indice_actual)).isoformat(),
                        "pedidos": 0,
                        "ventas": "0.00",
                        "descuentos": "0.00",
                        "ventas_con_descuento": "0.00",
                        "ventas_sin_descuento": "0.00",
                    },
                )
            )
        respuesta["series"] = elementos
        categorias = defaultdict(lambda: {"ventas": Decimal("0"), "unidades": 0})
        detalles = defaultdict(list)

        for item, categoria in repo.detalles_ventas(db, empresa, inicio, fin, sucursal):
            detalles[item.id_pedido].append((item, categoria or "Sin categoría"))

        for pedido in filas:
            lineas = detalles[pedido.id]
            total_calculado_4 = Decimal("0")

            for item_actual_3, __actual in lineas:
                total_calculado_4 += (
                    item_actual_3.precio_unitario * item_actual_3.cantidad
                )
            base = total_calculado_4
            exactos = []

            for item_actual_5, __actual_2 in lineas:
                exactos.append(
                    pedido.total
                    * item_actual_5.precio_unitario
                    * item_actual_5.cantidad
                    / base
                    if base
                    else Decimal("0")
                )
            importes = []

            for valor_actual in exactos:
                importes.append(
                    valor_actual.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
                )
            centavos = int((pedido.total - sum(importes, Decimal("0"))) * 100)

            for indice in sorted(
                range(len(lineas)), key=lambda i: exactos[i] - importes[i], reverse=True
            )[: max(0, centavos)]:
                importes[indice] += Decimal("0.01")

            for (item, categoria), importe in zip(lineas, importes):
                categorias[categoria]["ventas"] += importe
                categorias[categoria]["unidades"] += item.cantidad
        horas = {"actual": [0] * 24, "anterior": [0] * 24}

        for clave, pedidos in (("actual", filas), ("anterior", previas)):
            for item in pedidos:
                horas[clave][
                    item.fecha_pago.replace(tzinfo=timezone.utc).astimezone(zona).hour
                ] += 1
        inicio_anio, fin_anio = limites(date(anio, 1, 1), date(anio, 12, 31))
        anual = [Decimal("0")] * 12

        for item in repo.ventas(db, empresa, inicio_anio, fin_anio, sucursal):
            anual[
                item.fecha_pago.replace(tzinfo=timezone.utc).astimezone(zona).month - 1
            ] += item.total
        locales = {}

        for item_actual_6 in repo.sucursales(db, empresa):
            locales[item_actual_6.id] = item_actual_6

        for item in respuesta["sucursales"]:
            local = locales.get(item["id_sucursal"])
            item["nombre"] = local.nombre if local else "Sucursal"
            item["direccion"] = local.direccion if local else ""
        elementos_2 = []

        for nombre_actual, valor_actual_2 in sorted(
            categorias.items(), key=lambda item: item[1]["ventas"], reverse=True
        ):
            elementos_2.append(
                {
                    "nombre": nombre_actual,
                    "ventas": str(valor_actual_2["ventas"]),
                    "unidades": valor_actual_2["unidades"],
                }
            )
        elementos_3 = []

        for valor_actual_3 in anual:
            elementos_3.append(str(valor_actual_3))
        campos_3 = {}
        campos_4 = {}

        for clave_27_30, rango_actual in rangos.items():
            campos_4[clave_27_30] = limites(*rango_actual)

        for clave_actual, valor_actual_4 in repo.totales_periodos(
            db, empresa, sucursal, campos_4
        ).items():
            campos_3[clave_actual] = str(valor_actual_4)
        respuesta.update(
            {
                "actualizado": datetime.now(timezone.utc).isoformat(),
                "zona_horaria": negocio.zona_horaria,
                "promedio_pedido": (
                    str((total / len(filas)).quantize(Decimal("0.01")))
                    if filas
                    else "0.00"
                ),
                "anterior": str(anterior),
                "variacion": (
                    str(((total - anterior) / anterior * 100).quantize(Decimal("0.1")))
                    if anterior
                    else None
                ),
                "categorias": elementos_2,
                "horas": horas,
                "anio": anio,
                "anio_actual": hoy.year,
                "anual": elementos_3,
                "total_anual": str(sum(anual, Decimal("0"))),
                "promedio_mensual": str(
                    (
                        sum(anual, Decimal("0"))
                        / (hoy.month if anio == hoy.year else 12)
                    ).quantize(Decimal("0.01"))
                ),
                "periodos": campos_3,
            }
        )

        return respuesta
