from utils.hash import encriptar_contrasena
from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.Usuarios.tabla import Usuarios
from backend.Usuarios.repository import UsuarioRepository as repo
from backend.Usuarios.schema import Revisar_Json_Nuevo_Usuario, Revisar_Json_Editar_Usuario
from core.exceptions import RecursoDuplicadoError, RecursoNoEncontradoError


class UsuarioService():

    @staticmethod
    def crear_usuario_service(json: Revisar_Json_Nuevo_Usuario, db: Session):
        correo = str(json.correo).lower()
        look_up = repo.buscar_usuario_por_correo(db, correo)

        if look_up is not None:
            raise RecursoDuplicadoError("Ya existe un usuario con ese correo")

        nuevo_usuario = Usuarios(
            correo=correo,
            clave_protegida=encriptar_contrasena(json.clave.get_secret_value()),
            nombre=json.nombre
        )
        return repo.guardar_nuevo_usuario(db, nuevo_usuario)

    @staticmethod
    def listar_usuarios_service(pagina_actual: int, limite: int, db: Session):
        total, lista_usuarios = repo.listar_usuarios(db, pagina_actual, limite)
        total_paginas = (total + limite - 1) // limite

        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": total_paginas,
            "data": lista_usuarios
        }

    @staticmethod
    def ver_usuario_service(id: int, db: Session):
        look_up = repo.buscar_usuario_por_id(db, id)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el usuario")

        return look_up

    @staticmethod
    def editar_usuario_service(json: Revisar_Json_Editar_Usuario, id: int, db: Session):
        look_up = repo.buscar_usuario_por_id(db, id)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el usuario")

        cambios = json.model_dump(exclude_unset=True)
        if not cambios:
            raise HTTPException(status_code=422, detail="Debes enviar al menos un campo para editar")
        for campo, valor in cambios.items():
            if valor is None:
                raise HTTPException(status_code=422, detail="El campo " + campo + " no acepta null")

        if "correo" in cambios:
            cambios["correo"] = str(cambios["correo"]).lower()
            if cambios["correo"] != look_up.correo:
                usuario_existente = repo.buscar_usuario_por_correo(db, cambios["correo"])
                if usuario_existente is not None:
                    raise RecursoDuplicadoError("Ya existe un usuario con ese correo")

        if cambios.get("estado") is False:
            UsuarioService.revisar_ultimo_superadministrador(look_up, db)
            UsuarioService.revocar_accesos_service(id, db)
        for campo, valor in cambios.items():
            setattr(look_up, campo, valor)

        db.commit()
        db.refresh(look_up)
        return look_up

    @staticmethod
    def desactivar_usuario_service(id: int, db: Session):
        look_up = repo.buscar_usuario_por_id(db, id)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el usuario")

        UsuarioService.revisar_ultimo_superadministrador(look_up, db)
        UsuarioService.revocar_accesos_service(id, db)
        look_up.estado = False
        db.commit()
        db.refresh(look_up)
        return look_up


    @staticmethod
    def cambiar_rol_plataforma_service(json, id, db):
        look_up = repo.buscar_usuario_por_id(db, id)
        if not look_up:
            raise RecursoNoEncontradoError("No se encontro el usuario")
        if look_up.rol_plataforma == "Superadministrador" and json.rol_plataforma != "Superadministrador":
            UsuarioService.revisar_ultimo_superadministrador(look_up, db)
        look_up.rol_plataforma = json.rol_plataforma
        from backend.Sesiones.repository import SesionRepository
        from datetime import datetime, timezone
        SesionRepository.revocar_sesiones(db, id, datetime.now(timezone.utc).replace(tzinfo=None))
        db.commit()
        db.refresh(look_up)
        return look_up

    @staticmethod
    def revisar_ultimo_superadministrador(usuario, db):
        administradores = db.query(Usuarios).filter(
            Usuarios.rol_plataforma == "Superadministrador", Usuarios.estado.is_(True)
        ).order_by(Usuarios.id).with_for_update().all()
        if usuario.estado and usuario.rol_plataforma == "Superadministrador" and len(administradores) <= 1:
            raise HTTPException(409, "La plataforma debe conservar un superadministrador activo")


    @staticmethod
    def revocar_accesos_service(id, db):
        from datetime import datetime, timezone
        from backend.Sesiones.repository import SesionRepository
        from backend.RecuperacionesClave.repository import RecuperacionClaveRepository
        ahora = datetime.now(timezone.utc).replace(tzinfo=None)
        SesionRepository.revocar_sesiones(db, id, ahora)
        RecuperacionClaveRepository.invalidar_codigos(db, id, ahora)

    @staticmethod
    def registrar_negocio_service(json, db):
        from datetime import datetime, timedelta, timezone
        from fastapi import HTTPException
        from backend.Usuarios.tabla import Usuarios
        from backend.Empresas.tabla import Empresas
        from backend.Sucursales.tabla import Sucursales
        from backend.VinculosLaborales.tabla import VinculosLaborales
        from backend.Categorias.tabla import Categorias
        from backend.Productos.tabla import Productos
        from backend.Descuentos.tabla import Descuentos
        from backend.ConfiguracionImpuestos.tabla import ConfiguracionImpuestos
        from backend.TiposServicio.tabla import TiposServicio
        from backend.MetodosPago.tabla import MetodosPago
        from backend.ServiciosSucursales.tabla import ServiciosSucursales
        from backend.PagosSucursales.tabla import PagosSucursales
        from backend.DisponibilidadProductos.tabla import DisponibilidadProductos
        from backend.Sesiones.tabla import Sesiones
        from backend.Sesiones.schema import RespuestaSesion
        from core.config import revision
        from utils.hash import encriptar_contrasena
        from utils.token import crear_token_sesion, proteger_token_sesion
        def validar(condicion, mensaje):
            if not condicion:
                raise HTTPException(422, mensaje)

        for lista in (json.sucursales, json.categorias, json.productos, json.descuentos):
            validar(len({item.nombre.casefold() for item in lista}) == len(lista), "Hay nombres repetidos en la configuracion")
        sucursales_locales = {item.id_local for item in json.sucursales}
        categorias_locales = {item.id_local for item in json.categorias}
        validar(len(sucursales_locales) == len(json.sucursales), "Hay sucursales repetidas")
        validar(len(categorias_locales) == len(json.categorias), "Hay categorias repetidas")
        validar(sum(item.es_principal for item in json.sucursales) == 1, "Selecciona una sucursal principal")
        for sucursal in json.sucursales:
            validar(any(item.habilitado for item in sucursal.servicios.values()), "Activa un servicio en cada sucursal")
            for clave, servicio in sucursal.servicios.items():
                validar(not servicio.mesas_habilitadas or (servicio.habilitado and clave == "comer_aqui"), "Mesas requiere Comer aqui")
                validar(not servicio.reservas_habilitadas or servicio.mesas_habilitadas, "Reservas requiere mesas")
        for producto in json.productos:
            validar(producto.id_categoria is None or producto.id_categoria in categorias_locales, "La categoria del producto no existe en este registro")
            validar(set(producto.sucursales).issubset(sucursales_locales), "La sucursal del producto no existe en este registro")
        for descuento in json.descuentos:
            validar(descuento.tipo_descuento != "Porcentaje" or descuento.valor <= 100, "El descuento no puede superar 100 por ciento")

        correo = str(json.cuenta.correo).lower()
        look_up = db.query(Usuarios.id).filter(Usuarios.correo == correo).first()
        if look_up:
            raise HTTPException(409, "Este correo ya tiene una cuenta. Inicia sesion con ella o usa otro correo")
        look_up = db.query(Empresas.id).filter(Empresas.nombre == json.negocio.nombre).first()
        if look_up:
            raise HTTPException(409, "Ya existe una empresa con ese nombre")
        tipos = {item.clave_concepto: item.id for item in db.query(TiposServicio).filter(TiposServicio.activo.is_(True)).all()}
        pagos = {item.clave_concepto: item.id for item in db.query(MetodosPago).filter(MetodosPago.activo.is_(True)).all()}
        for sucursal in json.sucursales:
            validar(set(sucursal.servicios).issubset(tipos) and set(sucursal.pagos).issubset(pagos), "Faltan opciones del sistema. Revisa los catalogos de servicios y pagos")

        usuario = Usuarios(nombre=json.cuenta.nombre, correo=correo, clave_protegida=encriptar_contrasena(json.cuenta.clave.get_secret_value()))
        empresa = Empresas(**json.negocio.model_dump())
        try:
            db.add_all([usuario, empresa])
            db.flush()
            from backend.Suscripciones.tabla import Suscripciones
            db.add(Suscripciones(id_empresa=empresa.id, finanzas_habilitadas=json.finanzas_habilitadas))
            vinculo = VinculosLaborales(id_usuario=usuario.id, id_empresa=empresa.id, rol="Gerente", activo=True)
            db.add(vinculo)
            sucursales = {item.id_local: Sucursales(id_empresa=empresa.id, nombre=item.nombre, direccion=item.direccion, telefono=item.telefono, es_principal=item.es_principal) for item in json.sucursales}
            categorias = {item.id_local: Categorias(id_empresa=empresa.id, nombre=item.nombre, orden_presentacion=item.orden_presentacion) for item in json.categorias}
            db.add_all(list(sucursales.values()) + list(categorias.values()))
            db.flush()
            for item in json.sucursales:
                for clave, servicio in item.servicios.items():
                    db.add(ServiciosSucursales(id_sucursal=sucursales[item.id_local].id, id_tipo_servicio=tipos[clave], **servicio.model_dump()))
                for clave in set(item.pagos):
                    db.add(PagosSucursales(id_sucursal=sucursales[item.id_local].id, id_metodo_pago=pagos[clave], habilitado=True))
            for item in json.descuentos:
                db.add(Descuentos(id_empresa=empresa.id, **item.model_dump()))
            if json.impuesto:
                db.add(ConfiguracionImpuestos(id_empresa=empresa.id, **json.impuesto.model_dump()))
            productos = []
            for item in json.productos:
                producto = Productos(id_empresa=empresa.id, nombre=item.nombre, descripcion=item.descripcion, precio=item.precio, id_categoria=categorias[item.id_categoria].id if item.id_categoria is not None else None)
                db.add(producto)
                productos.append((producto, item.sucursales))
            db.flush()
            for producto, locales in productos:
                for local in set(locales):
                    db.add(DisponibilidadProductos(id_producto=producto.id, id_sucursal=sucursales[local].id, disponible=True))
            ahora = datetime.now(timezone.utc).replace(tzinfo=None)
            vencimiento = ahora + timedelta(hours=revision.SESION_HORAS)
            token = crear_token_sesion()
            principal = next(sucursales[item.id_local] for item in json.sucursales if item.es_principal)
            db.add(Sesiones(id_usuario=usuario.id, id_vinculo_laboral=vinculo.id, id_sucursal=principal.id, token_protegido=proteger_token_sesion(token), fecha_inicio=ahora, vencimiento=vencimiento))
            respuesta = RespuestaSesion(usuario=usuario, vencimiento=vencimiento, id_empresa=empresa.id, id_sucursal=principal.id, rol_empresa="Gerente", finanzas_habilitadas=json.finanzas_habilitadas, mesas_habilitadas=any(item.es_principal and any(opcion.habilitado and opcion.mesas_habilitadas for opcion in item.servicios.values()) for item in json.sucursales), reservas_habilitadas=any(item.es_principal and any(opcion.habilitado and opcion.reservas_habilitadas for opcion in item.servicios.values()) for item in json.sucursales))
            db.commit()
            return respuesta, token, vencimiento
        except Exception:
            db.rollback()
            raise
