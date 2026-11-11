from backend.Productos.tabla import Productos
from backend.Usuarios.tabla import Usuarios
from backend.VinculosLaborales.tabla import VinculosLaborales


def test_busqueda_y_orden_antes_de_paginar(client, db, datos):
    productos = [Productos(id_empresa=datos['empresa'], nombre=f'Producto filtro {numero:02}', precio=10) for numero in range(15)]
    db.add_all(productos)
    db.commit()
    ruta = '/productos/'
    respuesta = client.get(ruta, params={'busqueda':'Producto filtro', 'orden':'antiguos', 'limite':5})
    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()['total'] == 15
    assert respuesta.json()['data'][0]['nombre'] == 'Producto filtro 00'
    reciente = client.get(ruta, params={'busqueda':'Producto filtro', 'orden':'recientes', 'limite':5})
    assert reciente.json()['data'][0]['nombre'] == 'Producto filtro 14'
    ultima = client.get(ruta, params={'busqueda':'Producto filtro 14', 'limite':5})
    assert ultima.json()['total'] == 1
    assert ultima.json()['data'][0]['id'] == productos[-1].id


def test_busqueda_no_cruza_empresas_y_escapa_comodines(client, db, datos):
    db.add(Productos(id_empresa=datos['otra_empresa'], nombre='Producto privado ajeno', precio=5))
    db.commit()
    assert client.get('/productos/', params={'busqueda':'privado ajeno'}).json()['total'] == 0
    assert client.get('/productos/', params={'busqueda':'%'}).json()['total'] == 0
    assert client.get('/productos/', params={'orden':'inventado'}).status_code == 422


def test_buscar_empleado_por_nombre(client, db, datos):
    usuario = Usuarios(nombre='Persona identificable', correo='persona-filtro@example.com')
    db.add(usuario)
    db.flush()
    db.add(VinculosLaborales(id_usuario=usuario.id, id_empresa=datos['empresa'], rol='Mesero'))
    db.commit()
    resultado = client.get('/vinculos-laborales/', params={'busqueda':'identificable'})
    assert resultado.status_code == 200
    assert resultado.json()['total'] == 1
    assert resultado.json()['data'][0]['nombre_usuario'] == usuario.nombre


def test_sucursales_mismo_nombre_distinta_direccion(client):
    cuerpo = {'nombre':'La Cafeteada', 'direccion':'Boulevard principal, local 10'}
    primera = client.post('/sucursales/', json=cuerpo)
    assert primera.status_code == 201, primera.text
    segunda = client.post('/sucursales/', json={**cuerpo, 'direccion':'Centro comercial, local 25'})
    assert segunda.status_code == 201, segunda.text
    assert primera.json()['id'] != segunda.json()['id']
    assert client.post('/sucursales/', json=cuerpo).status_code == 409
    assert client.patch(f'/sucursales/{segunda.json()["id"]}', json={'direccion':cuerpo['direccion']}).status_code == 409
    assert client.patch(f'/sucursales/{segunda.json()["id"]}', json={'nombre':cuerpo['nombre']}).status_code == 200
