from sqlalchemy import event, inspect
from sqlalchemy.orm import Session
from backend.Bitacora.tabla import Bitacora
from backend.Bitacora.repository import BitacoraRepository as repo
from core.operaciones import alcance, paginar


class BitacoraService:
    @staticmethod
    def listar_service(db, contexto, pagina, limite, solo_sucursal=True, filtros=None):
        from core.operaciones import exigir

        if contexto["rol_plataforma"] == "Superadministrador":
            empresa, sucursal = None, None
        elif not solo_sucursal:
            exigir(
                contexto.get("rol") == "Gerente" and contexto.get("id_empresa"),
                "No estas autorizado",
                403,
            )
            empresa, sucursal = contexto["id_empresa"], None
        else:
            empresa, sucursal = alcance(contexto)
        return paginar(
            repo.listar(db, empresa, sucursal, filtros),
            pagina,
            limite,
            lambda fila: {
                "id": fila[0].id,
                "persona": fila[1],
                "sucursal": fila[2],
                "recurso": fila[0].recurso,
                "id_registro": fila[0].id_registro,
                "accion": fila[0].accion,
                "cliente": fila[0].cliente,
                "fecha": fila[0].fecha,
            },
        )


@event.listens_for(Session, "before_flush")
def preparar_eventos(db, contexto, instancias):
    actor = db.info.get("actor_bitacora")
    if not actor:
        return
    recursos = {
        "pedidos": "Pedido",
        "cajas": "Caja",
        "reservas": "Reserva",
        "mesas": "Mesa",
    }
    if actor.get("plataforma"):
        recursos = {"empresas": "Empresa", "usuarios": "Cuenta"}
    pendientes = db.info.setdefault("eventos_bitacora", [])
    for objeto in list(db.new) + list(db.dirty):
        tabla = getattr(objeto, "__tablename__", "")
        if tabla not in recursos or (
            objeto not in db.new
            and not db.is_modified(objeto, include_collections=False)
        ):
            continue
        if getattr(objeto, "id_sucursal", None) != actor["sucursal"]:
            continue
        femenino = tabla in ("mesas", "reservas", "cajas", "empresas", "usuarios")
        accion = recursos[tabla] + (
            (" creada" if femenino else " creado")
            if objeto in db.new
            else (" actualizada" if femenino else " actualizado")
        )
        if tabla == "cajas" and objeto in db.new:
            accion = "Caja abierta"
        if (
            tabla == "reservas"
            and objeto not in db.new
            and inspect(objeto).attrs.estado.history.has_changes()
        ):
            accion = {
                "Atendida": "Reserva atendida",
                "Cancelada": "Reserva cancelada",
            }.get(objeto.estado, accion)
        if (
            tabla == "mesas"
            and objeto not in db.new
            and inspect(objeto).attrs.activo.history.has_changes()
        ):
            accion = "Mesa activada" if objeto.activo else "Mesa desactivada"

        for campo, texto in [
            ("fecha_pago", "Pedido cobrado"),
            ("fecha_entrega", "Pedido entregado"),
            ("fecha_cancelacion", "Pedido cancelado"),
            ("fecha_cierre", "Caja cerrada"),
        ]:
            if (
                objeto not in db.new
                and campo in inspect(objeto).attrs
                and inspect(objeto).attrs[campo].history.has_changes()
                and getattr(objeto, campo)
            ):
                accion = texto
        pendientes.append((objeto, accion, tabla, actor.copy()))
        if tabla == "pedidos" and objeto in db.new and objeto.fecha_pago:
            pendientes.append((objeto, "Pedido cobrado", tabla, actor.copy()))


@event.listens_for(Session, "after_flush_postexec")
def guardar_eventos(db, contexto):
    for objeto, accion, recurso, actor in db.info.pop("eventos_bitacora", []):
        db.add(
            Bitacora(
                id_empresa=actor["empresa"],
                id_sucursal=actor["sucursal"],
                id_usuario=actor["usuario"],
                recurso=recurso,
                id_registro=objeto.id,
                accion=accion,
                cliente=(
                    getattr(objeto, "cliente", None) if recurso == "pedidos" else None
                ),
            )
        )


@event.listens_for(Session, "after_rollback")
def limpiar_eventos(db):
    db.info.pop("eventos_bitacora", None)
