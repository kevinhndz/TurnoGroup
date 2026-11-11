from datetime import datetime, timedelta, timezone
from uuid import uuid4
import pytest
from backend.Productos.tabla import Productos
from backend.DisponibilidadProductos.tabla import DisponibilidadProductos
from backend.ServiciosSucursales.tabla import ServiciosSucursales
from backend.PagosSucursales.tabla import PagosSucursales
from backend.TiposServicio.tabla import TiposServicio
from backend.MetodosPago.tabla import MetodosPago
from backend.Mesas.tabla import Mesas
from backend.ConfiguracionImpuestos.tabla import ConfiguracionImpuestos
from backend.Descuentos.tabla import Descuentos
from backend.Suscripciones.tabla import Suscripciones
from tests.test_roles_empresas import usar_rol


@pytest.fixture
def operacion(db, datos):
    servicio = db.query(TiposServicio).filter_by(clave_concepto="comer_aqui").one()
    pago = db.query(MetodosPago).filter_by(clave_concepto="efectivo").one()
    mesa = Mesas(id_sucursal=datos["sucursal"], nombre="Mesa uno", capacidad=4)
    db.add_all(
        [
            mesa,
            ServiciosSucursales(
                id_sucursal=datos["sucursal"],
                id_tipo_servicio=servicio.id,
                habilitado=True,
                mesas_habilitadas=True,
                reservas_habilitadas=True,
            ),
            PagosSucursales(
                id_sucursal=datos["sucursal"], id_metodo_pago=pago.id, habilitado=True
            ),
            DisponibilidadProductos(
                id_sucursal=datos["sucursal"],
                id_producto=datos["producto"],
                disponible=True,
            ),
        ]
    )
    db.query(Suscripciones).filter_by(
        id_empresa=datos["empresa"]
    ).one().finanzas_habilitadas = True
    db.commit()
    return {"mesa": mesa.id, "servicio": servicio.id, "pago": pago.id}


def pedido(datos, operacion, **extra):
    return {
        "clave_operacion": str(uuid4()),
        "id_tipo_servicio": operacion["servicio"],
        "id_metodo_pago": operacion["pago"],
        "cliente": "Cliente de prueba",
        "telefono": "9999-1234",
        "detalles": [{"id_producto": datos["producto"], "cantidad": 2}],
        **extra,
    }


def abrir_caja(client, db, datos):
    usar_rol(client, db, datos, "Mesero")
    respuesta = client.post("/cajas/", json={"monto_inicial": "100.00"})
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()["id"]


def test_pedido_importes_y_doble_envio(client, db, datos, operacion):
    cuerpo = pedido(datos, operacion)
    cotizacion = client.post(
        "/pedidos/cotizar",
        json={k: v for k, v in cuerpo.items() if k != "clave_operacion"},
    )
    assert cotizacion.status_code == 200, cotizacion.text
    assert float(cotizacion.json()["total"]) == 150
    primera = client.post("/pedidos/", json=cuerpo)
    assert primera.status_code == 201, primera.text
    segunda = client.post("/pedidos/", json=cuerpo)
    assert segunda.json()["id"] == primera.json()["id"]
    cuerpo["detalles"][0]["cantidad"] = 3
    assert client.post("/pedidos/", json=cuerpo).status_code == 409
    assert client.get("/pedidos/").json()["total"] == 1


def test_pago_y_entrega_cierran_pedido_sin_caja(client, db, datos, operacion):
    id = client.post("/pedidos/", json=pedido(datos, operacion)).json()["id"]
    assert client.post(f"/pedidos/{id}/entregar").json()["estado"] == "Abierto"
    cobrado = client.post(
        f"/pedidos/{id}/cobrar", json={"id_metodo_pago": operacion["pago"]}
    )
    assert cobrado.status_code == 200, cobrado.text
    assert cobrado.json()["estado"] == "Cerrado"
    assert (
        client.post(
            f"/pedidos/{id}/cobrar", json={"id_metodo_pago": operacion["pago"]}
        ).status_code
        == 409
    )


@pytest.mark.parametrize("rol", ["Gerente", "Administrador", "Mesero"])
def test_cobro_cierra_sin_entrega_para_cada_rol(client, db, datos, operacion, rol):
    usar_rol(client, db, datos, rol)
    creado = client.post("/pedidos/", json=pedido(datos, operacion, cobrado=True))
    assert creado.status_code == 201, creado.text
    assert creado.json()["estado"] == "Cerrado"
    assert creado.json()["fecha_entrega"] is None
    pendiente = client.post("/pedidos/", json=pedido(datos, operacion)).json()
    assert pendiente["estado"] == "Abierto"
    cobrado = client.post(f'/pedidos/{pendiente["id"]}/cobrar', json={"id_metodo_pago": operacion["pago"]})
    assert cobrado.status_code == 200, cobrado.text
    assert cobrado.json()["estado"] == "Cerrado"
    assert cobrado.json()["fecha_entrega"] is None
    assert client.post(f'/pedidos/{pendiente["id"]}/cobrar', json={"id_metodo_pago": operacion["pago"]}).status_code == 409


@pytest.mark.parametrize("campo", ["cliente", "telefono"])
@pytest.mark.parametrize("valor", [None, "", "   "])
def test_pedido_requiere_nombre_y_telefono(client, db, datos, operacion, campo, valor):
    assert client.post("/pedidos/", json=pedido(datos, operacion, **{campo: valor})).status_code == 422
    assert client.get("/pedidos/").json()["total"] == 0


def test_cobro_sin_caja_y_permisos_de_roles(client, db, datos, operacion):
    assert (
        client.post(
            "/pedidos/", json=pedido(datos, operacion, cobrado=True)
        ).status_code
        == 201
    )
    assert client.get("/pedidos/").json()["total"] == 1
    usar_rol(client, db, datos, "Mesero")
    assert client.get("/cajas/").status_code == 200
    assert (
        client.get(
            "/finanzas/ventas", params={"desde": "2026-01-01", "hasta": "2026-12-31"}
        ).status_code
        == 403
    )
    assert client.get("/suscripciones/actual").status_code == 403


def test_cancelar_conserva_historial_y_libera_mesa(client, db, datos, operacion):
    cuerpo = pedido(datos, operacion, id_mesa=operacion["mesa"])
    creado = client.post("/pedidos/", json=cuerpo).json()
    assert (
        client.post(
            "/pedidos/", json=pedido(datos, operacion, id_mesa=operacion["mesa"])
        ).status_code
        == 409
    )
    assert (
        client.post(
            f'/pedidos/{creado["id"]}/cancelar',
            json={"motivo": "Cliente no desea continuar"},
        ).json()["estado"]
        == "Cancelado"
    )
    assert client.get(f'/pedidos/{creado["id"]}').status_code == 200
    assert (
        client.post(
            "/pedidos/", json=pedido(datos, operacion, id_mesa=operacion["mesa"])
        ).status_code
        == 201
    )


def test_producto_externo_no_se_registra(client, datos, operacion):
    cuerpo = pedido(datos, operacion)
    cuerpo["detalles"][0]["id_producto"] = datos["otro_producto"]
    assert client.post("/pedidos/", json=cuerpo).status_code == 409
    assert client.get("/pedidos/").json()["total"] == 0


def test_precio_cambio_requiere_confirmar_y_congela_detalles(
    client, db, datos, operacion
):
    cuerpo = pedido(datos, operacion, total_esperado="140.00")
    assert client.post("/pedidos/", json=cuerpo).status_code == 409
    cuerpo["total_esperado"] = "150.00"
    creado = client.post("/pedidos/", json=cuerpo).json()
    db.get(Productos, datos["producto"]).precio = 999
    db.commit()
    assert float(client.get(f'/pedidos/{creado["id"]}').json()["total"]) == 150


def test_impuesto_incluido_y_descuento(client, db, datos, operacion):
    descuento = Descuentos(
        id_empresa=datos["empresa"],
        nombre="Cortesia",
        tipo_descuento="Porcentaje",
        valor=10,
    )
    db.add_all(
        [
            descuento,
            ConfiguracionImpuestos(
                id_empresa=datos["empresa"],
                porcentaje=15,
                precios_incluyen_impuesto=True,
            ),
        ]
    )
    db.commit()
    cuerpo = pedido(datos, operacion, id_descuento=descuento.id)
    cotizacion = client.post(
        "/pedidos/cotizar",
        json={k: v for k, v in cuerpo.items() if k != "clave_operacion"},
    ).json()
    assert float(cotizacion["total"]) == 135
    assert float(cotizacion["descuento"]) == 15
    assert float(cotizacion["impuesto"]) == 17.61


def test_reservas_capacidad_horario_y_cruces(client, operacion):
    inicio = datetime.now(timezone.utc) + timedelta(days=2)
    cuerpo = {
        "id_mesa": operacion["mesa"],
        "cliente": "Persona prueba",
        "personas": 2,
        "inicio": inicio.isoformat(),
        "fin": (inicio + timedelta(hours=1)).isoformat(),
    }
    creada = client.post("/reservas/", json=cuerpo)
    assert creada.status_code == 201, creada.text
    assert client.post("/reservas/", json=cuerpo).status_code == 409
    assert client.post("/reservas/", json={**cuerpo, "personas": 99}).status_code == 422
    assert client.post(f'/reservas/{creada.json()["id"]}/cancelar').status_code == 200
    assert client.post("/reservas/", json=cuerpo).status_code == 201


def test_finanzas_ventas_y_habilitacion(client, db, datos, operacion):
    assert (
        client.post(
            "/pedidos/", json=pedido(datos, operacion, cobrado=True)
        ).status_code
        == 201
    )
    usar_rol(client, db, datos, "Gerente")
    parametros = {
        "desde": (datetime.now() - timedelta(days=1)).date().isoformat(),
        "hasta": (datetime.now() + timedelta(days=1)).date().isoformat(),
        "periodo": "dia",
    }
    respuesta = client.get("/finanzas/ventas", params=parametros)
    assert respuesta.status_code == 200, respuesta.text
    assert float(respuesta.json()["total_cobrado"]) == 150
    suscripcion = db.query(Suscripciones).filter_by(id_empresa=datos["empresa"]).one()
    suscripcion.finanzas_habilitadas = False
    db.commit()
    assert client.get("/finanzas/ventas", params=parametros).status_code == 403


def test_operaciones_sucursal_ajena_no_filtran(client, db, datos, operacion):
    creado = client.post("/pedidos/", json=pedido(datos, operacion)).json()["id"]
    from backend.Sesiones.tabla import Sesiones
    from backend.VinculosLaborales.tabla import VinculosLaborales

    vinculo = db.get(VinculosLaborales, datos["vinculo"])
    vinculo.id_empresa = datos["otra_empresa"]
    db.get(Sesiones, datos["sesion"]).id_sucursal = datos["otra_sucursal"]
    db.commit()
    assert client.get(f"/pedidos/{creado}").status_code == 404
    assert client.post(f"/pedidos/{creado}/entregar").status_code == 404
    assert (
        client.post(
            f"/pedidos/{creado}/cancelar", json={"motivo": "Intento externo"}
        ).status_code
        == 404
    )


@pytest.mark.parametrize("rol", ["Administrador", "Mesero"])
@pytest.mark.parametrize(
    "ruta",
    [
        "/finanzas/ventas?desde=2026-01-01&hasta=2026-01-02",
        "/suscripciones/actual",
        "/invitaciones-laborales/",
        "/configuracion-impuestos/",
    ],
)
def test_modulos_privados_solo_gerente(client, db, datos, operacion, rol, ruta):
    usar_rol(client, db, datos, rol)
    assert client.get(ruta).status_code == 403


def test_pedido_edicion_solo_antes_de_cobrar_o_entregar(client, db, datos, operacion):
    cuerpo = pedido(datos, operacion, id_mesa=operacion["mesa"])
    id = client.post("/pedidos/", json=cuerpo).json()["id"]
    cambios = {k: v for k, v in cuerpo.items() if k != "clave_operacion"}
    cambios["detalles"][0]["cantidad"] = 3
    cotizacion = client.post(f"/pedidos/cotizar?id_pedido={id}", json=cambios)
    assert cotizacion.status_code == 200, cotizacion.text
    editado = client.patch(f"/pedidos/{id}", json=cambios)
    assert editado.status_code == 200, editado.text
    assert float(editado.json()["total"]) == 225
    client.post(f"/pedidos/{id}/entregar")
    assert client.patch(f"/pedidos/{id}", json=cambios).status_code == 409


def test_descuento_fijo_no_genera_total_negativo(client, db, datos, operacion):
    descuento = Descuentos(
        id_empresa=datos["empresa"],
        nombre="Invitacion",
        tipo_descuento="CantidadFija",
        valor=999,
    )
    db.add(descuento)
    db.commit()
    cuerpo = pedido(datos, operacion, id_descuento=descuento.id)
    respuesta = client.post("/pedidos/", json=cuerpo)
    assert respuesta.status_code == 201, respuesta.text
    assert float(respuesta.json()["total"]) == 0


def test_suscripcion_vencida_sin_acceso_operativo(client, db, datos, operacion):
    suscripcion = db.query(Suscripciones).filter_by(id_empresa=datos["empresa"]).one()
    suscripcion.fin_prueba = datetime.now(timezone.utc).replace(
        tzinfo=None
    ) - timedelta(days=1)
    db.commit()
    assert client.get("/pedidos/").status_code == 403
    assert client.get("/productos/").status_code == 403
    assert client.get("/suscripciones/actual").json()["estado"] == "Vencida"
    assert (
        client.patch(
            "/suscripciones/plan", json={"finanzas_habilitadas": True}
        ).status_code
        == 409
    )


def test_caja_duplicada_y_cancelacion_resta_del_resumen(client, db, datos, operacion):
    abrir_caja(client, db, datos)
    assert client.post("/cajas/", json={"monto_inicial": 0}).status_code == 409
    creado = client.post(
        "/pedidos/", json=pedido(datos, operacion, cobrado=True)
    ).json()
    assert (
        client.post(
            f'/pedidos/{creado["id"]}/cancelar',
            json={"motivo": "Cliente cancelo la compra"},
        ).status_code
        == 200
    )
    assert client.get("/cajas/actual").json()["efectivo_esperado"] == "100.00"


@pytest.mark.parametrize(
    "cambios",
    [{"cantidad": 0}, {"cantidad": -1}, {"cantidad": 100}, {"id_producto": 0}],
)
def test_detalles_invalidos_no_se_registran(client, datos, operacion, cambios):
    cuerpo = pedido(datos, operacion)
    cuerpo["detalles"][0].update(cambios)
    assert client.post("/pedidos/", json=cuerpo).status_code == 422
    assert client.get("/pedidos/").json()["total"] == 0


def test_reserva_adyacente_y_fecha_sin_zona(client, operacion):
    inicio = datetime.now(timezone.utc) + timedelta(days=2)
    cuerpo = {
        "id_mesa": operacion["mesa"],
        "cliente": "Reserva",
        "personas": 2,
        "inicio": inicio.isoformat(),
        "fin": (inicio + timedelta(hours=1)).isoformat(),
    }
    assert client.post("/reservas/", json=cuerpo).status_code == 201
    cuerpo["inicio"] = cuerpo["fin"]
    cuerpo["fin"] = (inicio + timedelta(hours=2)).isoformat()
    assert client.post("/reservas/", json=cuerpo).status_code == 201
    cuerpo["inicio"] = inicio.replace(tzinfo=None).isoformat()
    assert client.post("/reservas/", json=cuerpo).status_code == 422


def test_invitado_crea_acceso_sin_crear_otra_empresa(client, db, datos, monkeypatch):
    from tests.test_roles_empresas import preparar_correo
    from backend.Empresas.tabla import Empresas
    from backend.Usuarios.tabla import Usuarios

    enviados = preparar_correo(monkeypatch)
    anterior = db.query(Empresas).count()
    respuesta = client.post(
        "/invitaciones-laborales/",
        json={
            "correo": "nuevo-cajero@example.com",
            "rol": "Mesero",
            "sucursales": [datos["sucursal"]],
        },
    )
    assert respuesta.status_code == 201, respuesta.text
    codigo = enviados[0][1]
    client.cookies.clear()
    cuerpo = {
        "codigo": codigo,
        "nombre": "Mesero invitado",
        "clave": "Clave de prueba personal 123",
    }
    respuesta = client.post("/invitaciones-laborales/registrar", json=cuerpo)
    assert respuesta.status_code == 201, respuesta.text
    assert respuesta.json()["rol_empresa"] == "Mesero"
    assert respuesta.json()["id_empresa"] == datos["empresa"]
    assert db.query(Empresas).count() == anterior
    assert "clave" not in respuesta.text
    assert client.get("/sesiones/actual").status_code == 200
    assert (
        client.post("/invitaciones-laborales/registrar", json=cuerpo).status_code == 400
    )


def test_invitacion_invalida_no_crea_usuario(client, db, datos):
    from backend.Usuarios.tabla import Usuarios

    anterior = db.query(Usuarios).count()
    client.cookies.clear()
    respuesta = client.post(
        "/invitaciones-laborales/registrar",
        json={
            "codigo": "x" * 64,
            "nombre": "No registrado",
            "clave": "Clave de prueba personal 123",
        },
    )
    assert respuesta.status_code == 400
    assert db.query(Usuarios).count() == anterior


def test_alta_negocio_revierte_todo_si_falla_ultimo_paso(
    client, db, datos, monkeypatch
):
    from fastapi import HTTPException
    from backend.Empresas.tabla import Empresas
    from backend.Usuarios.tabla import Usuarios

    original = db.add

    def fallar_asignacion(objeto, *args, **kwargs):
        if isinstance(objeto, DisponibilidadProductos):
            raise HTTPException(422, "No se pudo completar la asignacion")
        return original(objeto, *args, **kwargs)

    monkeypatch.setattr(db, "add", fallar_asignacion)
    empresas = db.query(Empresas).count()
    usuarios = db.query(Usuarios).count()
    cuerpo = {
        "cuenta": {
            "nombre": "Propietario nuevo",
            "correo": "fallo-final@example.com",
            "clave": "Clave de prueba completa 123",
        },
        "negocio": {
            "nombre": "Empresa que no debe guardarse",
            "tipo_negocio": "Otro",
            "codigo_pais": "HN",
            "codigo_moneda": "HNL",
            "zona_horaria": "America/Tegucigalpa",
        },
        "sucursales": [
            {
                "id_local": 1,
                "nombre": "Principal",
                "direccion": "Direccion de prueba",
                "es_principal": True,
                "servicios": {"comer_aqui": {"habilitado": True}},
                "pagos": ["efectivo"],
            }
        ],
        "productos": [{"nombre": "Producto inicial", "precio": 45, "sucursales": [1]}],
    }
    client.cookies.clear()
    cuerpo["tarjeta_suscripcion"] = {"tarjeta_prueba":"visa", "titular":"Propietario nuevo", "mes":12, "anio":2099}
    assert client.post("/usuarios/registro-negocio", json=cuerpo).status_code == 422
    assert db.query(Empresas).count() == empresas
    assert db.query(Usuarios).count() == usuarios
    assert db.query(Productos).filter_by(nombre="Producto inicial").count() == 0


def test_catalogo_unificado_solo_productos_y_opciones_del_local(
    client, db, datos, operacion
):
    respuesta = client.get("/pedidos/catalogo")
    assert respuesta.status_code == 200, respuesta.text
    catalogo = respuesta.json()
    assert catalogo["sucursal"]["id"] == datos["sucursal"]
    assert [item["id"] for item in catalogo["productos"]] == [datos["producto"]]
    assert float(catalogo["productos"][0]["precio_local"]) == 75
    assert [item["id_metodo_pago"] for item in catalogo["pagos"]] == [operacion["pago"]]
    assert catalogo["mesas"][0]["id"] == operacion["mesa"]
    db.query(DisponibilidadProductos).filter_by(
        id_producto=datos["producto"], id_sucursal=datos["sucursal"]
    ).one().disponible = False
    db.commit()
    assert client.get("/pedidos/catalogo").json()["productos"] == []
