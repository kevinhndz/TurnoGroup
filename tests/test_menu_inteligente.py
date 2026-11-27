import base64
from io import BytesIO

from PIL import Image
from pydantic import SecretStr
import pytest
import requests

from backend.Categorias.tabla import Categorias
from backend.Productos import menu_ia
from backend.Productos.menu_schema import ExtraccionMenu
from backend.Productos.tabla import Productos
from backend.DisponibilidadProductos.tabla import DisponibilidadProductos
from core.config import revision
from tests.test_roles_empresas import usar_rol

RUTA = "/productos/menu-inteligente/"


def extraido(nombre="Cafe", precio="15.00", categoria="Bebidas"):
    return {
        "nombre": nombre,
        "precio": precio,
        "categoria": categoria,
        "descripcion": None,
        "evidencia": nombre + " a " + str(precio),
        "advertencia": None,
    }


@pytest.fixture
def lector(monkeypatch):
    llamadas = []

    def leer(solicitud, moneda):
        llamadas.append((solicitud, moneda))
        return ExtraccionMenu(productos=[extraido()], advertencias=[]), {
            "tokens_in": 20,
            "tokens_out": 30,
        }

    monkeypatch.setattr(menu_ia, "extraer_menu", leer)
    return llamadas


def test_preparar_solo_propone_y_no_guarda(client, db, datos, lector):
    respuesta = client.post(RUTA + "preparar", json={"texto": "Cafe a 15"})
    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["productos"][0]["precio"] == "15.00"
    assert lector[0][1] == "HNL"
    assert db.query(Productos).filter_by(nombre="Cafe").count() == 0
    assert db.query(Categorias).filter_by(nombre="Bebidas").count() == 0


@pytest.mark.parametrize("rol", ["Mesero", "Administrador", "Superadministrador"])
@pytest.mark.parametrize("operacion", ["preparar", "revisar", "confirmar"])
def test_solo_gerente_puede_importar_con_ia(client, db, datos, lector, rol, operacion):
    usar_rol(client, db, datos, rol)
    respuesta = client.post(RUTA + operacion, json={"texto": "Cafe a 15"})
    assert respuesta.status_code == 403
    assert lector == []


def test_ia_no_es_publica_ni_acepta_empresa_del_cliente(client, lector):
    assert (
        client.post(
            RUTA + "preparar", json={"texto": "Cafe", "id_empresa": 2}
        ).status_code
        == 422
    )
    client.cookies.clear()
    assert client.post(RUTA + "preparar", json={"texto": "Cafe"}).status_code == 401
    assert lector == []


def test_reconciliacion_aisla_empresa_y_detecta_repetidos(client, datos):
    respuesta = client.post(
        RUTA + "revisar",
        json={
            "productos": [
                extraido("Producto 0"),
                extraido("PRODUCTO 0"),
                extraido("Producto 1"),
            ]
        },
    )
    assert respuesta.status_code == 200
    filas = respuesta.json()["productos"]
    assert filas[0]["existente"]["id"] == datos["producto"]
    assert filas[1]["repetido"] is True
    assert filas[2]["existente"] is None
    assert datos["otro_producto"] not in [
        s["id"] for f in filas for s in f["similares"]
    ]


def test_precio_ausente_se_conserva_para_revision(client):
    respuesta = client.post(
        RUTA + "revisar", json={"productos": [extraido(precio=None)]}
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["productos"][0]["precio"] is None
    assert (
        client.post(
            RUTA + "confirmar", json={"productos": [{"nombre": "Agua", "precio": None}]}
        ).status_code
        == 422
    )


def test_confirmacion_atomica_y_reintento_no_duplica(client, db, datos):
    cuerpo = {
        "productos": [
            {"nombre": "Cafe nuevo", "precio": "15", "categoria": "Bebidas nuevas"},
            {"nombre": "Pan nuevo", "precio": "10", "categoria": "bebidas nuevas"},
        ]
    }
    respuesta = client.post(RUTA + "confirmar", json=cuerpo)
    assert respuesta.status_code == 201, respuesta.text
    assert respuesta.json() == {
        "creados": 2,
        "categorias_creadas": 1,
        "reutilizados": 0,
    }
    producto = db.query(Productos).filter_by(nombre="Cafe nuevo").one()
    assert producto.id_empresa == datos["empresa"]
    assert (
        db.query(DisponibilidadProductos)
        .filter_by(id_producto=producto.id, id_sucursal=datos["sucursal"])
        .one()
        .disponible
    )
    assert client.post(RUTA + "confirmar", json=cuerpo).status_code == 409
    assert db.query(Productos).filter_by(nombre="Cafe nuevo").count() == 1


def test_error_al_final_revierte_productos_y_categorias(client, db, datos):
    respuesta = client.post(
        RUTA + "confirmar",
        json={
            "productos": [
                {
                    "nombre": "Nuevo atomico",
                    "precio": "15",
                    "categoria": "Categoria atomica",
                },
                {
                    "nombre": "Ajeno",
                    "accion": "usar_existente",
                    "id_existente": datos["otro_producto"],
                },
            ]
        },
    )
    assert respuesta.status_code == 404
    assert db.query(Productos).filter_by(nombre="Nuevo atomico").count() == 0
    assert db.query(Categorias).filter_by(nombre="Categoria atomica").count() == 0


def test_reutilizar_no_cambia_precio_nombre_ni_categoria(client, db, datos):
    respuesta = client.post(
        RUTA + "confirmar",
        json={
            "productos": [
                {
                    "nombre": "Nombre del documento",
                    "precio": "999",
                    "categoria": "No crear",
                    "accion": "usar_existente",
                    "id_existente": datos["producto"],
                }
            ]
        },
    )
    assert respuesta.status_code == 201
    producto = db.get(Productos, datos["producto"])
    assert producto.nombre == "Producto 0"
    assert producto.precio == 75
    assert producto.id_categoria == datos["categoria"]
    assert db.query(Categorias).filter_by(nombre="No crear").count() == 0


def test_normaliza_acentos_espacios_y_mayusculas(client, db, datos):
    db.get(Productos, datos["producto"]).nombre = "Cafe con leche"
    db.commit()
    respuesta = client.post(
        RUTA + "confirmar",
        json={"productos": [{"nombre": " CAFÉ  CON LECHE ", "precio": "10"}]},
    )
    assert respuesta.status_code == 409


def test_categoria_inactiva_requiere_revision(client, db, datos):
    categoria = db.get(Categorias, datos["categoria"])
    categoria.activo = False
    db.commit()
    respuesta = client.post(
        RUTA + "confirmar",
        json={
            "productos": [
                {"nombre": "Nuevo", "precio": "10", "categoria": categoria.nombre}
            ]
        },
    )
    assert respuesta.status_code == 409


def test_limite_de_costo_por_empresa(client, lector, monkeypatch):
    monkeypatch.setattr(revision, "LIMITE_MENU_IA", 1)
    assert client.post(RUTA + "preparar", json={"texto": "Cafe"}).status_code == 200
    assert client.post(RUTA + "preparar", json={"texto": "Cafe"}).status_code == 429
    assert len(lector) == 1


@pytest.fixture
def proveedor(monkeypatch):
    monkeypatch.setattr(revision, "OPENAI_API_KEY", SecretStr("clave-ficticia-no-real"))
    estado = {
        "codigo": 200,
        "datos": {
            "status": "completed",
            "output": [
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "output_text",
                            "text": ExtraccionMenu(
                                productos=[extraido()], advertencias=[]
                            ).model_dump_json(),
                        }
                    ],
                }
            ],
            "usage": {"input_tokens": 20, "output_tokens": 30},
        },
        "llamadas": [],
    }

    def enviar(url, **opciones):
        estado["llamadas"].append((url, opciones))
        if "error" in estado:
            raise estado["error"]

        class Respuesta:
            status_code = estado["codigo"]

            def json(self):
                return estado["datos"]

        return Respuesta()

    monkeypatch.setattr(menu_ia.requests, "post", enviar)
    return estado


def test_api_envia_contrato_estricto_sin_catalogo_ni_herramientas(client, proveedor):
    respuesta = client.post(RUTA + "preparar", json={"texto": "Cafe a 15"})
    assert respuesta.status_code == 200
    url, opciones = proveedor["llamadas"][0]
    cuerpo = opciones["json"]
    assert url == "https://api.openai.com/v1/responses"
    assert cuerpo["store"] is False
    assert "tools" not in cuerpo
    assert cuerpo["text"]["format"]["strict"] is True
    assert "Producto 0" not in str(cuerpo)
    assert opciones["allow_redirects"] is False


def test_foto_se_decodifica_y_reenvia_sin_metadatos(client, proveedor):
    foto = BytesIO()
    Image.new("RGB", (30, 40), "white").save(foto, format="PNG")
    respuesta = client.post(
        RUTA + "preparar", json={"imagen": base64.b64encode(foto.getvalue()).decode()}
    )
    assert respuesta.status_code == 200
    contenido = proveedor["llamadas"][0][1]["json"]["input"][0]["content"]
    assert contenido[1]["image_url"].startswith("data:image/jpeg;base64,")


def test_foto_invalida_no_llega_al_proveedor(client, proveedor):
    respuesta = client.post(
        RUTA + "preparar", json={"imagen": base64.b64encode(b"no soy imagen").decode()}
    )
    assert respuesta.status_code == 422
    assert proveedor["llamadas"] == []


@pytest.mark.parametrize("codigo", [401, 429, 500])
def test_errores_del_proveedor_no_exponen_secretos(client, proveedor, codigo):
    proveedor["codigo"] = codigo
    respuesta = client.post(RUTA + "preparar", json={"texto": "Cafe"})
    assert respuesta.status_code == 503
    assert "clave-ficticia" not in respuesta.text


def test_timeout_no_guarda_productos(client, db, proveedor):
    proveedor["error"] = requests.Timeout("dato sensible")
    assert client.post(RUTA + "preparar", json={"texto": "Cafe"}).status_code == 504
    assert db.query(Productos).filter_by(nombre="Cafe").count() == 0


@pytest.mark.parametrize(
    "respuesta_proveedor",
    [
        {"status": "incomplete", "output": []},
        {"status": "completed", "output": []},
        {
            "status": "completed",
            "output": [
                {
                    "content": [
                        {
                            "type": "output_text",
                            "text": '{"productos": [{"nombre": "Agua", "precio": "-2"}], "advertencias": []}',
                        }
                    ]
                }
            ],
        },
    ],
)
def test_respuestas_incompletas_o_invalidas_no_se_aceptan(
    client, proveedor, respuesta_proveedor
):
    proveedor["datos"] = respuesta_proveedor
    assert client.post(RUTA + "preparar", json={"texto": "Cafe"}).status_code == 502


def test_sin_clave_informa_configuracion_pendiente(client, monkeypatch):
    monkeypatch.setattr(revision, "OPENAI_API_KEY", SecretStr(""))
    respuesta = client.post(RUTA + "preparar", json={"texto": "Cafe"})
    assert respuesta.status_code == 503
    assert "no esta configurada" in respuesta.json()["detail"]
