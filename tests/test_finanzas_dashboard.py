from decimal import Decimal
import pytest
from tests.test_operacion import operacion, pedido
from tests.test_roles_empresas import usar_rol
from backend.Suscripciones.tabla import Suscripciones


def test_dashboard_usa_cobros_reales_y_categorias(client, db, datos, operacion):
    creado = client.post('/pedidos/', json=pedido(datos, operacion, cobrado=True))
    assert creado.status_code == 201, creado.text
    respuesta = client.get('/finanzas/dashboard', params={'periodo':'mes'})
    assert respuesta.status_code == 200, respuesta.text
    d = respuesta.json()
    assert d['pedidos'] == 1
    assert Decimal(d['total_cobrado']) == Decimal(creado.json()['total'])
    assert sum(Decimal(item['ventas']) for item in d['categorias']) == Decimal(d['total_cobrado'])
    assert sum(d['horas']['actual']) == 1
    assert len(d['anual']) == 12
    assert set(d['periodos']) == {'dia','semana','mes','anio'}
    assert d['sucursales'][0]['id_sucursal'] == datos['sucursal']
    assert d['sucursales'][0]['direccion']


def test_dashboard_excluye_pendientes_y_cancelados(client, db, datos, operacion):
    assert client.post('/pedidos/', json=pedido(datos, operacion)).status_code == 201
    pagado = client.post('/pedidos/', json=pedido(datos, operacion, cobrado=True)).json()
    assert client.post(f'/pedidos/{pagado["id"]}/cancelar', json={'motivo':'Prueba de cancelacion'}).status_code == 200
    d = client.get('/finanzas/dashboard').json()
    assert d['pedidos'] == 0
    assert Decimal(d['total_cobrado']) == 0
    assert d['categorias'] == []


@pytest.mark.parametrize('rol',['Mesero','Administrador','Superadministrador'])
def test_dashboard_reserva_acceso_al_gerente(client, db, datos, operacion, rol):
    usar_rol(client, db, datos, rol)
    assert client.get('/finanzas/dashboard').status_code == 403


def test_dashboard_valida_fechas_y_suscripcion(client, db, datos, operacion):
    assert client.get('/finanzas/dashboard', params={'desde':'2026-11-10','hasta':'2026-11-01'}).status_code == 422
    assert client.get('/finanzas/dashboard', params={'desde':'2026-11-01'}).status_code == 422
    assert client.get('/finanzas/dashboard', params={'periodo':'invalido'}).status_code == 422
    db.query(Suscripciones).filter_by(id_empresa=datos['empresa']).one().finanzas_habilitadas = False
    db.commit()
    assert client.get('/finanzas/dashboard').status_code == 403
