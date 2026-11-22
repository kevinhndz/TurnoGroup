from datetime import datetime, timedelta, timezone
import jwt
import pytest
from utils.token import crear_token, verificar_token, KEY
from core.exceptions import AccesoProhibidoError


def test_token_heredado_verifica_firma_y_vencimiento():
    token = crear_token("prueba", 1, "Usuario")
    assert verificar_token(token)["id_user"] == 1


@pytest.mark.parametrize(
    "datos",
    [{"user": "prueba"}, {"exp": datetime.now(timezone.utc) - timedelta(minutes=1)}],
)
def test_no_acepta_sin_vencimiento_o_expirado(datos):
    token = jwt.encode(datos, KEY, algorithm="HS256")
    with pytest.raises(AccesoProhibidoError):
        verificar_token(token)
