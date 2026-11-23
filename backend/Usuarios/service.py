from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.Categorias.tabla import Categorias
from backend.ConfiguracionImpuestos.tabla import ConfiguracionImpuestos
from backend.Descuentos.tabla import Descuentos
from backend.DisponibilidadProductos.tabla import DisponibilidadProductos
from backend.Empresas.tabla import Empresas
from backend.Mesas.tabla import Mesas
from backend.PagosSucursales.tabla import PagosSucursales
from backend.Productos.tabla import Productos
from backend.RecuperacionesClave.repository import RecuperacionClaveRepository
from backend.ServiciosSucursales.tabla import ServiciosSucursales
from backend.Sesiones.repository import SesionRepository
from backend.Sesiones.schema import RespuestaSesion
from backend.Sesiones.tabla import Sesiones
from backend.Sucursales.tabla import Sucursales
from backend.Suscripciones.service import SuscripcionService
from backend.Suscripciones.tabla import Suscripciones
from backend.Usuarios.repository import UsuarioRepository as repo
from backend.Usuarios.schema import (
    Revisar_Json_Editar_Usuario,
    Revisar_Json_Nuevo_Usuario,
)
from backend.Usuarios.tabla import Usuarios
from backend.Usuarios.verificacion import VerificacionCorreoService
from backend.VinculosLaborales.tabla import VinculosLaborales
from core.config import revision
from core.exceptions import (
    AccesoProhibidoError,
    RecursoDuplicadoError,
    RecursoNoEncontradoError,
    SolicitudError,
)
from utils.hash import encriptar_contrasena
from utils.token import crear_token_sesion, proteger_token_sesion


class UsuarioService:
    @staticmethod
    def crear_usuario_service(json: Revisar_Json_Nuevo_Usuario, db: Session):
        try:
            correo = str(json.correo).lower()
            look_up = repo.buscar_usuario_por_correo(db, correo)

            if look_up is not None:
                raise RecursoDuplicadoError("Ya existe un usuario con ese correo")

            nuevo_usuario = Usuarios(
                correo=correo,
                clave_protegida=encriptar_contrasena(json.clave.get_secret_value()),
                nombre=json.nombre,
            )
            resultado = repo.guardar_nuevo_usuario(db, nuevo_usuario)
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
    def listar_usuarios_service(
        pagina_actual: int, limite: int, db: Session, filtros=None
    ):
        total, lista_usuarios = repo.listar_usuarios(
            db, pagina_actual, limite, filtros=filtros
        )
        total_paginas = (total + limite - 1) // limite

        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": total_paginas,
            "data": lista_usuarios,
        }

    @staticmethod
    def ver_usuario_service(id: int, db: Session):
        look_up = repo.buscar_usuario_por_id(db, id)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el usuario")

        return look_up

    @staticmethod
    def editar_usuario_service(json: Revisar_Json_Editar_Usuario, id: int, db: Session):
        try:
            look_up = repo.buscar_usuario_por_id(db, id)

            if look_up is None:
                raise RecursoNoEncontradoError("No se encontro el usuario")

            cambios = json.model_dump(exclude_unset=True)

            if not cambios:
                raise SolicitudError(
                    status_code=422, detail="Debes enviar al menos un campo para editar"
                )

            for campo, valor in cambios.items():
                if valor is None:
                    raise SolicitudError(
                        status_code=422, detail="El campo " + campo + " no acepta null"
                    )

            if "correo" in cambios:
                cambios["correo"] = str(cambios["correo"]).lower()

                if cambios["correo"] != look_up.correo:
                    raise AccesoProhibidoError(
                        "Confirma el correo nuevo desde Mi cuenta"
                    )

            if cambios.get("estado") is False:
                look_up.fecha_desactivacion_voluntaria = None
                UsuarioService.revisar_ultimo_superadministrador(look_up, db)
                UsuarioService.revocar_accesos_service(id, db)

            for campo, valor in cambios.items():
                setattr(look_up, campo, valor)

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
    def desactivar_usuario_service(id: int, db: Session):
        try:
            look_up = repo.buscar_usuario_por_id(db, id)

            if look_up is None:
                raise RecursoNoEncontradoError("No se encontro el usuario")

            UsuarioService.revisar_ultimo_superadministrador(look_up, db)
            UsuarioService.revocar_accesos_service(id, db)
            look_up.estado = False
            look_up.fecha_desactivacion_voluntaria = None
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
    def cambiar_rol_plataforma_service(json, id, db):
        try:
            look_up = repo.buscar_usuario_por_id(db, id)

            if not look_up:
                raise RecursoNoEncontradoError("No se encontro el usuario")

            if (
                look_up.rol_plataforma == "Superadministrador"
                and json.rol_plataforma != "Superadministrador"
            ):
                UsuarioService.revisar_ultimo_superadministrador(look_up, db)
            look_up.rol_plataforma = json.rol_plataforma

            SesionRepository.revocar_sesiones(
                db, id, datetime.now(timezone.utc).replace(tzinfo=None)
            )
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
    def revisar_ultimo_superadministrador(usuario, db):
        administradores = repo.listar_superadministradores_activos(db)

        if (
            usuario.estado
            and usuario.rol_plataforma == "Superadministrador"
            and len(administradores) <= 1
        ):
            raise RecursoDuplicadoError(
                "La plataforma debe conservar un superadministrador activo"
            )

    @staticmethod
    def revocar_accesos_service(id, db):
        ahora = datetime.now(timezone.utc).replace(tzinfo=None)
        SesionRepository.revocar_sesiones(db, id, ahora)
        RecuperacionClaveRepository.invalidar_codigos(db, id, ahora)
        repo.invalidar_cambios_correo(db, id, ahora)

    @staticmethod
    def registrar_negocio_service(json, db):
        try:

            def validar(condicion, mensaje):
                if not condicion:
                    raise SolicitudError(422, mensaje)

            for lista in (json.categorias, json.productos, json.descuentos):
                valores_unicos = set()

                for item_actual_10 in lista:
                    valores_unicos.add(item_actual_10.nombre.casefold())
                validar(
                    len(valores_unicos) == len(lista),
                    "Hay nombres repetidos en la configuracion",
                )
            valores_unicos_2 = set()

            for item_actual_11 in json.sucursales:
                valores_unicos_2.add(
                    (
                        item_actual_11.nombre.casefold(),
                        item_actual_11.direccion.casefold(),
                    )
                )
            validar(
                len(valores_unicos_2) == len(json.sucursales),
                "Hay sucursales con el mismo nombre y direccion",
            )
            sucursales_locales = set()

            for item_actual_12 in json.sucursales:
                sucursales_locales.add(item_actual_12.id_local)
            categorias_locales = set()

            for item_actual_13 in json.categorias:
                categorias_locales.add(item_actual_13.id_local)
            validar(
                len(sucursales_locales) == len(json.sucursales),
                "Hay sucursales repetidas",
            )
            validar(
                len(categorias_locales) == len(json.categorias),
                "Hay categorias repetidas",
            )
            total_calculado = 0

            for item_actual_2 in json.sucursales:
                total_calculado += item_actual_2.es_principal
            validar(total_calculado == 1, "Selecciona una sucursal principal")

            for sucursal in json.sucursales:
                cumple_condicion = False

                for item_actual_3 in sucursal.servicios.values():
                    if item_actual_3.habilitado:
                        cumple_condicion = True
                        break
                validar(cumple_condicion, "Activa un servicio en cada sucursal")

                for clave, servicio in sucursal.servicios.items():
                    validar(
                        not servicio.mesas_habilitadas
                        or (servicio.habilitado and clave == "comer_aqui"),
                        "Mesas requiere Comer aqui",
                    )
                    validar(
                        not servicio.reservas_habilitadas or servicio.mesas_habilitadas,
                        "Reservas requiere mesas",
                    )

            for producto in json.productos:
                validar(
                    producto.id_categoria is None
                    or producto.id_categoria in categorias_locales,
                    "La categoria del producto no existe en este registro",
                )
                validar(
                    set(producto.sucursales).issubset(sucursales_locales),
                    "La sucursal del producto no existe en este registro",
                )

            for descuento in json.descuentos:
                validar(
                    descuento.tipo_descuento != "Porcentaje" or descuento.valor <= 100,
                    "El descuento no puede superar 100 por ciento",
                )

            correo = str(json.cuenta.correo).lower()
            look_up = repo.buscar_id_por_correo(db, correo)

            if look_up:
                raise RecursoDuplicadoError(
                    "Este correo ya tiene una cuenta. Inicia sesion con ella o usa otro correo"
                )
            look_up = repo.buscar_empresa_para_registro(db, json)

            if look_up:
                raise RecursoDuplicadoError("Ya existe una empresa con ese nombre")
            tipos = {}

            for item_actual in repo.listar_tipos_servicio_activos(db):
                tipos[item_actual.clave_concepto] = item_actual.id
            pagos = {}

            for item_actual_7 in repo.listar_metodos_pago_activos(db):
                pagos[item_actual_7.clave_concepto] = item_actual_7.id

            for sucursal in json.sucursales:
                validar(
                    set(sucursal.servicios).issubset(tipos)
                    and set(sucursal.pagos).issubset(pagos),
                    "Faltan opciones del sistema. Revisa los catalogos de servicios y pagos",
                )

            VerificacionCorreoService.consumir(
                json.cuenta.correo, json.comprobante_correo.get_secret_value(), db
            )
            usuario = Usuarios(
                nombre=json.cuenta.nombre,
                correo=correo,
                clave_protegida=encriptar_contrasena(
                    json.cuenta.clave.get_secret_value()
                ),
            )
            empresa = Empresas(**json.negocio.model_dump())

            try:
                repo.agregar_varios(db, [usuario, empresa])
                repo.guardar_cambios(db)

                repo.agregar(
                    db,
                    Suscripciones(
                        id_empresa=empresa.id,
                        finanzas_habilitadas=json.finanzas_habilitadas,
                    ),
                )
                vinculo = VinculosLaborales(
                    id_usuario=usuario.id,
                    id_empresa=empresa.id,
                    rol="Gerente",
                    activo=True,
                )
                repo.agregar(db, vinculo)
                campos = {}

                for item_actual_8 in json.sucursales:
                    campos[item_actual_8.id_local] = Sucursales(
                        id_empresa=empresa.id,
                        nombre=item_actual_8.nombre,
                        direccion=item_actual_8.direccion,
                        telefono=item_actual_8.telefono,
                        es_principal=item_actual_8.es_principal,
                    )
                sucursales = campos
                campos_2 = {}

                for item_actual_9 in json.categorias:
                    campos_2[item_actual_9.id_local] = Categorias(
                        id_empresa=empresa.id,
                        nombre=item_actual_9.nombre,
                        orden_presentacion=item_actual_9.orden_presentacion,
                    )
                categorias = campos_2
                repo.agregar_varios(
                    db, list(sucursales.values()) + list(categorias.values())
                )
                repo.guardar_cambios(db)

                for item in json.sucursales:
                    cumple_condicion_2 = False

                    for servicio_actual in item.servicios.values():
                        if (
                            servicio_actual.habilitado
                            and servicio_actual.mesas_habilitadas
                        ):
                            cumple_condicion_2 = True
                            break

                    if cumple_condicion_2:
                        elementos = []

                        for numero_actual in range(1, item.cantidad_mesas + 1):
                            elementos.append(
                                Mesas(
                                    id_sucursal=sucursales[item.id_local].id,
                                    nombre=f"Mesa {numero_actual}",
                                )
                            )
                        repo.agregar_varios(db, elementos)

                    for clave, servicio in item.servicios.items():
                        repo.agregar(
                            db,
                            ServiciosSucursales(
                                id_sucursal=sucursales[item.id_local].id,
                                id_tipo_servicio=tipos[clave],
                                **servicio.model_dump(),
                            ),
                        )

                    for clave in set(item.pagos):
                        repo.agregar(
                            db,
                            PagosSucursales(
                                id_sucursal=sucursales[item.id_local].id,
                                id_metodo_pago=pagos[clave],
                                habilitado=True,
                            ),
                        )

                for item in json.descuentos:
                    repo.agregar(
                        db, Descuentos(id_empresa=empresa.id, **item.model_dump())
                    )

                if json.impuesto:
                    repo.agregar(
                        db,
                        ConfiguracionImpuestos(
                            id_empresa=empresa.id, **json.impuesto.model_dump()
                        ),
                    )
                productos = []

                for item in json.productos:
                    producto = Productos(
                        id_empresa=empresa.id,
                        nombre=item.nombre,
                        descripcion=item.descripcion,
                        precio=item.precio,
                        id_categoria=(
                            categorias[item.id_categoria].id
                            if item.id_categoria is not None
                            else None
                        ),
                    )
                    repo.agregar(db, producto)
                    productos.append((producto, item.sucursales))
                repo.guardar_cambios(db)

                for producto, locales in productos:
                    for local in set(locales):
                        repo.agregar(
                            db,
                            DisponibilidadProductos(
                                id_producto=producto.id,
                                id_sucursal=sucursales[local].id,
                                disponible=True,
                            ),
                        )
                ahora = datetime.now(timezone.utc).replace(tzinfo=None)
                vencimiento = ahora + timedelta(hours=revision.SESION_HORAS)
                token = crear_token_sesion()
                registro_encontrado = None

                for item_actual_4 in json.sucursales:
                    if item_actual_4.es_principal:
                        registro_encontrado = sucursales[item_actual_4.id_local]
                        break
                else:
                    raise StopIteration()
                principal = registro_encontrado
                repo.agregar(
                    db,
                    Sesiones(
                        id_usuario=usuario.id,
                        id_vinculo_laboral=vinculo.id,
                        id_sucursal=principal.id,
                        token_protegido=proteger_token_sesion(token),
                        fecha_inicio=ahora,
                        vencimiento=vencimiento,
                    ),
                )
                cumple_condicion_3 = False

                for item_actual_5 in json.sucursales:
                    condicion_verificada = item_actual_5.es_principal

                    if condicion_verificada:
                        cumple_condicion_4 = False

                        for opcion_actual in item_actual_5.servicios.values():
                            if (
                                opcion_actual.habilitado
                                and opcion_actual.mesas_habilitadas
                            ):
                                cumple_condicion_4 = True
                                break
                        condicion_verificada = cumple_condicion_4

                    if condicion_verificada:
                        cumple_condicion_3 = True
                        break
                cumple_condicion_5 = False

                for item_actual_6 in json.sucursales:
                    condicion_verificada_2 = item_actual_6.es_principal

                    if condicion_verificada_2:
                        cumple_condicion_6 = False

                        for opcion_actual_2 in item_actual_6.servicios.values():
                            if (
                                opcion_actual_2.habilitado
                                and opcion_actual_2.reservas_habilitadas
                            ):
                                cumple_condicion_6 = True
                                break
                        condicion_verificada_2 = cumple_condicion_6

                    if condicion_verificada_2:
                        cumple_condicion_5 = True
                        break
                respuesta = RespuestaSesion(
                    usuario=usuario,
                    vencimiento=vencimiento,
                    id_empresa=empresa.id,
                    id_sucursal=principal.id,
                    rol_empresa="Gerente",
                    finanzas_habilitadas=json.finanzas_habilitadas,
                    mesas_habilitadas=cumple_condicion_3,
                    reservas_habilitadas=cumple_condicion_5,
                )

                repo.guardar_cambios(db)
                SuscripcionService.agregar_tarjeta_service(
                    json.tarjeta_suscripcion, db, empresa.id, confirmar=False
                )
                SuscripcionService.crear_comprobante_registro(
                    db, empresa.id, confirmar=False
                )
                repo.guardar_cambios(db)
                db.commit()

                return respuesta, token, vencimiento
            except Exception:
                db.rollback()
                raise
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise
