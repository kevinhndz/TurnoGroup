import hashlib
import json as codificar
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from backend.Pedidos.repository import PedidoRepository as repo
from backend.Pedidos.tabla import DetallesPedidos, Pedidos
from backend.Productos.schema import NuevoProductoRespuesta
from core.operaciones import ahora, alcance, exigir, moneda, paginar


class PedidoService:
    @staticmethod
    def respuesta(db, pedido, detalle=True):
        campos = [
            "id",
            "id_usuario",
            "id_tipo_servicio",
            "id_metodo_pago",
            "id_mesa",
            "id_descuento",
            "cliente",
            "telefono",
            "direccion",
            "nota",
            "estado",
            "fecha_registro",
            "fecha_pago",
            "fecha_entrega",
            "fecha_cancelacion",
            "motivo_cancelacion",
            "id_usuario_cobro",
            "id_usuario_cancelacion",
            "moneda",
            "impuesto_incluido",
        ]
        salida = {}

        for campo_actual in campos:
            salida[campo_actual] = getattr(pedido, campo_actual)

        for campo in [
            "subtotal",
            "descuento",
            "impuesto",
            "porcentaje_impuesto",
            "total",
        ]:
            salida[campo] = str(getattr(pedido, campo))

        if detalle:
            salida["registrado_por"] = repo.nombre_usuario(db, pedido.id_usuario)
            mesa = (
                repo.mesa(db, pedido.id_mesa, pedido.id_sucursal)
                if pedido.id_mesa
                else None
            )
            salida["nombre_mesa"] = mesa.nombre if mesa else None
            elementos_8 = []

            for item_actual in repo.detalles(db, pedido.id):
                elementos_8.append(
                    {
                        "id_producto": item_actual.id_producto,
                        "nombre": item_actual.nombre,
                        "cantidad": item_actual.cantidad,
                        "precio_unitario": str(item_actual.precio_unitario),
                        "nota": item_actual.nota,
                    }
                )
            salida["detalles"] = elementos_8

        return salida

    @staticmethod
    def calcular_service(json, db, contexto, excluir=None):
        empresa, sucursal = alcance(contexto)
        servicio = repo.servicio(db, sucursal, json.id_tipo_servicio)
        exigir(
            servicio is not None, "El servicio no esta habilitado en esta sucursal", 422
        )
        exigir(
            repo.pago(db, sucursal, json.id_metodo_pago) is not None,
            "El metodo de pago no esta habilitado en esta sucursal",
        )

        if servicio[1] == "domicilio":
            exigir(
                bool(json.cliente and json.direccion),
                "Domicilio requiere nombre y direccion del cliente",
            )

        if json.id_mesa is not None:
            exigir(
                servicio[1] == "comer_aqui" and servicio[0].mesas_habilitadas,
                "La gestion de mesas no esta habilitada",
            )
            exigir(
                repo.mesa(db, json.id_mesa, sucursal) is not None,
                "No se encontro la mesa",
                404,
            )
            exigir(
                not repo.mesa_ocupada(db, json.id_mesa, sucursal, excluir),
                "La mesa ya tiene un pedido abierto",
                409,
            )

        if json.id_mesa is not None:
            registro_encontrado = None

            for mesa_actual in PedidoService.mesas_service(db, contexto, excluir):
                if mesa_actual["id"] == json.id_mesa:
                    registro_encontrado = mesa_actual["estado"]
                    break
            estado = registro_encontrado
            exigir(estado == "Disponible", "La mesa ya no esta disponible", 409)
        campos_2 = {}
        valores_unicos = set()

        for fila_actual_4 in json.detalles:
            valores_unicos.add(fila_actual_4.id_producto)

        for item_actual_2 in repo.productos(db, valores_unicos, empresa, sucursal):
            campos_2[item_actual_2.id] = item_actual_2
        productos = campos_2
        detalles = []

        for item in json.detalles:
            exigir(
                item.id_producto in productos,
                "Un producto ya no esta disponible en esta sucursal",
                409,
            )
            producto = productos[item.id_producto]
            precio = moneda(producto.precio)
            detalles.append(
                {
                    "id_producto": producto.id,
                    "nombre": producto.nombre,
                    "cantidad": item.cantidad,
                    "precio_unitario": precio,
                    "nota": item.nota,
                }
            )
        total_calculado = Decimal("0")

        for fila_actual_2 in detalles:
            total_calculado += (
                fila_actual_2["precio_unitario"] * fila_actual_2["cantidad"]
            )
        subtotal = moneda(total_calculado)
        descuento = Decimal("0")

        if json.id_descuento is not None:
            configurado = repo.descuento(db, json.id_descuento, empresa)
            exigir(configurado is not None, "El descuento no esta disponible", 404)
            descuento = min(
                subtotal,
                moneda(
                    subtotal * configurado.valor / 100
                    if configurado.tipo_descuento == "Porcentaje"
                    else configurado.valor
                ),
            )
        base = subtotal - descuento
        configuracion = repo.impuesto(db, empresa)
        tasa = configuracion.porcentaje if configuracion else Decimal("0")
        incluido = bool(configuracion and configuracion.precios_incluyen_impuesto)
        impuesto = moneda(
            base - base / (1 + tasa / 100) if incluido else base * tasa / 100
        )
        total = base if incluido else base + impuesto
        exigir(total <= Decimal("9999999999.99"), "El total supera el limite permitido")

        return {
            "subtotal": subtotal,
            "descuento": descuento,
            "impuesto": impuesto,
            "porcentaje_impuesto": tasa,
            "impuesto_incluido": incluido,
            "total": moneda(total),
            "moneda": repo.empresa(db, empresa).codigo_moneda,
            "detalles": detalles,
        }

    @staticmethod
    def crear_service(json, db, contexto):
        try:
            empresa, sucursal = alcance(contexto)
            clave = str(json.clave_operacion)
            huella = hashlib.sha256(
                codificar.dumps(
                    json.model_dump(mode="json", exclude={"clave_operacion"}),
                    sort_keys=True,
                ).encode()
            ).hexdigest()
            repo.bloquear_sucursal(db, empresa, sucursal)
            look_up = repo.por_operacion(db, empresa, clave)

            if look_up:
                exigir(
                    look_up.huella_solicitud == huella,
                    "La operacion ya se uso con otro pedido",
                    409,
                )
                exigir(look_up.id_sucursal == sucursal, "No se encontro el pedido", 404)

                return PedidoService.respuesta(db, look_up)
            calculo = PedidoService.calcular_service(json, db, contexto)

            if json.total_esperado is not None:
                exigir(
                    calculo["total"] == json.total_esperado,
                    "El precio cambio. Revisa de nuevo el total antes de registrar",
                    409,
                )
            filas = calculo.pop("detalles")
            nuevo_pedido = Pedidos(
                id_empresa=empresa,
                id_sucursal=sucursal,
                id_usuario=contexto["usuario"].id,
                clave_operacion=clave,
                huella_solicitud=huella,
                fecha_registro=ahora(),
                estado="Abierto",
                **json.model_dump(
                    exclude={"detalles", "clave_operacion", "cobrado", "total_esperado"}
                ),
                **calculo,
            )

            if json.cobrado:
                PedidoService.aplicar_cobro(
                    nuevo_pedido, json.id_metodo_pago, db, contexto
                )
            repo.agregar(db, nuevo_pedido)
            repo.guardar_cambios(db)
            elementos_10 = []

            for fila_actual in filas:
                elementos_10.append(
                    DetallesPedidos(id_pedido=nuevo_pedido.id, **fila_actual)
                )
            repo.agregar_varios(db, elementos_10)
            repo.guardar_cambios(db)
            respuesta = PedidoService.respuesta(db, nuevo_pedido)
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
    def aplicar_cobro(pedido, id_metodo, db, contexto):
        empresa, sucursal = alcance(contexto)
        exigir(
            repo.pago(db, sucursal, id_metodo) is not None,
            "El metodo de pago no esta habilitado",
        )
        pedido.id_metodo_pago = id_metodo
        pedido.id_usuario_cobro = contexto["usuario"].id
        pedido.fecha_pago = ahora()
        pedido.estado = "Cerrado"

    @staticmethod
    def accion_service(id, accion, json, db, contexto):
        try:
            empresa, sucursal = alcance(contexto)
            look_up = repo.buscar(db, id, empresa, sucursal, True)
            exigir(look_up is not None, "No se encontro el pedido", 404)
            exigir(look_up.estado != "Cancelado", "El pedido esta cancelado", 409)

            if accion == "cobrar":
                exigir(look_up.fecha_pago is None, "El pago ya fue registrado", 409)
                PedidoService.aplicar_cobro(look_up, json.id_metodo_pago, db, contexto)
            elif accion == "entregar":
                exigir(look_up.fecha_entrega is None, "El pedido ya fue entregado", 409)
                look_up.fecha_entrega = ahora()

                if look_up.fecha_pago:
                    look_up.estado = "Cerrado"
            elif accion == "cancelar":
                look_up.estado = "Cancelado"
                look_up.fecha_cancelacion = ahora()
                look_up.motivo_cancelacion = json.motivo
                look_up.id_usuario_cancelacion = contexto["usuario"].id
            respuesta = PedidoService.respuesta(db, look_up)
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
    def editar_service(id, json, db, contexto):
        try:
            empresa, sucursal = alcance(contexto)
            repo.bloquear_sucursal(db, empresa, sucursal)
            look_up = repo.buscar(db, id, empresa, sucursal, True)
            exigir(look_up is not None, "No se encontro el pedido", 404)
            exigir(
                look_up.estado == "Abierto"
                and not look_up.fecha_pago
                and not look_up.fecha_entrega,
                "Solo puedes editar un pedido abierto sin cobro ni entrega",
                409,
            )
            calculo = PedidoService.calcular_service(json, db, contexto, id)
            filas = calculo.pop("detalles")

            for campo, valor in {
                **json.model_dump(exclude={"detalles"}),
                **calculo,
            }.items():
                setattr(look_up, campo, valor)
            repo.eliminar_detalles(db, id)
            elementos = []

            for fila_actual_3 in filas:
                elementos.append(DetallesPedidos(id_pedido=id, **fila_actual_3))
            repo.agregar_varios(db, elementos)
            repo.guardar_cambios(db)
            respuesta = PedidoService.respuesta(db, look_up)
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
    def ver_service(id, db, contexto):
        empresa, sucursal = alcance(contexto)
        look_up = repo.buscar(db, id, empresa, sucursal)
        exigir(look_up is not None, "No se encontro el pedido", 404)

        return PedidoService.respuesta(db, look_up)

    @staticmethod
    def listar_service(db, contexto, pagina, limite, estado, filtros=None):
        empresa, sucursal = alcance(contexto)
        respuesta = paginar(
            repo.listar(db, empresa, sucursal, estado, filtros),
            pagina,
            limite,
            lambda fila: PedidoService.respuesta(db, fila, False),
        )
        conteos = dict(repo.contar_pedidos_por_estado(db, empresa, sucursal))
        respuesta["conteos"] = {**conteos, "Todos": sum(conteos.values())}
        entregados = repo.listar(db, empresa, sucursal, estado, filtros).filter(
            Pedidos.estado != "Cancelado",
            Pedidos.fecha_entrega.is_not(None),
            Pedidos.fecha_entrega >= Pedidos.fecha_registro,
        )

        if db.bind.dialect.name == "sqlite":
            minutos = (
                func.julianday(Pedidos.fecha_entrega)
                - func.julianday(Pedidos.fecha_registro)
            ) * 1440
        else:
            minutos = (
                func.extract("epoch", Pedidos.fecha_entrega - Pedidos.fecha_registro)
                / 60
            )
        promedio = entregados.order_by(None).with_entities(func.avg(minutos)).scalar()
        respuesta["promedio_entrega_minutos"] = (
            round(float(promedio), 1) if promedio is not None else None
        )

        return respuesta

    @staticmethod
    def catalogo_service(db, contexto):
        empresa, sucursal = alcance(contexto)
        datos = repo.catalogo(db, empresa, sucursal)
        elementos_2 = []

        for producto_actual in datos["productos"]:
            elementos_2.append(
                {
                    **NuevoProductoRespuesta.model_validate(producto_actual).model_dump(
                        mode="json"
                    ),
                    "precio_local": str(producto_actual.precio),
                }
            )
        elementos_3 = []

        for categoria_actual in datos["categorias"]:
            elementos_3.append(
                {
                    "id": categoria_actual.id,
                    "nombre": categoria_actual.nombre,
                    "activo": True,
                }
            )
        elementos_4 = []

        for servicio_actual, tipo_actual in datos["servicios"]:
            elementos_4.append(
                {
                    "id_tipo_servicio": tipo_actual.id,
                    "nombre_visible": tipo_actual.nombre_visible,
                    "clave_concepto": tipo_actual.clave_concepto,
                    "mesas_habilitadas": servicio_actual.mesas_habilitadas,
                    "reservas_habilitadas": servicio_actual.reservas_habilitadas,
                }
            )
        elementos_5 = []

        for pago_actual, metodo_actual in datos["pagos"]:
            elementos_5.append(
                {
                    "id_metodo_pago": metodo_actual.id,
                    "nombre_visible": metodo_actual.nombre_visible,
                    "clave_concepto": metodo_actual.clave_concepto,
                }
            )
        elementos_6 = []

        for mesa_actual_2 in datos["mesas"]:
            elementos_6.append(
                {
                    "id": mesa_actual_2.id,
                    "nombre": mesa_actual_2.nombre,
                    "capacidad": mesa_actual_2.capacidad,
                    "activo": True,
                }
            )
        elementos_7 = []

        for descuento_actual in datos["descuentos"]:
            elementos_7.append(
                {
                    "id": descuento_actual.id,
                    "nombre": descuento_actual.nombre,
                    "tipo_descuento": descuento_actual.tipo_descuento,
                    "valor": str(descuento_actual.valor),
                    "activo": True,
                }
            )

        return {
            "empresa": {
                "id": datos["empresa"].id,
                "nombre": datos["empresa"].nombre,
                "codigo_moneda": datos["empresa"].codigo_moneda,
            },
            "sucursal": {
                "id": datos["sucursal"].id,
                "nombre": datos["sucursal"].nombre,
            },
            "productos": elementos_2,
            "categorias": elementos_3,
            "servicios": elementos_4,
            "pagos": elementos_5,
            "mesas": elementos_6,
            "descuentos": elementos_7,
        }

    @staticmethod
    def mesas_service(db, contexto, excluir=None):
        empresa, sucursal = alcance(contexto)
        instante = ahora()
        consulta = repo.consultar_mesas_ocupadas(db, empresa, sucursal)

        if excluir:
            consulta = consulta.filter(Pedidos.id != excluir)
        ocupadas = set()

        for (id_actual,) in consulta.all():
            if id_actual:
                ocupadas.add(id_actual)
        reservadas = set()

        for (id_actual_2,) in repo.listar_mesas_reservadas(
            db, empresa, sucursal, instante
        ):
            reservadas.add(id_actual_2)
        elementos_9 = []

        for mesa_actual_3 in repo.listar_mesas_activas(db, sucursal):
            elementos_9.append(
                {
                    "id": mesa_actual_3.id,
                    "nombre": mesa_actual_3.nombre,
                    "capacidad": mesa_actual_3.capacidad,
                    "estado": (
                        "Ocupada"
                        if mesa_actual_3.id in ocupadas
                        else (
                            "Reservada"
                            if mesa_actual_3.id in reservadas
                            else "Disponible"
                        )
                    ),
                }
            )

        return elementos_9

    @staticmethod
    def consultar_operacion_service(clave_operacion, db, contexto):
        empresa, sucursal = alcance(contexto)
        look_up = repo.por_operacion(db, empresa, str(clave_operacion))
        exigir(
            look_up is not None and look_up.id_sucursal == sucursal,
            "No se encontro el pedido",
            404,
        )

        return PedidoService.respuesta(db, look_up)
