from difflib import SequenceMatcher
import json
import logging
from time import monotonic
import unicodedata

from backend.Categorias.tabla import Categorias
from backend.DisponibilidadProductos.tabla import DisponibilidadProductos
from backend.Productos import menu_ia
from backend.Productos.menu_repository import MenuRepository as repo
from backend.Productos.repository import ProductoRepository
from backend.Productos.tabla import Productos
from core.config import revision
from core.exceptions import SolicitudError
from utils.rate_limiting import limitar_identidad

registro = logging.getLogger("turnogroup.seguridad")


def normalizar(nombre):
    letras = unicodedata.normalize("NFKD", nombre.casefold())
    return " ".join(
        "".join(letra for letra in letras if not unicodedata.combining(letra)).split()
    )


class MenuService:
    @staticmethod
    def preparar(solicitud, db, id_empresa):
        limitar_identidad(
            "menu_ia_empresa", str(id_empresa), revision.LIMITE_MENU_IA, 60
        )
        limitar_identidad(
            "menu_ia_diario", str(id_empresa), revision.LIMITE_MENU_IA_DIARIO, 86400
        )
        moneda = repo.empresa(db, id_empresa).codigo_moneda or "HNL"
        # Libero la conexion antes de esperar al proveedor; aqui no hay escrituras.
        db.rollback()
        inicio = monotonic()
        evento = {
            "evento": "extraccion_menu_ia",
            "id_empresa": id_empresa,
            "modelo": revision.OPENAI_MODELO_CATALOGO,
            "entrada": "imagen" if solicitud.imagen else "texto",
        }
        try:
            extraccion, uso = menu_ia.extraer_menu(solicitud, moneda)
            evento.update(uso, estado="completado")
            if not extraccion.productos:
                raise SolicitudError(
                    422,
                    "No se encontraron productos. Usa una foto mas clara o una lista con precios.",
                )
            propuesta = MenuService.revisar(extraccion.productos, db, id_empresa)
            propuesta["advertencias"] = extraccion.advertencias
            return propuesta
        except SolicitudError as error:
            evento.update(estado="rechazado", codigo=error.status_code)
            raise
        finally:
            evento["latency_ms"] = round((monotonic() - inicio) * 1000)
            registro.info(json.dumps(evento))

    @staticmethod
    def revisar(productos, db, id_empresa):
        existentes = repo.productos(db, id_empresa)
        categorias = repo.categorias(db, id_empresa)
        por_nombre = {normalizar(p.nombre): p for p in existentes}
        categorias_por_nombre = {normalizar(c.nombre): c for c in categorias}
        recibidos = set()
        filas = []
        for producto in productos:
            fila = producto.model_dump()
            nombre = normalizar(producto.nombre)
            exacto = por_nombre.get(nombre)
            similares = []
            if not exacto:
                candidatos = []
                for existente in existentes:
                    puntaje = SequenceMatcher(
                        None, nombre, normalizar(existente.nombre)
                    ).ratio()
                    if puntaje >= 0.72:
                        candidatos.append((puntaje, existente))
                candidatos.sort(key=lambda item: item[0], reverse=True)
                for _, existente in candidatos[:3]:
                    similares.append(
                        {
                            "id": existente.id,
                            "nombre": existente.nombre,
                            "precio": str(existente.precio),
                            "disponible": existente.disponible,
                        }
                    )
            categoria = categorias_por_nombre.get(normalizar(producto.categoria or ""))
            fila.update(
                existente=(
                    {
                        "id": exacto.id,
                        "nombre": exacto.nombre,
                        "precio": str(exacto.precio),
                        "disponible": exacto.disponible,
                    }
                    if exacto
                    else None
                ),
                similares=similares,
                repetido=nombre in recibidos,
                categoria_existente=(
                    categoria.nombre if categoria and categoria.activo else None
                ),
                categoria_inactiva=bool(categoria and not categoria.activo),
            )
            filas.append(fila)
            recibidos.add(nombre)
        return {
            "productos": filas,
            "advertencias": [],
            "moneda": repo.empresa(db, id_empresa).codigo_moneda,
        }

    @staticmethod
    def confirmar(solicitud, db, id_empresa, id_sucursal):
        try:
            # Serializo confirmaciones del mismo negocio, incluida la creacion de categorias.
            repo.empresa(db, id_empresa, bloquear=True)
            if (
                solicitud.asignar_sucursal
                and not ProductoRepository.buscar_sucursal_activa(
                    db, id_sucursal, id_empresa
                )
            ):
                raise SolicitudError(404, "No se encontro la sucursal")
            existentes = repo.productos(db, id_empresa)
            por_id = {p.id: p for p in existentes}
            nombres = {normalizar(p.nombre) for p in existentes}
            categorias = {
                normalizar(c.nombre): c for c in repo.categorias(db, id_empresa)
            }
            creados = categorias_creadas = reutilizados = 0
            usados = set()
            for fila in solicitud.productos:
                if fila.accion == "usar_existente":
                    producto = por_id.get(fila.id_existente)
                    if not producto:
                        raise SolicitudError(
                            404, "No se encontro el producto existente"
                        )
                    if not producto.disponible:
                        raise SolicitudError(
                            409,
                            "El producto existente esta desactivado. Revisalo en Productos.",
                        )
                    if producto.id in usados:
                        raise SolicitudError(
                            409, "Seleccionaste el mismo producto mas de una vez"
                        )
                    reutilizados += 1
                else:
                    nombre = normalizar(fila.nombre)
                    if nombre in nombres:
                        raise SolicitudError(
                            409,
                            "Un producto ya existe o esta repetido. Revisa la propuesta antes de confirmar.",
                        )
                    categoria = None
                    if fila.categoria:
                        clave = normalizar(fila.categoria)
                        categoria = categorias.get(clave)
                        if categoria and not categoria.activo:
                            raise SolicitudError(
                                409,
                                "La categoria esta desactivada. Elige otra o reactiva la existente.",
                            )
                        if not categoria:
                            categoria = repo.agregar(
                                db,
                                Categorias(
                                    id_empresa=id_empresa, nombre=fila.categoria
                                ),
                            )
                            categorias[clave] = categoria
                            categorias_creadas += 1
                    producto = repo.agregar(
                        db,
                        Productos(
                            id_empresa=id_empresa,
                            nombre=fila.nombre,
                            precio=fila.precio,
                            descripcion=fila.descripcion,
                            id_categoria=categoria.id if categoria else None,
                        ),
                    )
                    nombres.add(nombre)
                    creados += 1
                usados.add(producto.id)
                if solicitud.asignar_sucursal:
                    asignacion = repo.asignacion(db, producto.id, id_sucursal)
                    if asignacion:
                        asignacion.disponible = True
                    else:
                        repo.agregar(
                            db,
                            DisponibilidadProductos(
                                id_producto=producto.id,
                                id_sucursal=id_sucursal,
                                disponible=True,
                            ),
                        )
            db.commit()
            return {
                "creados": creados,
                "categorias_creadas": categorias_creadas,
                "reutilizados": reutilizados,
            }
        except Exception:
            db.rollback()
            raise
