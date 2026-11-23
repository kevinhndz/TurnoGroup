from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import func

from backend.Categorias.tabla import Categorias
from backend.ConfiguracionImpuestos.tabla import ConfiguracionImpuestos
from backend.Descuentos.tabla import Descuentos
from backend.DisponibilidadProductos.tabla import DisponibilidadProductos
from backend.Empresas.tabla import Empresas
from backend.Mesas.tabla import Mesas
from backend.MetodosPago.tabla import MetodosPago
from backend.PagosSucursales.tabla import PagosSucursales
from backend.Pedidos.tabla import DetallesPedidos, Pedidos
from backend.Productos.tabla import Productos
from backend.Reservas.tabla import Reservas
from backend.ServiciosSucursales.tabla import ServiciosSucursales
from backend.Sucursales.tabla import Sucursales
from backend.TiposServicio.tabla import TiposServicio
from backend.Usuarios.tabla import Usuarios
from core.listados import filtrar_listado


class PedidoRepository:
    @staticmethod
    def nombre_usuario(db, id_usuario):
        usuario = db.get(Usuarios, id_usuario)

        return usuario.nombre if usuario else "Persona no disponible"

    @staticmethod
    def bloquear_sucursal(db, id_empresa, id_sucursal):
        return (
            db.query(Sucursales)
            .filter(
                Sucursales.id == id_sucursal,
                Sucursales.id_empresa == id_empresa,
                Sucursales.activo.is_(True),
            )
            .with_for_update()
            .first()
        )

    @staticmethod
    def buscar(db, id, id_empresa, id_sucursal, bloquear=False):
        consulta = db.query(Pedidos).filter(
            Pedidos.id == id,
            Pedidos.id_empresa == id_empresa,
            Pedidos.id_sucursal == id_sucursal,
        )

        return (consulta.with_for_update() if bloquear else consulta).first()

    @staticmethod
    def por_operacion(db, id_empresa, clave):
        return (
            db.query(Pedidos)
            .filter(Pedidos.id_empresa == id_empresa, Pedidos.clave_operacion == clave)
            .first()
        )

    @staticmethod
    def listar(db, id_empresa, id_sucursal, estado, filtros=None):
        consulta = db.query(Pedidos).filter(
            Pedidos.id_empresa == id_empresa, Pedidos.id_sucursal == id_sucursal
        )
        filtros = filtros or {}

        if filtros.get("entrega") or filtros.get("pago"):
            consulta = consulta.filter(Pedidos.estado != "Cancelado")

        if filtros.get("entrega") == "pendiente":
            consulta = consulta.filter(Pedidos.fecha_entrega.is_(None))
        elif filtros.get("entrega") == "servido":
            consulta = consulta.filter(Pedidos.fecha_entrega.is_not(None))

        if filtros.get("pago") == "pendiente":
            consulta = consulta.filter(Pedidos.fecha_pago.is_(None))
        elif filtros.get("pago") == "cobrado":
            consulta = consulta.filter(Pedidos.fecha_pago.is_not(None))

        if filtros.get("fecha"):
            inicio = datetime.combine(
                filtros["fecha"], time(), ZoneInfo("America/Tegucigalpa")
            )
            inicio = inicio.astimezone(timezone.utc).replace(tzinfo=None)
            consulta = consulta.filter(
                Pedidos.fecha_registro >= inicio,
                Pedidos.fecha_registro < inicio + timedelta(days=1),
            )

        if estado:
            consulta = consulta.filter(Pedidos.estado == estado)

        return filtrar_listado(consulta.order_by(Pedidos.id.desc()), Pedidos, filtros)

    @staticmethod
    def detalles(db, id):
        return (
            db.query(DetallesPedidos)
            .filter(DetallesPedidos.id_pedido == id)
            .order_by(DetallesPedidos.id)
            .all()
        )

    @staticmethod
    def productos(db, ids, id_empresa, id_sucursal):
        return (
            db.query(Productos)
            .join(
                DisponibilidadProductos,
                DisponibilidadProductos.id_producto == Productos.id,
            )
            .filter(
                Productos.id.in_(ids),
                Productos.id_empresa == id_empresa,
                Productos.disponible.is_(True),
                DisponibilidadProductos.id_sucursal == id_sucursal,
                DisponibilidadProductos.disponible.is_(True),
            )
            .all()
        )

    @staticmethod
    def servicio(db, id_sucursal, id_tipo):
        return (
            db.query(ServiciosSucursales, TiposServicio.clave_concepto)
            .join(
                TiposServicio, TiposServicio.id == ServiciosSucursales.id_tipo_servicio
            )
            .filter(
                ServiciosSucursales.id_sucursal == id_sucursal,
                ServiciosSucursales.id_tipo_servicio == id_tipo,
                ServiciosSucursales.habilitado.is_(True),
                TiposServicio.activo.is_(True),
            )
            .first()
        )

    @staticmethod
    def pago(db, id_sucursal, id_metodo):
        return (
            db.query(PagosSucursales)
            .join(MetodosPago, MetodosPago.id == PagosSucursales.id_metodo_pago)
            .filter(
                PagosSucursales.id_sucursal == id_sucursal,
                PagosSucursales.id_metodo_pago == id_metodo,
                PagosSucursales.habilitado.is_(True),
                MetodosPago.activo.is_(True),
            )
            .first()
        )

    @staticmethod
    def mesa(db, id, id_sucursal):
        return (
            db.query(Mesas)
            .filter(
                Mesas.id == id, Mesas.id_sucursal == id_sucursal, Mesas.activo.is_(True)
            )
            .first()
        )

    @staticmethod
    def mesa_ocupada(db, id, id_sucursal, excluir=None):
        consulta = db.query(Pedidos.id).filter(
            Pedidos.id_mesa == id,
            Pedidos.id_sucursal == id_sucursal,
            Pedidos.estado == "Abierto",
        )

        if excluir:
            consulta = consulta.filter(Pedidos.id != excluir)

        return consulta.first()

    @staticmethod
    def descuento(db, id, id_empresa):
        return (
            db.query(Descuentos)
            .filter(
                Descuentos.id == id,
                Descuentos.id_empresa == id_empresa,
                Descuentos.activo.is_(True),
            )
            .first()
        )

    @staticmethod
    def impuesto(db, id_empresa):
        return (
            db.query(ConfiguracionImpuestos)
            .filter(
                ConfiguracionImpuestos.id_empresa == id_empresa,
                ConfiguracionImpuestos.activo.is_(True),
            )
            .first()
        )

    @staticmethod
    def empresa(db, id):
        return db.get(Empresas, id)

    @staticmethod
    def catalogo(db, id_empresa, id_sucursal):
        productos = (
            db.query(Productos)
            .join(
                DisponibilidadProductos,
                DisponibilidadProductos.id_producto == Productos.id,
            )
            .filter(
                Productos.id_empresa == id_empresa,
                Productos.disponible.is_(True),
                DisponibilidadProductos.id_sucursal == id_sucursal,
                DisponibilidadProductos.disponible.is_(True),
            )
            .order_by(Productos.nombre, Productos.id)
            .all()
        )
        servicios = (
            db.query(ServiciosSucursales, TiposServicio)
            .join(
                TiposServicio, TiposServicio.id == ServiciosSucursales.id_tipo_servicio
            )
            .filter(
                ServiciosSucursales.id_sucursal == id_sucursal,
                ServiciosSucursales.habilitado.is_(True),
                TiposServicio.activo.is_(True),
            )
            .order_by(TiposServicio.id)
            .all()
        )
        pagos = (
            db.query(PagosSucursales, MetodosPago)
            .join(MetodosPago, MetodosPago.id == PagosSucursales.id_metodo_pago)
            .filter(
                PagosSucursales.id_sucursal == id_sucursal,
                PagosSucursales.habilitado.is_(True),
                MetodosPago.activo.is_(True),
            )
            .order_by(MetodosPago.id)
            .all()
        )
        cumple_condicion = False

        for servicio_actual, tipo_actual in servicios:
            if servicio_actual.mesas_habilitadas:
                cumple_condicion = True
                break

        return {
            "empresa": db.get(Empresas, id_empresa),
            "sucursal": db.query(Sucursales)
            .filter(Sucursales.id == id_sucursal, Sucursales.id_empresa == id_empresa)
            .first(),
            "productos": productos,
            "categorias": db.query(Categorias)
            .filter(Categorias.id_empresa == id_empresa, Categorias.activo.is_(True))
            .order_by(Categorias.orden_presentacion, Categorias.id)
            .all(),
            "servicios": servicios,
            "pagos": pagos,
            "mesas": (
                db.query(Mesas)
                .filter(Mesas.id_sucursal == id_sucursal, Mesas.activo.is_(True))
                .order_by(Mesas.id)
                .all()
                if cumple_condicion
                else []
            ),
            "descuentos": db.query(Descuentos)
            .filter(Descuentos.id_empresa == id_empresa, Descuentos.activo.is_(True))
            .order_by(Descuentos.nombre)
            .all(),
        }

    @staticmethod
    def agregar(db, registro):
        db.add(registro)

        return registro

    @staticmethod
    def agregar_varios(db, registros):
        db.add_all(registros)

    @staticmethod
    def guardar_cambios(db):
        db.flush()

    @staticmethod
    def eliminar_detalles(db, id):
        return (
            db.query(DetallesPedidos).filter(DetallesPedidos.id_pedido == id).delete()
        )

    @staticmethod
    def contar_pedidos_por_estado(db, empresa, sucursal):
        return (
            db.query(Pedidos.estado, func.count(Pedidos.id))
            .filter(Pedidos.id_empresa == empresa, Pedidos.id_sucursal == sucursal)
            .group_by(Pedidos.estado)
            .all()
        )

    @staticmethod
    def consultar_mesas_ocupadas(db, empresa, sucursal):
        return db.query(Pedidos.id_mesa).filter(
            Pedidos.id_empresa == empresa,
            Pedidos.id_sucursal == sucursal,
            Pedidos.estado == "Abierto",
        )

    @staticmethod
    def listar_mesas_reservadas(db, empresa, sucursal, instante):
        return (
            db.query(Reservas.id_mesa)
            .filter(
                Reservas.id_empresa == empresa,
                Reservas.id_sucursal == sucursal,
                Reservas.estado == "Confirmada",
                Reservas.inicio <= instante,
                Reservas.fin > instante,
            )
            .all()
        )

    @staticmethod
    def listar_mesas_activas(db, sucursal):
        return (
            db.query(Mesas)
            .filter(Mesas.id_sucursal == sucursal, Mesas.activo.is_(True))
            .order_by(Mesas.id)
            .all()
        )
