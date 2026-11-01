import hashlib
import json as codificar
from decimal import Decimal
from sqlalchemy import func
from backend.Pedidos.repository import PedidoRepository as repo
from backend.Pedidos.tabla import Pedidos, DetallesPedidos
from core.operaciones import ahora, moneda, exigir, alcance, paginar


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
        salida = {campo: getattr(pedido, campo) for campo in campos}
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
            mesa = repo.mesa(db, pedido.id_mesa, pedido.id_sucursal) if pedido.id_mesa else None
            salida["nombre_mesa"] = mesa.nombre if mesa else None
            salida["detalles"] = [
                {
                    "id_producto": item.id_producto,
                    "nombre": item.nombre,
                    "cantidad": item.cantidad,
                    "precio_unitario": str(item.precio_unitario),
                    "nota": item.nota,
                }
                for item in repo.detalles(db, pedido.id)
            ]
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
            estado = next(
                (
                    mesa["estado"]
                    for mesa in PedidoService.mesas_service(db, contexto, excluir)
                    if mesa["id"] == json.id_mesa
                ),
                None,
            )
            exigir(estado == "Disponible", "La mesa ya no esta disponible", 409)
        productos = {
            item.id: (item, especial)
            for item, especial in repo.productos(
                db, {fila.id_producto for fila in json.detalles}, empresa, sucursal
            )
        }
        detalles = []
        for item in json.detalles:
            exigir(
                item.id_producto in productos,
                "Un producto ya no esta disponible en esta sucursal",
                409,
            )
            producto, especial = productos[item.id_producto]
            precio = moneda(especial if especial is not None else producto.precio)
            detalles.append(
                {
                    "id_producto": producto.id,
                    "nombre": producto.nombre,
                    "cantidad": item.cantidad,
                    "precio_unitario": precio,
                    "nota": item.nota,
                }
            )
        subtotal = moneda(
            sum(
                (fila["precio_unitario"] * fila["cantidad"] for fila in detalles),
                Decimal("0"),
            )
        )
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
            **calculo
        )
        if json.cobrado:
            PedidoService.aplicar_cobro(nuevo_pedido, json.id_metodo_pago, db, contexto)
        db.add(nuevo_pedido)
        db.flush()
        db.add_all(
            [DetallesPedidos(id_pedido=nuevo_pedido.id, **fila) for fila in filas]
        )
        db.flush()
        respuesta = PedidoService.respuesta(db, nuevo_pedido)
        db.commit()
        return respuesta

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
        db.commit()
        return respuesta

    @staticmethod
    def editar_service(id, json, db, contexto):
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
        db.query(DetallesPedidos).filter(DetallesPedidos.id_pedido == id).delete()
        db.add_all([DetallesPedidos(id_pedido=id, **fila) for fila in filas])
        db.flush()
        respuesta = PedidoService.respuesta(db, look_up)
        db.commit()
        return respuesta

    @staticmethod
    def ver_service(id, db, contexto):
        empresa, sucursal = alcance(contexto)
        look_up = repo.buscar(db, id, empresa, sucursal)
        exigir(look_up is not None, "No se encontro el pedido", 404)
        return PedidoService.respuesta(db, look_up)

    @staticmethod
    def listar_service(db, contexto, pagina, limite, estado):
        empresa, sucursal = alcance(contexto)
        respuesta = paginar(
            repo.listar(db, empresa, sucursal, estado),
            pagina,
            limite,
            lambda fila: PedidoService.respuesta(db, fila, False),
        )
        conteos = dict(
            db.query(Pedidos.estado, func.count(Pedidos.id))
            .filter(Pedidos.id_empresa == empresa, Pedidos.id_sucursal == sucursal)
            .group_by(Pedidos.estado)
            .all()
        )
        respuesta["conteos"] = {**conteos, "Todos": sum(conteos.values())}
        return respuesta

    @staticmethod
    def catalogo_service(db, contexto):
        from backend.Productos.schema import NuevoProductoRespuesta

        empresa, sucursal = alcance(contexto)
        datos = repo.catalogo(db, empresa, sucursal)
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
            "productos": [
                {
                    **NuevoProductoRespuesta.model_validate(producto).model_dump(
                        mode="json"
                    ),
                    "precio_local": str(
                        especial if especial is not None else producto.precio
                    ),
                }
                for producto, especial in datos["productos"]
            ],
            "categorias": [
                {"id": categoria.id, "nombre": categoria.nombre, "activo": True}
                for categoria in datos["categorias"]
            ],
            "servicios": [
                {
                    "id_tipo_servicio": tipo.id,
                    "nombre_visible": tipo.nombre_visible,
                    "clave_concepto": tipo.clave_concepto,
                    "mesas_habilitadas": servicio.mesas_habilitadas,
                    "reservas_habilitadas": servicio.reservas_habilitadas,
                }
                for servicio, tipo in datos["servicios"]
            ],
            "pagos": [
                {"id_metodo_pago": metodo.id, "nombre_visible": metodo.nombre_visible, "clave_concepto": metodo.clave_concepto}
                for pago, metodo in datos["pagos"]
            ],
            "mesas": [
                {
                    "id": mesa.id,
                    "nombre": mesa.nombre,
                    "capacidad": mesa.capacidad,
                    "activo": True,
                }
                for mesa in datos["mesas"]
            ],
            "descuentos": [
                {
                    "id": descuento.id,
                    "nombre": descuento.nombre,
                    "tipo_descuento": descuento.tipo_descuento,
                    "valor": str(descuento.valor),
                    "activo": True,
                }
                for descuento in datos["descuentos"]
            ],
        }

    @staticmethod
    def mesas_service(db, contexto, excluir=None):
        from backend.Mesas.tabla import Mesas
        from backend.Reservas.tabla import Reservas

        empresa, sucursal = alcance(contexto)
        instante = ahora()
        consulta = db.query(Pedidos.id_mesa).filter(
            Pedidos.id_empresa == empresa,
            Pedidos.id_sucursal == sucursal,
            Pedidos.estado == "Abierto",
        )
        if excluir:
            consulta = consulta.filter(Pedidos.id != excluir)
        ocupadas = {id for id, in consulta.all() if id}
        reservadas = {
            id
            for id, in db.query(Reservas.id_mesa)
            .filter(
                Reservas.id_empresa == empresa,
                Reservas.id_sucursal == sucursal,
                Reservas.estado == "Confirmada",
                Reservas.inicio <= instante,
                Reservas.fin > instante,
            )
            .all()
        }
        return [
            {
                "id": mesa.id,
                "nombre": mesa.nombre,
                "capacidad": mesa.capacidad,
                "estado": (
                    "Ocupada"
                    if mesa.id in ocupadas
                    else "Reservada" if mesa.id in reservadas else "Disponible"
                ),
            }
            for mesa in db.query(Mesas)
            .filter(Mesas.id_sucursal == sucursal, Mesas.activo.is_(True))
            .order_by(Mesas.id)
            .all()
        ]

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
