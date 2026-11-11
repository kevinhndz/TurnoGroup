from backend.Bitacora.tabla import Bitacora
<<<<<<< HEAD
=======
from core.listados import filtrar_listado
>>>>>>> pruebas-frontend
from backend.Usuarios.tabla import Usuarios
from backend.Sucursales.tabla import Sucursales


class BitacoraRepository:
    @staticmethod
<<<<<<< HEAD
    def listar(db, empresa, sucursal):
=======
    def listar(db, empresa, sucursal, filtros=None):
>>>>>>> pruebas-frontend
        consulta = (
            db.query(Bitacora, Usuarios.nombre, Sucursales.nombre)
            .join(Usuarios, Usuarios.id == Bitacora.id_usuario)
            .outerjoin(Sucursales, Sucursales.id == Bitacora.id_sucursal)
            .filter(Bitacora.id_empresa == empresa)
        )
        if sucursal is not None or empresa is None:
            consulta = consulta.filter(Bitacora.id_sucursal == sucursal)
<<<<<<< HEAD
        return consulta.order_by(Bitacora.id.desc())
=======
        return filtrar_listado(consulta.order_by(Bitacora.id.desc()), Bitacora, filtros, [Usuarios.nombre])
>>>>>>> pruebas-frontend
