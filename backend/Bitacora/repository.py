from backend.Bitacora.tabla import Bitacora
from core.listados import filtrar_listado
from backend.Usuarios.tabla import Usuarios
from backend.Sucursales.tabla import Sucursales


class BitacoraRepository:
    @staticmethod
    def listar(db, empresa, sucursal, filtros=None):
        consulta = (
            db.query(Bitacora, Usuarios.nombre, Sucursales.nombre)
            .join(Usuarios, Usuarios.id == Bitacora.id_usuario)
            .outerjoin(Sucursales, Sucursales.id == Bitacora.id_sucursal)
            .filter(Bitacora.id_empresa == empresa)
        )
        if sucursal is not None or empresa is None:
            consulta = consulta.filter(Bitacora.id_sucursal == sucursal)
        return filtrar_listado(consulta.order_by(Bitacora.id.desc()), Bitacora, filtros, [Usuarios.nombre])
