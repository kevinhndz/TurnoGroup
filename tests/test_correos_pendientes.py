from datetime import datetime, timedelta
from backend.Correos.service import encolar_correo, procesar_correo
from backend.Correos.tabla import CorreosPendientes


def mensaje(db):
    id = encolar_correo(
        db,
        "recuperacion",
        "prueba@example.com",
        "codigo-secreto",
        datetime.utcnow() + timedelta(minutes=15),
    )
    db.commit()
    return id


def test_contenido_cifrado_y_borrado_al_entregar(db):
    id = mensaje(db)
    fila = db.get(CorreosPendientes, id)
    assert "codigo-secreto" not in fila.contenido_cifrado
    enviados = []
    procesar_correo(db, id, lambda correo, codigo: enviados.append((correo, codigo)))
    assert enviados == [("prueba@example.com", "codigo-secreto")]
    assert fila.estado == "enviado"
    assert fila.contenido_cifrado is None
    procesar_correo(db, id, lambda *args: enviados.append(args))
    assert len(enviados) == 1


def test_fallo_programa_reintento_sin_perder_mensaje(db):
    id = mensaje(db)
    procesar_correo(db, id, lambda *args: False)
    fila = db.get(CorreosPendientes, id)
    assert fila.estado == "pendiente"
    assert fila.intentos == 1
    assert fila.proximo_intento > datetime.utcnow()
    assert fila.contenido_cifrado


def test_vencido_no_se_envia(db):
    id = mensaje(db)
    fila = db.get(CorreosPendientes, id)
    fila.vencimiento = datetime.utcnow() - timedelta(seconds=1)
    db.commit()
    enviados = []
    procesar_correo(db, id, lambda *args: enviados.append(args))
    assert fila.estado == "vencido"
    assert fila.contenido_cifrado is None
    assert not enviados
