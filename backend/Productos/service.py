import base64
import binascii
import csv
import io
import os
import warnings
from decimal import Decimal, InvalidOperation
from io import BytesIO, StringIO
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile

from fastapi import HTTPException
from openpyxl import load_workbook
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.Categorias.repository import CategoriaRepository as repo_categoria
from backend.DisponibilidadProductos.tabla import DisponibilidadProductos
from backend.Empresas.repository import EmpresaRepository as repo_empresa
from backend.Productos.repository import ProductoRepository as repo
from backend.Productos.schema import (
    Revisar_Json_Editar_Producto,
    Revisar_Json_Nuevo_Producto,
)
from backend.Productos.tabla import Productos
from core.exceptions import (
    RecursoDuplicadoError,
    RecursoNoEncontradoError,
    SolicitudError,
)


class ProductoService:
    @staticmethod
    def revisar_archivo_service(json):
        extension = ".xlsx" if json.formato == "excel" else ".csv"

        if not json.nombre_archivo.lower().endswith(extension):
            raise SolicitudError(422, f"Selecciona un archivo {extension}")

        try:
            contenido = base64.b64decode(json.contenido, validate=True)
        except (ValueError, binascii.Error):
            raise SolicitudError(422, "No se pudo leer el archivo") from None

        if len(contenido) > 1_000_000:
            raise SolicitudError(413, "El archivo supera 1 MB")

        if json.formato == "excel":
            libro = None

            try:
                with ZipFile(BytesIO(contenido)) as archivo:
                    entradas = archivo.infolist()
                    condicion_verificada = len(entradas) > 1000

                    if not condicion_verificada:
                        total_calculado = 0

                        for item_actual in entradas:
                            total_calculado += item_actual.file_size
                        condicion_verificada = total_calculado > 10000000

                    if condicion_verificada:
                        raise SolicitudError(
                            422, "El Excel contiene demasiada informacion"
                        )

                    for item in entradas:
                        if item.filename.lower().endswith(".xml"):
                            xml = archivo.read(item).upper()

                            if b"<!DOCTYPE" in xml or b"<!ENTITY" in xml:
                                raise SolicitudError(
                                    422, "Usa un Excel sin contenido XML personalizado"
                                )
                libro = load_workbook(
                    BytesIO(contenido),
                    read_only=True,
                    data_only=False,
                    keep_links=False,
                )
                hoja = libro.worksheets[0]

                if hoja.max_row and hoja.max_row > 1001:
                    raise SolicitudError(
                        422,
                        "El Excel debe tener hasta 1000 productos y una fila de encabezados",
                    )
                filas = []

                for fila in hoja.iter_rows(max_row=1002, max_col=21):
                    cumple_condicion = False

                    for celda_actual in fila:
                        if celda_actual.data_type == "f":
                            cumple_condicion = True
                            break

                    if cumple_condicion:
                        raise SolicitudError(
                            422,
                            "Reemplaza las formulas del Excel por sus valores antes de importar",
                        )
                    valores = []

                    for celda_actual_2 in fila:
                        valores.append(celda_actual_2.value)

                    while valores and valores[-1] is None:
                        valores.pop()
                    cumple_condicion_2 = False

                    for valor_actual in valores:
                        if valor_actual is not None and str(valor_actual).strip():
                            cumple_condicion_2 = True
                            break

                    if cumple_condicion_2:
                        filas.append(valores)

                if hoja.max_column and hoja.max_column > 20:
                    raise SolicitudError(422, "Usa solo las columnas de la plantilla")
            except HTTPException:
                raise
            except Exception:
                raise SolicitudError(
                    422,
                    "No se pudo abrir el Excel. Usa un archivo .xlsx valido, sin contrasena",
                ) from None
            finally:
                if libro:
                    libro.close()
        else:
            try:
                texto = contenido.decode("utf-8-sig")

                try:
                    separador = (
                        csv.Sniffer().sniff(texto[:4096], delimiters=",;").delimiter
                    )
                except csv.Error:
                    separador = ","
                filas = []

                for fila in csv.reader(
                    StringIO(texto), delimiter=separador, strict=True
                ):
                    cumple_condicion_3 = False

                    for valor_actual_2 in fila:
                        if valor_actual_2.strip():
                            cumple_condicion_3 = True
                            break

                    if cumple_condicion_3:
                        filas.append(fila)

                    if len(filas) > 1001:
                        break
            except (UnicodeDecodeError, csv.Error):
                raise SolicitudError(
                    422, "No se pudo leer el CSV. Guardalo como CSV UTF-8"
                ) from None

        if not 2 <= len(filas) <= 1001:
            raise SolicitudError(422, "El archivo debe tener entre 1 y 1000 productos")
        titulos = []

        for valor_actual_3 in filas[0]:
            titulos.append(str(valor_actual_3 or "").strip().lower())
        permitidos = {"nombre", "precio", "categoria", "descripcion"}

        if (
            not {"nombre", "precio"}.issubset(titulos)
            or len(set(titulos)) != len(titulos)
            or not set(titulos).issubset(permitidos)
        ):
            raise SolicitudError(
                422,
                "Usa las columnas nombre, precio, categoria y descripcion, sin repetir. Nombre y precio son obligatorias",
            )
        productos = []
        nombres = set()

        for numero, valores in enumerate(filas[1:], start=2):
            if len(valores) > len(titulos):
                raise SolicitudError(422, f"Revisa las columnas de la fila {numero}")
            valores = valores + [None] * (len(titulos) - len(valores))
            fila = {}

            for titulo_actual, valor_actual_4 in zip(titulos, valores):
                fila[titulo_actual] = (
                    str(valor_actual_4).strip() if valor_actual_4 is not None else ""
                )

            try:
                precio = Decimal(fila["precio"])

                if (
                    not precio.is_finite()
                    or precio < 0
                    or precio > Decimal("99999999.99")
                    or precio != precio.quantize(Decimal("0.01"))
                ):
                    raise ValueError()
            except (InvalidOperation, ValueError):
                raise SolicitudError(
                    422,
                    f"Revisa el precio de la fila {numero}. Usa un numero no negativo con hasta dos decimales",
                ) from None

            if (
                not fila["nombre"]
                or len(fila["nombre"]) > 100
                or len(fila.get("descripcion", "")) > 10000
            ):
                raise SolicitudError(
                    422, f"Revisa el nombre y la descripcion de la fila {numero}"
                )

            if fila["nombre"].casefold() in nombres:
                raise RecursoDuplicadoError(
                    f"El producto de la fila {numero} esta repetido en el archivo"
                )
            nombres.add(fila["nombre"].casefold())
            productos.append(
                {
                    "nombre": fila["nombre"],
                    "precio": format(precio, ".2f"),
                    "categoria": fila.get("categoria", ""),
                    "descripcion": fila.get("descripcion") or None,
                }
            )

        return {"productos": productos}

    @staticmethod
    def crear_producto_service(
        json: Revisar_Json_Nuevo_Producto, db: Session, id_empresa: int
    ):
        try:
            empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

            if empresa is None:
                raise RecursoNoEncontradoError("No se encontro la empresa")

            if json.id_categoria is not None:
                categoria = repo_categoria.buscar_categoria_por_id(
                    db, json.id_categoria, id_empresa
                )

                if categoria is None or not categoria.activo:
                    raise RecursoNoEncontradoError(
                        "No se encontro la categoria de esta empresa"
                    )

            look_up = repo.buscar_producto_por_nombre(db, id_empresa, json.nombre)

            if look_up is not None:
                raise RecursoDuplicadoError(
                    "Ya existe un producto con ese nombre en la empresa"
                )

            nuevo_producto = Productos(
                id_empresa=id_empresa,
                id_categoria=json.id_categoria,
                nombre=json.nombre,
                descripcion=json.descripcion,
                precio=json.precio,
            )
            resultado = repo.guardar_nuevo_producto(db, nuevo_producto)
            repo.guardar_cambios(db)
            db.commit()
            repo.actualizar(db, resultado)

            return resultado
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def listar_productos_service(
        id_empresa: int,
        pagina_actual: int,
        limite: int,
        db: Session,
        id_sucursal=None,
        filtros=None,
    ):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        total, lista_productos = repo.listar_productos(
            db, id_empresa, pagina_actual, limite, id_sucursal, filtros=filtros
        )
        total_paginas = (total + limite - 1) // limite

        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": total_paginas,
            "data": lista_productos,
        }

    @staticmethod
    def ver_producto_service(id: int, id_empresa: int, db: Session, id_sucursal=None):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_producto_por_id(db, id, id_empresa, id_sucursal)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el producto")

        return look_up

    @staticmethod
    def editar_producto_service(
        json: Revisar_Json_Editar_Producto, id: int, id_empresa: int, db: Session
    ):
        try:
            empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

            if empresa is None:
                raise RecursoNoEncontradoError("No se encontro la empresa")

            look_up = repo.buscar_producto_por_id(db, id, id_empresa)

            if look_up is None:
                raise RecursoNoEncontradoError("No se encontro el producto")

            cambios = json.model_dump(exclude_unset=True)

            if not cambios:
                raise SolicitudError(
                    status_code=422, detail="Debes enviar al menos un campo para editar"
                )

            for campo, valor in cambios.items():
                if valor is None and campo not in ("id_categoria", "descripcion"):
                    raise SolicitudError(
                        status_code=422, detail="El campo " + campo + " no acepta null"
                    )

            if "nombre" in cambios and cambios["nombre"] != look_up.nombre:
                producto_existente = repo.buscar_producto_por_nombre(
                    db, id_empresa, cambios["nombre"]
                )

                if producto_existente is not None:
                    raise RecursoDuplicadoError(
                        "Ya existe un producto con ese nombre en la empresa"
                    )

            if "id_categoria" in cambios and cambios["id_categoria"] is not None:
                categoria = repo_categoria.buscar_categoria_por_id(
                    db, cambios["id_categoria"], id_empresa
                )

                if categoria is None or not categoria.activo:
                    raise RecursoNoEncontradoError(
                        "No se encontro la categoria de esta empresa"
                    )

            # Recorre el diccionario y actualiza cada campo enviado.
            for campo, valor in cambios.items():
                if valor is not None:
                    setattr(look_up, campo, valor)
                elif campo == "id_categoria" or campo == "descripcion":
                    setattr(look_up, campo, None)

            repo.guardar_cambios(db)
            db.commit()
            repo.actualizar(db, look_up)

            return look_up
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def desactivar_producto_service(id: int, id_empresa: int, db: Session):
        try:
            empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

            if empresa is None:
                raise RecursoNoEncontradoError("No se encontro la empresa")

            look_up = repo.buscar_producto_por_id(db, id, id_empresa)

            if look_up is None:
                raise RecursoNoEncontradoError("No se encontro el producto")

            look_up.disponible = False
            repo.guardar_cambios(db)
            db.commit()
            repo.actualizar(db, look_up)

            return look_up
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def importar_productos_service(json, db, id_empresa, id_sucursal):
        try:
            nombres = []

            for item_actual_4 in json.productos:
                nombres.append(item_actual_4.nombre.casefold())

            if len(set(nombres)) != len(nombres):
                raise RecursoDuplicadoError("Hay productos repetidos en el archivo")
            existentes = set()

            for (nombre_actual,) in repo.listar_nombres_para_importacion(
                db, id_empresa
            ):
                existentes.add(nombre_actual.casefold())

            if existentes.intersection(nombres):
                raise RecursoDuplicadoError(
                    "Un producto del archivo ya existe en tu catalogo"
                )

            for item in json.productos:
                if item.id_categoria:
                    categoria = repo_categoria.buscar_categoria_por_id(
                        db, item.id_categoria, id_empresa
                    )

                    if not categoria or not categoria.activo:
                        raise RecursoNoEncontradoError(
                            "No se encontro la categoria de esta empresa"
                        )

            if json.asignar_sucursal:
                sucursal = repo.buscar_sucursal_activa(db, id_sucursal, id_empresa)

                if not sucursal:
                    raise RecursoNoEncontradoError("No se encontro la sucursal")
            elementos = []

            for item_actual_2 in json.productos:
                elementos.append(
                    Productos(id_empresa=id_empresa, **item_actual_2.model_dump())
                )
            productos = elementos
            repo.agregar_varios(db, productos)
            repo.guardar_cambios(db)

            if json.asignar_sucursal:
                elementos_2 = []

                for item_actual_3 in productos:
                    elementos_2.append(
                        DisponibilidadProductos(
                            id_producto=item_actual_3.id,
                            id_sucursal=id_sucursal,
                            disponible=True,
                        )
                    )
                repo.agregar_varios(db, elementos_2)
            respuesta = {"creados": len(productos)}
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
    def guardar_imagen_service(json, id, id_empresa, db):
        try:
            look_up = repo.buscar_producto_por_id(db, id, id_empresa)

            if not look_up:
                raise RecursoNoEncontradoError("No se encontro el producto")

            try:
                contenido = base64.b64decode(json.contenido, validate=True)

                if len(contenido) > 5 * 1024 * 1024:
                    raise SolicitudError(413, "La imagen supera 5 MB")

                with warnings.catch_warnings():
                    warnings.simplefilter("error", Image.DecompressionBombWarning)

                    with Image.open(io.BytesIO(contenido)) as imagen:
                        if (
                            imagen.format not in ("JPEG", "PNG")
                            or imagen.width * imagen.height > 16_000_000
                        ):
                            raise SolicitudError(
                                422, "Usa JPG o PNG de hasta 16 millones de pixeles"
                            )
                        imagen = ImageOps.exif_transpose(imagen).convert("RGB")
                        imagen.thumbnail((1600, 1600))
                        salida = io.BytesIO()
                        imagen.save(salida, format="JPEG", quality=85)
            except (
                binascii.Error,
                ValueError,
                UnidentifiedImageError,
                OSError,
                Image.DecompressionBombWarning,
                Image.DecompressionBombError,
            ):
                raise SolicitudError(
                    422, "El archivo no es una imagen JPG o PNG valida"
                ) from None
            carpeta = ProductoService.carpeta_imagenes(id_empresa)
            carpeta.mkdir(parents=True, exist_ok=True)
            nombre = str(uuid4()) + ".jpg"
            archivo = carpeta / nombre
            archivo.write_bytes(salida.getvalue())
            anterior = look_up.ruta_imagen

            try:
                look_up.ruta_imagen = nombre
                repo.guardar_cambios(db)
                db.commit()
            except Exception:
                archivo.unlink(missing_ok=True)
                raise

            if anterior and Path(anterior).name == anterior:
                (carpeta / anterior).unlink(missing_ok=True)

            return look_up
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def carpeta_imagenes(id_empresa):
        return Path(
            os.environ.get(
                "TURNO_ARCHIVOS", str(Path(__file__).resolve().parents[2] / ".archivos")
            )
        ) / str(id_empresa)

    @staticmethod
    def consultar_imagen_service(id, id_empresa, db, id_sucursal):
        look_up = ProductoService.ver_producto_service(id, id_empresa, db, id_sucursal)

        if (
            not look_up.ruta_imagen
            or Path(look_up.ruta_imagen).name != look_up.ruta_imagen
        ):
            raise RecursoNoEncontradoError("No se encontro la imagen")
        archivo = ProductoService.carpeta_imagenes(id_empresa) / look_up.ruta_imagen

        if not archivo.is_file():
            raise RecursoNoEncontradoError("No se encontro la imagen")

        return archivo
