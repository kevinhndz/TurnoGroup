from backend.Suscripciones.repository import SuscripcionRepository as repo
from core.operaciones import ahora, exigir
from backend.Suscripciones.tabla import TarjetasSuscripcion, ComprobantesSuscripcion
from backend.Suscripciones.proveedor import datos_tarjeta_prueba, exigir_simulacion
from backend.Empresas.tabla import Empresas
from decimal import Decimal


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
            "mensualidad_pagada": any(item.importe > 0 for item in repo.comprobantes(db, id_empresa)),
            "renovacion_automatica": look_up.renovacion_automatica,
            "tarjetas": [SuscripcionService.respuesta_tarjeta(item) for item in repo.tarjetas(db, id_empresa)],
            "comprobantes": [SuscripcionService.respuesta_comprobante(item) for item in repo.comprobantes(db, id_empresa)],
        }

    @staticmethod
    def cambiar_plan_service(json, db, id_empresa):
        look_up = repo.buscar_suscripcion(db, id_empresa, True)
        exigir(look_up is not None, "No se encontro la suscripcion", 404)
        exigir(
            look_up.estado == "Prueba" and look_up.fin_prueba > ahora(),
            "Los cambios de un plan de pago requieren la integracion de Paddle",
            409,
        )
        look_up.finanzas_habilitadas = json.finanzas_habilitadas
        db.commit()
        return SuscripcionService.consultar_service(db, id_empresa)

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
        return {campo: getattr(item, campo) for campo in ("id", "titular", "marca", "ultimos_cuatro", "mes", "anio", "prioridad", "modo")}

    @staticmethod
    def respuesta_comprobante(item):
        return {campo: getattr(item, campo) for campo in ("id", "concepto", "fecha", "periodo_inicio", "periodo_fin", "importe", "moneda", "modo", "detalle")}

    @staticmethod
    def bloquear_simulado(db, id_empresa):
        exigir_simulacion()
        look_up = repo.buscar_suscripcion(db, id_empresa, True)
        exigir(look_up is not None, "No se encontro la suscripcion", 404)
        exigir(not look_up.id_suscripcion_paddle, "Esta suscripcion se administra con su proveedor", 409)
        return look_up

    @staticmethod
    def agregar_tarjeta_service(json, db, id_empresa, confirmar=True):
        SuscripcionService.bloquear_simulado(db, id_empresa)
        tarjetas = repo.tarjetas(db, id_empresa)
        exigir(len(tarjetas) < 5, "Puedes guardar hasta cinco tarjetas", 409)
        marca, ultimos = datos_tarjeta_prueba(json.tarjeta_prueba)
        exigir(not any(item.marca == marca and item.ultimos_cuatro == ultimos and item.mes == json.mes and item.anio == json.anio and item.titular.casefold() == json.titular.casefold() for item in tarjetas), "Esta tarjeta ya esta registrada", 409)
        nueva_tarjeta = TarjetasSuscripcion(id_empresa=id_empresa, titular=json.titular, marca=marca, ultimos_cuatro=ultimos, mes=json.mes, anio=json.anio, prioridad="Principal" if not tarjetas else "Adicional", modo="simulado")
        db.add(nueva_tarjeta)
        db.flush()
        respuesta = SuscripcionService.respuesta_tarjeta(nueva_tarjeta)
        if confirmar:
            db.commit()
        return respuesta

    @staticmethod
    def prioridad_service(id, prioridad, db, id_empresa):
        SuscripcionService.bloquear_simulado(db, id_empresa)
        look_up = repo.buscar_tarjeta(db, id_empresa, id)
        exigir(look_up is not None, "No se encontro la tarjeta", 404)
        exigir((look_up.anio, look_up.mes) >= (ahora().year, ahora().month), "La tarjeta esta vencida", 409)
        tarjetas = repo.tarjetas(db, id_empresa)
        if prioridad == "Secundaria":
            exigir(look_up.prioridad != "Principal", "Selecciona otra principal antes de asignar esta como secundaria", 409)
        for item in tarjetas:
            if item.prioridad == prioridad:
                item.prioridad = "Adicional"
        look_up.prioridad = prioridad
        db.commit()
        return SuscripcionService.respuesta_tarjeta(look_up)

    @staticmethod
    def retirar_tarjeta_service(id, db, id_empresa):
        suscripcion = SuscripcionService.bloquear_simulado(db, id_empresa)
        look_up = repo.buscar_tarjeta(db, id_empresa, id)
        exigir(look_up is not None, "No se encontro la tarjeta", 404)
        alternativas = [item for item in repo.tarjetas(db, id_empresa) if item.id != id and (item.anio, item.mes) >= (ahora().year, ahora().month)]
        exigir(look_up.prioridad != "Principal" or alternativas or not suscripcion.renovacion_automatica, "Agrega otra tarjeta o cancela la renovacion antes de retirar la principal", 409)
        if look_up.prioridad == "Principal" and alternativas:
            nueva = next((item for item in alternativas if item.prioridad == "Secundaria"), alternativas[0])
            nueva.prioridad = "Principal"
        look_up.activo = False
        db.commit()

    @staticmethod
    def renovacion_service(json, db, id_empresa):
        look_up = SuscripcionService.bloquear_simulado(db, id_empresa)
        if json.renovacion_automatica:
            exigir(any(item.prioridad == "Principal" and (item.anio, item.mes) >= (ahora().year, ahora().month) for item in repo.tarjetas(db, id_empresa)), "Agrega una tarjeta principal vigente", 409)
        look_up.renovacion_automatica = json.renovacion_automatica
        db.commit()
        return SuscripcionService.consultar_service(db, id_empresa)

    @staticmethod
    def crear_comprobante_registro(db, id_empresa, confirmar=True):
        suscripcion = SuscripcionService.bloquear_simulado(db, id_empresa)
        look_up = next((item for item in repo.comprobantes(db, id_empresa) if item.concepto == "Registro y primer mes de prueba"), None)
        if not look_up:
            empresa = db.get(Empresas, id_empresa)
            locales = repo.contar_sucursales(db, id_empresa)
            mensual = locales * 100 + (30 if suscripcion.finanzas_habilitadas else 0)
            look_up = ComprobantesSuscripcion(id_empresa=id_empresa, concepto="Registro y primer mes de prueba", nombre_empresa=empresa.nombre, fecha=suscripcion.inicio_prueba, periodo_inicio=suscripcion.inicio_prueba, periodo_fin=suscripcion.fin_prueba, importe=Decimal("0.00"), moneda="USD", modo="simulado", detalle=f"{locales} sucursales. Plan mensual de referencia: {mensual} USD. Primer mes gratuito. Sin cargos realizados.")
            db.add(look_up)
            db.flush()
        respuesta = SuscripcionService.respuesta_comprobante(look_up)
        if confirmar:
            db.commit()
        return respuesta

    @staticmethod
    def desactivar_cuenta_service(json, db, contexto):
        from backend.VinculosLaborales.tabla import VinculosLaborales
        from backend.Usuarios.tabla import Usuarios
        from backend.Sesiones.repository import SesionRepository
        from backend.RecuperacionesClave.repository import RecuperacionClaveRepository
        from utils.hash import verificar_contrasena

        exigir(contexto["rol"] == "Gerente", "No estas autorizado", 403)
        usuario = db.query(Usuarios).filter_by(id=contexto["usuario"].id).with_for_update().one()
        exigir(usuario.clave_protegida and verificar_contrasena(json.clave.get_secret_value(), usuario.clave_protegida), "La clave no es correcta", 403)
        empresas = sorted({item.id_empresa for item in db.query(VinculosLaborales).filter_by(id_usuario=usuario.id, rol="Gerente", activo=True).all()})
        suscripciones = [SuscripcionService.bloquear_simulado(db, empresa) for empresa in empresas]
        for empresa, suscripcion in zip(empresas, suscripciones):
            exigir(SuscripcionService.vigente(suscripcion), "Debes estar al dia con la suscripcion para desactivar tu cuenta", 409)
            exigir(any(item.importe > 0 for item in repo.comprobantes(db, empresa)), "Debes haber pagado al menos una mensualidad antes de desactivar tu cuenta", 409)
        for item in suscripciones:
            item.renovacion_automatica = False
        usuario.estado = False
        usuario.fecha_desactivacion_voluntaria = ahora()
        SesionRepository.revocar_sesiones(db, usuario.id, ahora())
        RecuperacionClaveRepository.invalidar_codigos(db, usuario.id, ahora())
        db.commit()
