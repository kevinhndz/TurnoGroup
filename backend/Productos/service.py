from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.Categorias.repository import CategoriaRepository as repo_categoria
from backend.Empresas.repository import EmpresaRepository as repo_empresa
from backend.Productos.repository import ProductoRepository as repo
from backend.Productos.schema import (
    Revisar_Json_Nuevo_Producto,
    Revisar_Json_Editar_Producto,
)
from backend.Productos.tabla import Productos
from core.exceptions import RecursoNoEncontradoError, RecursoDuplicadoError


class ProductoService:

    @staticmethod
    def crear_producto_service(
        json: Revisar_Json_Nuevo_Producto, db: Session, id_empresa: int
    ):
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
        return repo.guardar_nuevo_producto(db, nuevo_producto)

    @staticmethod
    def listar_productos_service(
        id_empresa: int, pagina_actual: int, limite: int, db: Session, id_sucursal=None
    ):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)
        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        total, lista_productos = repo.listar_productos(
            db, id_empresa, pagina_actual, limite, id_sucursal
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
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)
        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_producto_por_id(db, id, id_empresa)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el producto")

        cambios = json.model_dump(exclude_unset=True)
        if not cambios:
            raise HTTPException(
                status_code=422, detail="Debes enviar al menos un campo para editar"
            )
        for campo, valor in cambios.items():
            if valor is None and campo not in ("id_categoria", "descripcion"):
                raise HTTPException(
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

        db.commit()
        db.refresh(look_up)
        return look_up

    @staticmethod
    def desactivar_producto_service(id: int, id_empresa: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)
        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_producto_por_id(db, id, id_empresa)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el producto")

        look_up.disponible = False
        db.commit()
        db.refresh(look_up)
        return look_up

    @staticmethod
    def importar_productos_service(json, db, id_empresa, id_sucursal):
        from backend.DisponibilidadProductos.tabla import DisponibilidadProductos
        from backend.Sucursales.tabla import Sucursales
        from sqlalchemy import func

        nombres = [item.nombre.casefold() for item in json.productos]
        if len(set(nombres)) != len(nombres):
            raise HTTPException(409, "Hay productos repetidos en el archivo")
        existentes = {
            nombre.casefold()
            for nombre, in db.query(Productos.nombre)
            .filter(Productos.id_empresa == id_empresa)
            .all()
        }
        if existentes.intersection(nombres):
            raise HTTPException(409, "Un producto del archivo ya existe en tu catalogo")
        for item in json.productos:
            if item.id_categoria:
                categoria = repo_categoria.buscar_categoria_por_id(
                    db, item.id_categoria, id_empresa
                )
                if not categoria or not categoria.activo:
                    raise HTTPException(
                        404, "No se encontro la categoria de esta empresa"
                    )
        if json.asignar_sucursal:
            sucursal = (
                db.query(Sucursales)
                .filter(
                    Sucursales.id == id_sucursal,
                    Sucursales.id_empresa == id_empresa,
                    Sucursales.activo.is_(True),
                )
                .first()
            )
            if not sucursal:
                raise HTTPException(404, "No se encontro la sucursal")
        productos = [
            Productos(id_empresa=id_empresa, **item.model_dump())
            for item in json.productos
        ]
        db.add_all(productos)
        db.flush()
        if json.asignar_sucursal:
            db.add_all(
                [
                    DisponibilidadProductos(
                        id_producto=item.id, id_sucursal=id_sucursal, disponible=True
                    )
                    for item in productos
                ]
            )
        respuesta = {"creados": len(productos)}
        db.commit()
        return respuesta

    @staticmethod
    def guardar_imagen_service(json, id, id_empresa, db):
        import base64
        import binascii
        import io
        import warnings
        from pathlib import Path
        from uuid import uuid4
        from PIL import Image, ImageOps, UnidentifiedImageError

        look_up = repo.buscar_producto_por_id(db, id, id_empresa)
        if not look_up:
            raise RecursoNoEncontradoError("No se encontro el producto")
        try:
            contenido = base64.b64decode(json.contenido, validate=True)
            if len(contenido) > 5 * 1024 * 1024:
                raise HTTPException(413, "La imagen supera 5 MB")
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(contenido)) as imagen:
                    if (
                        imagen.format not in ("JPEG", "PNG")
                        or imagen.width * imagen.height > 16_000_000
                    ):
                        raise HTTPException(
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
            raise HTTPException(
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
            db.commit()
        except Exception:
            archivo.unlink(missing_ok=True)
            raise
        if anterior and Path(anterior).name == anterior:
            (carpeta / anterior).unlink(missing_ok=True)
        return look_up

    @staticmethod
    def carpeta_imagenes(id_empresa):
        import os
        from pathlib import Path

        return Path(
            os.environ.get(
                "TURNO_ARCHIVOS", str(Path(__file__).resolve().parents[2] / ".archivos")
            )
        ) / str(id_empresa)

    @staticmethod
    def consultar_imagen_service(id, id_empresa, db, id_sucursal):
        from pathlib import Path

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
