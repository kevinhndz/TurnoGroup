import base64
import io
from PIL import Image
from backend.Productos.tabla import Productos
from backend.DisponibilidadProductos.tabla import DisponibilidadProductos
from tests.test_roles_empresas import usar_rol


def test_importacion_completa_y_asignacion(client, db, datos):
    cuerpo = {
        "productos": [
            {
                "nombre": "Cafe importado",
                "precio": "45.50",
                "id_categoria": datos["categoria"],
            }
        ],
        "asignar_sucursal": True,
    }
    respuesta = client.post("/productos/importar", json=cuerpo)
    assert respuesta.status_code == 201, respuesta.text
    producto = (
        db.query(Productos)
        .filter_by(nombre="Cafe importado", id_empresa=datos["empresa"])
        .one()
    )
    assert (
        db.query(DisponibilidadProductos)
        .filter_by(id_producto=producto.id, id_sucursal=datos["sucursal"])
        .one()
        .disponible
    )
    assert client.post("/productos/importar", json=cuerpo).status_code == 409


def test_importacion_no_guarda_parcialmente_si_categoria_ajena(client, db, datos):
    cuerpo = {
        "productos": [
            {"nombre": "Valido", "precio": 10},
            {
                "nombre": "Invalido",
                "precio": 20,
                "id_categoria": datos["otra_categoria"],
            },
        ]
    }
    assert client.post("/productos/importar", json=cuerpo).status_code == 404
    assert (
        db.query(Productos).filter(Productos.nombre.in_(["Valido", "Invalido"])).count()
        == 0
    )


def test_foto_validada_aislada_y_sin_metadatos(
    client, db, datos, tmp_path, monkeypatch
):
    monkeypatch.setenv("TURNO_ARCHIVOS", str(tmp_path))
    imagen = io.BytesIO()
    Image.new("RGB", (40, 40), "red").save(imagen, format="PNG")
    cuerpo = {"contenido": base64.b64encode(imagen.getvalue()).decode()}
    respuesta = client.post(f'/productos/{datos["producto"]}/imagen', json=cuerpo)
    assert respuesta.status_code == 200, respuesta.text
    archivo = client.get(f'/productos/{datos["producto"]}/imagen')
    assert archivo.status_code == 200
    assert archivo.headers["content-type"] == "image/jpeg"
    assert Image.open(io.BytesIO(archivo.content)).size == (40, 40)
    assert client.get(f'/productos/{datos["otro_producto"]}/imagen').status_code == 404
    assert (
        client.post(
            f'/productos/{datos["otro_producto"]}/imagen', json=cuerpo
        ).status_code
        == 404
    )
    assert (
        client.post(
            f'/productos/{datos["producto"]}/imagen',
            json={"contenido": base64.b64encode(b"<script>alert(1)</script>").decode()},
        ).status_code
        == 422
    )


def test_mesero_no_importa_ni_modifica_foto(client, db, datos):
    usar_rol(client, db, datos, "Mesero")
    assert (
        client.post(
            "/productos/importar", json={"productos": [{"nombre": "Uno", "precio": 1}]}
        ).status_code
        == 403
    )
    assert (
        client.post(
            f'/productos/{datos["producto"]}/imagen', json={"contenido": "abcd"}
        ).status_code
        == 403
    )
