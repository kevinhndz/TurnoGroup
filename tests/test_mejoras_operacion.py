from datetime import timedelta
from backend.Bitacora.tabla import Bitacora
from backend.Mesas.tabla import Mesas
from backend.Reservas.tabla import Reservas
from backend.Usuarios.tabla import Usuarios
from backend.Pedidos.tabla import Pedidos
from core.operaciones import ahora
from tests.test_operacion import operacion, pedido
from tests.test_roles_empresas import usar_rol


def test_preparar_mesas_sin_duplicar(client, db, datos):
    respuesta = client.post("/mesas/preparar", json={"cantidad": 8})
    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["creadas"] == 8
    assert client.post("/mesas/preparar", json={"cantidad": 8}).json()["creadas"] == 0
    assert db.query(Mesas).filter_by(id_sucursal=datos["sucursal"]).count() == 8
    usar_rol(client, db, datos, "Mesero")
    assert client.post("/mesas/preparar", json={"cantidad": 9}).status_code == 403


def test_disponibilidad_ocupada_y_reservada(client, db, datos, operacion):
    creada = client.post(
        "/pedidos/", json=pedido(datos, operacion, id_mesa=operacion["mesa"])
    ).json()
    assert client.get("/pedidos/mesas").json()[0]["estado"] == "Ocupada"
    assert (
        client.get(f'/pedidos/mesas?id_pedido={creada["id"]}').json()[0]["estado"]
        == "Disponible"
    )
    client.post(f'/pedidos/{creada["id"]}/cancelar', json={"motivo": "Cliente cancelo"})
    assert client.get("/pedidos/mesas").json()[0]["estado"] == "Disponible"
    db.add(
        Reservas(
            id_empresa=datos["empresa"],
            id_sucursal=datos["sucursal"],
            id_usuario=datos["usuario_autorizado"],
            id_mesa=operacion["mesa"],
            cliente="Cliente reservado",
            personas=2,
            inicio=ahora() - timedelta(minutes=10),
            fin=ahora() + timedelta(minutes=30),
            estado="Confirmada",
        )
    )
    db.commit()
    assert client.get("/pedidos/mesas").json()[0]["estado"] == "Reservada"
    assert (
        client.post(
            "/pedidos/", json=pedido(datos, operacion, id_mesa=operacion["mesa"])
        ).status_code
        == 409
    )


def test_bitacora_actor_cliente_y_acciones(client, db, datos, operacion):
    creada = client.post(
        "/pedidos/", json=pedido(datos, operacion, cliente="Ana")
    ).json()
    respuesta = client.get("/bitacora/")
    assert respuesta.status_code == 200, respuesta.text
    fila = respuesta.json()["data"][0]
    assert fila["persona"] == "Gerente de pruebas"
    assert fila["cliente"] == "Ana"
    assert fila["accion"] == "Pedido creado"
    client.post(f'/pedidos/{creada["id"]}/entregar')
    assert client.get("/bitacora/").json()["data"][0]["accion"] == "Pedido entregado"
    usar_rol(client, db, datos, "Mesero")
    assert client.get("/bitacora/").status_code == 200
    assert client.get("/bitacora/?solo_sucursal=false").status_code == 403
    assert client.post("/bitacora/", json={}).status_code == 405


def test_bitacora_no_filtra_otra_empresa(client, db, datos, operacion):
    db.add(
        Bitacora(
            id_empresa=datos["otra_empresa"],
            id_sucursal=datos["otra_sucursal"],
            id_usuario=datos["usuario"],
            recurso="pedidos",
            id_registro=999,
            accion="Pedido creado",
            cliente="Cliente ajeno",
        )
    )
    db.commit()
    respuesta = client.get("/bitacora/?solo_sucursal=false")
    assert respuesta.status_code == 200
    assert "Cliente ajeno" not in respuesta.text
    db.get(Usuarios, datos["usuario_autorizado"]).rol_plataforma = "Superadministrador"
    db.commit()
    respuesta = client.get("/bitacora/")
    assert respuesta.status_code == 200, respuesta.text
    assert "Cliente ajeno" not in respuesta.text
    assert all(item["sucursal"] is None for item in respuesta.json()["data"])


def test_error_no_deja_bitacora_fantasma(client, db, datos, operacion):
    anterior = db.query(Bitacora).count()
    assert (
        client.post(
            "/pedidos/", json=pedido(datos, operacion, cobrado=True, id_metodo_pago=999999)
        ).status_code
        == 422
    )
    assert db.query(Bitacora).count() == anterior


def test_correo_invitacion_incluye_boton(monkeypatch):
    import utils.correo as correo
    from core.config import revision

    enviados = []

    class Servidor:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def starttls(self, **kwargs):
            pass

        def login(self, *args):
            pass

        def send_message(self, mensaje):
            enviados.append(mensaje)

    monkeypatch.setattr(correo.smtplib, "SMTP", Servidor)
    assert correo.enviar_invitacion("invitado@example.com", "a" * 64)
    html = enviados[0].get_body(preferencelist=("html",)).get_content()
    assert "Aceptar invitacion" in html
    assert "/invitacion#codigo=" + "a" * 64 in html


def test_bitacora_se_revierte_si_falla_commit(
    client, db, datos, operacion, monkeypatch
):
    from fastapi import HTTPException

    anterior = db.query(Bitacora).count()

    def fallar():
        raise HTTPException(409, "No se pudo confirmar")

    monkeypatch.setattr(db, "commit", fallar)
    assert client.post("/pedidos/", json=pedido(datos, operacion)).status_code == 409
    assert db.query(Bitacora).count() == anterior
    assert db.query(Pedidos).count() == 0


def test_alta_prepara_mesas_por_sucursal(client, db):
    cuerpo = {
        "cuenta": {
            "nombre": "Gerente con mesas",
            "correo": "mesas-nuevas@example.com",
            "clave": "Clave propia de prueba 123",
        },
        "negocio": {
            "nombre": "Empresa con mesas iniciales",
            "tipo_negocio": "Otro",
            "codigo_pais": "HN",
            "codigo_moneda": "HNL",
            "zona_horaria": "America/Tegucigalpa",
        },
        "sucursales": [
            {
                "id_local": 1,
                "nombre": "Principal",
                "direccion": "Direccion principal",
                "es_principal": True,
                "cantidad_mesas": 5,
                "servicios": {
                    "comer_aqui": {"habilitado": True, "mesas_habilitadas": True}
                },
                "pagos": ["efectivo"],
            }
        ],
    }
    cuerpo["tarjeta_suscripcion"] = {"tarjeta_prueba":"visa", "titular":"Gerente de prueba", "mes":12, "anio":2099}
    respuesta = client.post("/usuarios/registro-negocio", json=cuerpo)
    assert respuesta.status_code == 201, respuesta.text
    assert (
        db.query(Mesas).filter_by(id_sucursal=respuesta.json()["id_sucursal"]).count()
        == 5
    )


def test_gerente_consulta_empresa_sin_sucursal_seleccionada(client, db, datos):
    from backend.Sesiones.tabla import Sesiones

    db.get(Sesiones, datos["sesion"]).id_sucursal = None
    db.commit()
    assert client.get("/bitacora/?solo_sucursal=false").status_code == 200
    assert client.get("/bitacora/").status_code == 403


def test_plataforma_registra_su_actividad_sin_exponer_ventas(client, db, datos):
    db.get(Usuarios, datos["usuario_autorizado"]).rol_plataforma = "Superadministrador"
    db.commit()
    cuerpo = {
        "nombre": "Empresa de plataforma auditada",
        "tipo_negocio": "Otro",
        "codigo_pais": "HN",
        "codigo_moneda": "HNL",
        "zona_horaria": "America/Tegucigalpa",
    }
    creada = client.post("/empresas/", json=cuerpo)
    assert creada.status_code == 201, creada.text
    filas = client.get("/bitacora/").json()["data"]
    assert any(
        fila["recurso"] == "empresas" and fila["id_registro"] == creada.json()["id"]
        for fila in filas
    )
    assert all(fila["sucursal"] is None and fila["cliente"] is None for fila in filas)


def test_recuperar_operacion_no_duplica_y_respeta_empresa(client, db, datos, operacion):
    cuerpo = pedido(datos, operacion)
    creada = client.post("/pedidos/", json=cuerpo).json()
    respuesta = client.get("/pedidos/operaciones/" + cuerpo["clave_operacion"])
    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["id"] == creada["id"]
    assert client.post("/pedidos/", json=cuerpo).json()["id"] == creada["id"]
    from backend.Sesiones.tabla import Sesiones
    from backend.VinculosLaborales.tabla import VinculosLaborales

    db.get(VinculosLaborales, datos["vinculo"]).id_empresa = datos["otra_empresa"]
    db.get(Sesiones, datos["sesion"]).id_sucursal = datos["otra_sucursal"]
    db.commit()
    assert (
        client.get("/pedidos/operaciones/" + cuerpo["clave_operacion"]).status_code
        == 404
    )
