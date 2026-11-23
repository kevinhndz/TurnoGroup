from datetime import timedelta
from decimal import Decimal

from sqlalchemy.exc import SQLAlchemyError

from backend.RecuperacionesClave.repository import RecuperacionClaveRepository
from backend.Sesiones.repository import SesionRepository
from backend.Suscripciones.proveedor import datos_tarjeta_prueba, exigir_simulacion
from backend.Suscripciones.repository import SuscripcionRepository as repo
from backend.Suscripciones.tabla import ComprobantesSuscripcion, TarjetasSuscripcion
from backend.Usuarios.repository import UsuarioRepository
from core.operaciones import ahora, exigir
from core.config import revision
from utils.hash import verificar_contrasena


class SuscripcionService:
    @staticmethod
    def vigente(suscripcion):
        return bool(
            suscripcion
            and (
                (suscripcion.estado == "Prueba" and suscripcion.fin_prueba > ahora())
                or (
                    suscripcion.estado == "Activa"
                    and suscripcion.proximo_cobro
                    and suscripcion.proximo_cobro > ahora()
                )
            )
        )

    @staticmethod
    def consultar_service(db, id_empresa):
        look_up = repo.buscar_suscripcion(db, id_empresa)
        exigir(look_up is not None, "No se encontro la suscripcion", 404)
        locales = repo.contar_sucursales(db, id_empresa)
        elementos = []

        for item_actual_9 in repo.tarjetas(db, id_empresa):
            elementos.append(SuscripcionService.respuesta_tarjeta(item_actual_9))
        elementos_2 = []

        for item_actual_10 in repo.comprobantes(db, id_empresa):
            elementos_2.append(SuscripcionService.respuesta_comprobante(item_actual_10))
        cumple_condicion = False

        for item_actual_2 in repo.comprobantes(db, id_empresa):
            if item_actual_2.importe > 0:
                cumple_condicion = True
                break

        return {
            "id": look_up.id,
            "estado": (
                look_up.estado if SuscripcionService.vigente(look_up) else "Vencida"
            ),
            "inicio_prueba": look_up.inicio_prueba,
            "fin_prueba": look_up.fin_prueba,
            "proximo_cobro": look_up.proximo_cobro,
            "finanzas_habilitadas": look_up.finanzas_habilitadas,
            "sucursales_activas": locales,
            "precio_por_sucursal_usd": "100.00",
            "complemento_finanzas_usd": (
                "30.00" if look_up.finanzas_habilitadas else "0.00"
            ),
            "total_mensual_usd": str(
                locales * 100 + (30 if look_up.finanzas_habilitadas else 0)
            ),
            "proveedor": "Paddle",
            "modo": "simulado" if not look_up.id_suscripcion_paddle else "paddle",
            "simulacion_local": (
                revision.ENTORNO in ("desarrollo", "pruebas")
                and revision.FACTURACION_MODO == "simulado"
                and not look_up.id_suscripcion_paddle
            ),
            "mensualidad_pagada": cumple_condicion,
            "renovacion_automatica": look_up.renovacion_automatica,
            "tarjetas": elementos,
            "comprobantes": elementos_2,
        }

    @staticmethod
    def renovar_prueba_service(db, id_empresa):
        try:
            exigir(
                revision.ENTORNO in ("desarrollo", "pruebas"),
                "Esta opcion solo esta disponible en desarrollo y pruebas",
                403,
            )
            suscripcion = SuscripcionService.bloquear_simulado(db, id_empresa)
            exigir(
                suscripcion.estado in ("Prueba", "Activa"),
                "Esta suscripcion no permite ampliar el periodo de prueba",
                409,
            )
            instante = ahora()

            if suscripcion.estado == "Prueba":
                fin_actual = suscripcion.fin_prueba or instante
                suscripcion.fin_prueba = max(fin_actual, instante) + timedelta(days=30)
            else:
                fin_actual = suscripcion.proximo_cobro or instante
                suscripcion.proximo_cobro = max(fin_actual, instante) + timedelta(
                    days=30
                )

            repo.guardar_cambios(db)
            db.commit()

            return SuscripcionService.consultar_service(db, id_empresa)
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def cambiar_plan_service(json, db, id_empresa):
        try:
            look_up = repo.buscar_suscripcion(db, id_empresa, True)
            exigir(look_up is not None, "No se encontro la suscripcion", 404)
            exigir(
                look_up.estado == "Prueba" and look_up.fin_prueba > ahora(),
                "Los cambios de un plan de pago requieren la integracion de Paddle",
                409,
            )
            look_up.finanzas_habilitadas = json.finanzas_habilitadas
            repo.guardar_cambios(db)
            db.commit()

            return SuscripcionService.consultar_service(db, id_empresa)
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def exigir_finanzas(db, id_empresa):
        look_up = repo.buscar_suscripcion(db, id_empresa)
        exigir(
            SuscripcionService.vigente(look_up) and look_up.finanzas_habilitadas,
            "El modulo Finanzas no esta habilitado en tu plan",
            403,
        )

    @staticmethod
    def respuesta_tarjeta(item):
        campos = {}

        for campo_actual in (
            "id",
            "titular",
            "marca",
            "ultimos_cuatro",
            "mes",
            "anio",
            "prioridad",
            "modo",
        ):
            campos[campo_actual] = getattr(item, campo_actual)

        return campos

    @staticmethod
    def respuesta_comprobante(item):
        campos_2 = {}

        for campo_actual_2 in (
            "id",
            "concepto",
            "fecha",
            "periodo_inicio",
            "periodo_fin",
            "importe",
            "moneda",
            "modo",
            "detalle",
        ):
            campos_2[campo_actual_2] = getattr(item, campo_actual_2)

        return campos_2

    @staticmethod
    def bloquear_simulado(db, id_empresa):
        exigir_simulacion()
        look_up = repo.buscar_suscripcion(db, id_empresa, True)
        exigir(look_up is not None, "No se encontro la suscripcion", 404)
        exigir(
            not look_up.id_suscripcion_paddle,
            "Esta suscripcion se administra con su proveedor",
            409,
        )

        return look_up

    @staticmethod
    def agregar_tarjeta_service(json, db, id_empresa, confirmar=True):
        try:
            SuscripcionService.bloquear_simulado(db, id_empresa)
            tarjetas = repo.tarjetas(db, id_empresa)
            exigir(len(tarjetas) < 5, "Puedes guardar hasta cinco tarjetas", 409)
            marca, ultimos = datos_tarjeta_prueba(json.tarjeta_prueba)
            cumple_condicion_2 = False

            for item_actual_3 in tarjetas:
                if (
                    item_actual_3.marca == marca
                    and item_actual_3.ultimos_cuatro == ultimos
                    and (item_actual_3.mes == json.mes)
                    and (item_actual_3.anio == json.anio)
                    and (item_actual_3.titular.casefold() == json.titular.casefold())
                ):
                    cumple_condicion_2 = True
                    break
            exigir(not cumple_condicion_2, "Esta tarjeta ya esta registrada", 409)
            nueva_tarjeta = TarjetasSuscripcion(
                id_empresa=id_empresa,
                titular=json.titular,
                marca=marca,
                ultimos_cuatro=ultimos,
                mes=json.mes,
                anio=json.anio,
                prioridad="Principal" if not tarjetas else "Adicional",
                modo="simulado",
            )
            repo.agregar(db, nueva_tarjeta)
            repo.guardar_cambios(db)
            respuesta = SuscripcionService.respuesta_tarjeta(nueva_tarjeta)

            if confirmar:
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
    def prioridad_service(id, prioridad, db, id_empresa):
        try:
            SuscripcionService.bloquear_simulado(db, id_empresa)
            look_up = repo.buscar_tarjeta(db, id_empresa, id)
            exigir(look_up is not None, "No se encontro la tarjeta", 404)
            exigir(
                (look_up.anio, look_up.mes) >= (ahora().year, ahora().month),
                "La tarjeta esta vencida",
                409,
            )
            tarjetas = repo.tarjetas(db, id_empresa)

            if prioridad == "Secundaria":
                exigir(
                    look_up.prioridad != "Principal",
                    "Selecciona otra principal antes de asignar esta como secundaria",
                    409,
                )

            for item in tarjetas:
                if item.prioridad == prioridad:
                    item.prioridad = "Adicional"
            look_up.prioridad = prioridad
            repo.guardar_cambios(db)
            db.commit()

            return SuscripcionService.respuesta_tarjeta(look_up)
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def retirar_tarjeta_service(id, db, id_empresa):
        try:
            suscripcion = SuscripcionService.bloquear_simulado(db, id_empresa)
            look_up = repo.buscar_tarjeta(db, id_empresa, id)
            exigir(look_up is not None, "No se encontro la tarjeta", 404)
            alternativas = []

            for item_actual in repo.tarjetas(db, id_empresa):
                if item_actual.id != id and (item_actual.anio, item_actual.mes) >= (
                    ahora().year,
                    ahora().month,
                ):
                    alternativas.append(item_actual)
            exigir(
                look_up.prioridad != "Principal"
                or alternativas
                or not suscripcion.renovacion_automatica,
                "Agrega otra tarjeta o cancela la renovacion antes de retirar la principal",
                409,
            )

            if look_up.prioridad == "Principal" and alternativas:
                registro_encontrado = alternativas[0]

                for item_actual_4 in alternativas:
                    if item_actual_4.prioridad == "Secundaria":
                        registro_encontrado = item_actual_4
                        break
                nueva = registro_encontrado
                nueva.prioridad = "Principal"
            look_up.activo = False
            repo.guardar_cambios(db)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def renovacion_service(json, db, id_empresa):
        try:
            look_up = SuscripcionService.bloquear_simulado(db, id_empresa)

            if json.renovacion_automatica:
                cumple_condicion_3 = False

                for item_actual_5 in repo.tarjetas(db, id_empresa):
                    if item_actual_5.prioridad == "Principal" and (
                        item_actual_5.anio,
                        item_actual_5.mes,
                    ) >= (ahora().year, ahora().month):
                        cumple_condicion_3 = True
                        break
                exigir(cumple_condicion_3, "Agrega una tarjeta principal vigente", 409)
            look_up.renovacion_automatica = json.renovacion_automatica
            repo.guardar_cambios(db)
            db.commit()

            return SuscripcionService.consultar_service(db, id_empresa)
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def crear_comprobante_registro(db, id_empresa, confirmar=True):
        try:
            suscripcion = SuscripcionService.bloquear_simulado(db, id_empresa)
            registro_encontrado_2 = None

            for item_actual_6 in repo.comprobantes(db, id_empresa):
                if item_actual_6.concepto == "Registro y primer mes de prueba":
                    registro_encontrado_2 = item_actual_6
                    break
            look_up = registro_encontrado_2

            if not look_up:
                empresa = repo.buscar_empresa(db, id_empresa)
                locales = repo.contar_sucursales(db, id_empresa)
                mensual = locales * 100 + (
                    30 if suscripcion.finanzas_habilitadas else 0
                )
                look_up = ComprobantesSuscripcion(
                    id_empresa=id_empresa,
                    concepto="Registro y primer mes de prueba",
                    nombre_empresa=empresa.nombre,
                    fecha=suscripcion.inicio_prueba,
                    periodo_inicio=suscripcion.inicio_prueba,
                    periodo_fin=suscripcion.fin_prueba,
                    importe=Decimal("0.00"),
                    moneda="USD",
                    modo="simulado",
                    detalle=f"{locales} sucursales. Plan mensual de referencia: {mensual} USD. Primer mes gratuito. Sin cargos realizados.",
                )
                repo.agregar(db, look_up)
                repo.guardar_cambios(db)
            respuesta = SuscripcionService.respuesta_comprobante(look_up)

            if confirmar:
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
    def desactivar_cuenta_service(json, db, contexto):
        try:
            exigir(contexto["rol"] == "Gerente", "No estas autorizado", 403)
            usuario = repo.buscar_usuario_para_desactivar(db, contexto)
            exigir(
                usuario.clave_protegida
                and verificar_contrasena(
                    json.clave.get_secret_value(), usuario.clave_protegida
                ),
                "La clave no es correcta",
                403,
            )
            valores_unicos = set()

            for item_actual_8 in repo.listar_empresas_del_gerente(db, usuario):
                valores_unicos.add(item_actual_8.id_empresa)
            empresas = sorted(valores_unicos)
            suscripciones = []

            for empresa_actual in empresas:
                suscripciones.append(
                    SuscripcionService.bloquear_simulado(db, empresa_actual)
                )

            for empresa, suscripcion in zip(empresas, suscripciones):
                exigir(
                    SuscripcionService.vigente(suscripcion),
                    "Debes estar al dia con la suscripcion para desactivar tu cuenta",
                    409,
                )
                cumple_condicion_4 = False

                for item_actual_7 in repo.comprobantes(db, empresa):
                    if item_actual_7.importe > 0:
                        cumple_condicion_4 = True
                        break
                exigir(
                    cumple_condicion_4,
                    "Debes haber pagado al menos una mensualidad antes de desactivar tu cuenta",
                    409,
                )

            for item in suscripciones:
                item.renovacion_automatica = False
            usuario.estado = False
            usuario.fecha_desactivacion_voluntaria = ahora()
            SesionRepository.revocar_sesiones(db, usuario.id, ahora())
            RecuperacionClaveRepository.invalidar_codigos(db, usuario.id, ahora())

            UsuarioRepository.invalidar_cambios_correo(db, usuario.id, ahora())
            repo.guardar_cambios(db)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise
