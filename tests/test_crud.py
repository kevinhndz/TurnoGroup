import pytest


MODULOS = ["empresas", "categorias", "productos", "usuarios", "sucursales", "mesas",
           "configuracion-impuestos", "descuentos", "categorias-gastos"]


def caso(modulo, datos):
    empresa = datos["empresa"]
    cuerpos = {
        "empresas": {"nombre": "Nuevo negocio", "tipo_negocio": "Otro", "codigo_pais": "HN", "zona_horaria": "America/Tegucigalpa", "codigo_moneda": "HNL"},
        "categorias": {"id_empresa": empresa, "nombre": "Bebidas"},
        "productos": {"id_empresa": empresa, "id_categoria": datos["categoria"], "nombre": "Nuevo cafe", "precio": "75.50"},
        "usuarios": {"correo": "nuevo@example.com", "nombre": "Nueva persona", "clave": "Clave-de-prueba-123"},
        "sucursales": {"id_empresa": empresa, "nombre": "Nuevo local", "direccion": "Direccion del nuevo local"},
        "mesas": {"id_sucursal": datos["sucursal"], "nombre": "Mesa 01", "capacidad": 4},
        "configuracion-impuestos": {"id_empresa": empresa, "nombre": "ISV", "porcentaje": "15", "precios_incluyen_impuesto": False},
        "descuentos": {"id_empresa": empresa, "nombre": "Cortesia", "tipo_descuento": "Porcentaje", "valor": "10"},
        "categorias-gastos": {"id_empresa": empresa, "nombre": "Alquiler"},
    }
    params = {} if modulo in ("empresas", "usuarios") else {"id_empresa": empresa}
    if modulo == "mesas":
        params["id_sucursal"] = datos["sucursal"]
    body = {campo:valor for campo,valor in cuerpos[modulo].items() if campo not in ("id_empresa", "id_sucursal")}
    crear_params = {"id_empresa": empresa} if modulo == "mesas" else {}
    return "/" + modulo + "/", body, params, crear_params


def crear(client, modulo, datos):
    ruta, body, params, crear_params = caso(modulo, datos)
    respuesta = client.post(ruta, json=body, params=crear_params)
    assert respuesta.status_code == 201, respuesta.text
    return ruta, respuesta.json(), params


@pytest.mark.parametrize("modulo", MODULOS)
def test_crear_y_detalle_conservan_respuesta(client, datos, modulo):
    ruta, creado, params = crear(client, modulo, datos)
    respuesta = client.get(ruta + str(creado["id"]), params=params)
    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json() == creado


@pytest.mark.parametrize("modulo", MODULOS)
def test_listado_paginado(client, datos, modulo):
    ruta, creado, params = crear(client, modulo, datos)
    respuesta = client.get(ruta, params={**params, "limite": 100}).json()
    assert set(respuesta) == {"total", "pagina_actual", "limite", "total_paginas", "data"}
    assert respuesta["pagina_actual"] == 1
    assert any(item["id"] == creado["id"] for item in respuesta["data"])
    ultima = client.get(ruta, params={**params, "pagina_actual": 99999}).json()
    assert ultima["data"] == []


@pytest.mark.parametrize("modulo", MODULOS)
def test_editar_parcial_y_rechazar_vacios_nulos_y_extras(client, datos, modulo):
    ruta, creado, params = crear(client, modulo, datos)
    detalle = ruta + str(creado["id"])
    cambio = {"porcentaje": "12.5"} if modulo == "configuracion-impuestos" else {"nombre": "Nombre editado"}
    respuesta = client.patch(detalle, params=params, json=cambio)
    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["id"] == creado["id"]
    campo = "porcentaje" if modulo == "configuracion-impuestos" else "nombre"
    for body in [{}, {campo: None}, {"id_empresa": datos["otra_empresa"]}]:
        invalido = client.patch(detalle, params=params, json=body)
        assert invalido.status_code == 422, invalido.text
        assert isinstance(invalido.json()["detail"], str)


@pytest.mark.parametrize("modulo", MODULOS)
def test_desactivar_conserva_detalle_y_listado(client, datos, modulo):
    ruta, creado, params = crear(client, modulo, datos)
    respuesta = client.post(ruta + str(creado["id"]) + "/desactivar", params=params)
    assert respuesta.status_code == 200, respuesta.text
    campo = {"empresas": "estado", "usuarios": "estado", "productos": "disponible"}.get(modulo, "activo")
    esperado = "Inactiva" if modulo == "empresas" else False
    assert respuesta.json()[campo] == esperado
    assert client.get(ruta + str(creado["id"]), params=params).status_code == 200
    listado = client.get(ruta, params={**params, "limite": 100}).json()
    assert any(item["id"] == creado["id"] for item in listado["data"])
    assert client.post(ruta + str(creado["id"]) + "/desactivar", params=params).status_code == 200


@pytest.mark.parametrize("modulo", MODULOS)
def test_registros_inexistentes(client, datos, modulo):
    ruta, _, params, _ = caso(modulo, datos)
    for method, suffix, body in [("GET", "", None), ("PATCH", "", {"nombre": "Cambio"}), ("POST", "/desactivar", None)]:
        if modulo == "configuracion-impuestos" and method == "PATCH":
            body = {"porcentaje": 15}
        respuesta = client.request(method, ruta + "2147483647" + suffix, params=params, json=body)
        assert respuesta.status_code == 404, respuesta.text
        assert respuesta.json()["detail"].startswith("No se encontro")


@pytest.mark.parametrize("modulo", MODULOS)
def test_creacion_invalida_y_duplicada(client, datos, modulo):
    ruta, body, _, crear_params = caso(modulo, datos)
    for invalido in [{}, {**body, "campo_desconocido": True}]:
        respuesta = client.post(ruta, params=crear_params, json=invalido)
        assert respuesta.status_code == 422, respuesta.text
        assert isinstance(respuesta.json()["detail"], str)
    assert client.post(ruta, params=crear_params, json=body).status_code == 201
    duplicado = client.post(ruta, params=crear_params, json=body)
    assert duplicado.status_code == 409, duplicado.text
    assert "detail" in duplicado.json()


@pytest.mark.parametrize("modulo", MODULOS)
@pytest.mark.parametrize("limites", [{"limite": 0}, {"limite": 101}, {"pagina_actual": 0}])
def test_limites_de_paginacion(client, datos, modulo, limites):
    ruta, _, params, _ = caso(modulo, datos)
    respuesta = client.get(ruta, params={**params, **limites})
    assert respuesta.status_code == 422
    assert isinstance(respuesta.json()["detail"], str)


@pytest.mark.parametrize("modulo", MODULOS)
def test_id_no_positivo(client, datos, modulo):
    ruta, _, params, _ = caso(modulo, datos)
    assert client.get(ruta + "0", params=params).status_code == 422


@pytest.mark.parametrize("modulo", [m for m in MODULOS if m not in ("empresas", "usuarios")])
def test_limite_entre_empresas(client, datos, modulo):
    ruta, creado, params = crear(client, modulo, datos)
    ajenos = {**params, "id_empresa": datos["otra_empresa"]}
    detalle = ruta + str(creado["id"])
    assert client.get(detalle, params=ajenos).status_code == 403
    cambio = {"porcentaje": 10} if modulo == "configuracion-impuestos" else {"nombre": "Cambio ajeno"}
    assert client.patch(detalle, params=ajenos, json=cambio).status_code == 403
    assert client.post(detalle + "/desactivar", params=ajenos).status_code == 403
    if modulo != "mesas":
        assert client.get(ruta, params=ajenos).status_code == 403


@pytest.mark.parametrize("modulo", [m for m in MODULOS if m != "configuracion-impuestos"])
def test_editar_no_duplica_identidad(client, datos, modulo):
    ruta, creado, params = crear(client, modulo, datos)
    body = {"correo": "persona@example.com"} if modulo == "usuarios" else {"nombre": "Empresa de prueba 0"} if modulo == "empresas" else {"nombre": "Otra identidad"}
    if modulo not in ("usuarios", "empresas"):
        _, crear_body, _, crear_params = caso(modulo, datos)
        assert client.post(ruta, params=crear_params, json={**crear_body, **body}).status_code == 201
    respuesta = client.patch(ruta + str(creado["id"]), params=params, json=body)
    assert respuesta.status_code == 409, respuesta.text


@pytest.mark.parametrize("valor", ["-1", "NaN", "Infinity", "1.001", "100000000.00"])
def test_precio_producto_invalido(client, datos, valor):
    ruta, body, _, _ = caso("productos", datos)
    assert client.post(ruta, json={**body, "precio": valor}).status_code == 422


def test_producto_no_acepta_categoria_ajena_o_desactivada(client, datos, db):
    ruta, body, _, _ = caso("productos", datos)
    assert client.post(ruta, json={**body, "id_categoria": datos["otra_categoria"]}).status_code == 404
    assert client.post(f'/categorias/{datos["categoria"]}/desactivar', params={"id_empresa": datos["empresa"]}).status_code == 200
    assert client.post(ruta, json=body).status_code == 404


@pytest.mark.parametrize("modulo,campo", [("mesas", "capacidad"), ("sucursales", "telefono"), ("productos", "id_categoria"), ("configuracion-impuestos", "nombre")])
def test_campos_opcionales_se_pueden_limpiar(client, datos, modulo, campo):
    ruta, creado, params = crear(client, modulo, datos)
    respuesta = client.patch(ruta + str(creado["id"]), params=params, json={campo: None})
    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()[campo] is None


def test_sucursal_principal_no_se_duplica_al_reactivar(client, datos):
    body = {"nombre": "Principal A", "direccion": "Direccion de prueba", "es_principal": True}
    primera = client.post('/sucursales/', json=body).json()
    params = {"id_empresa": datos["empresa"]}
    assert client.post(f'/sucursales/{primera["id"]}/desactivar', params=params).status_code == 200
    assert client.post('/sucursales/', json={**body, "nombre": "Principal B"}).status_code == 201
    assert client.patch(f'/sucursales/{primera["id"]}', params=params, json={"activo": True}).status_code == 409


def test_conflicto_detectado_en_base_devuelve_409(client, datos, monkeypatch):
    from backend.Productos.repository import ProductoRepository
    ruta, body, _, _ = caso('productos', datos)
    assert client.post(ruta, json=body).status_code == 201
    monkeypatch.setattr(ProductoRepository, 'buscar_producto_por_nombre', lambda *args: None)
    respuesta = client.post(ruta, json=body)
    assert respuesta.status_code == 409
    assert 'INSERT' not in respuesta.text


@pytest.mark.parametrize('porcentaje', [-1,101,'NaN','Infinity','0.1234'])
def test_impuestos_rechazan_porcentajes_invalidos(client,datos,porcentaje):
    ruta,body,_,_=caso('configuracion-impuestos',datos)
    assert client.post(ruta,json={**body,'porcentaje':porcentaje}).status_code==422


def test_descuento_valida_tipo_y_valor_al_editar(client,datos):
    ruta,body,_,_=caso('descuentos',datos)
    for invalido in [{'tipo_descuento':'Porcentaje','valor':101},{'tipo_descuento':'CantidadFija','valor':-1},{'tipo_descuento':'Otro','valor':10}]:
        assert client.post(ruta,json={**body,**invalido}).status_code==422
    creado=client.post(ruta,json={**body,'tipo_descuento':'CantidadFija','valor':200}).json()
    detalle=ruta+str(creado['id'])
    scope={'id_empresa':datos['empresa']}
    assert client.patch(detalle,params=scope,json={'tipo_descuento':'Porcentaje'}).status_code==422
    assert client.patch(detalle,params=scope,json={'tipo_descuento':'Porcentaje','valor':100}).status_code==200
    assert client.patch(detalle,params=scope,json={'valor':101}).status_code==422


def test_usuario_normaliza_correo(client,datos):
    respuesta=client.post('/usuarios/',json={'nombre':'Otra persona','correo':'NUEVO@EXAMPLE.COM','clave':'Clave-de-prueba-123'})
    assert respuesta.status_code==201
    assert respuesta.json()['correo']=='nuevo@example.com'
    assert client.post('/usuarios/',json={'nombre':'Otra persona','correo':'nuevo@example.com','clave':'Clave-de-prueba-123'}).status_code==409


def test_categoria_desactivada_no_pierde_identidad(client,datos):
    ruta,creado,scope=crear(client,'categorias',datos)
    assert client.post(ruta+str(creado['id'])+'/desactivar',params=scope).status_code==200
    _,body,_,_=caso('categorias',datos)
    assert client.post(ruta,json=body).status_code==409
    assert client.patch(ruta+str(creado['id']),params=scope,json={'activo':True}).status_code==200


def test_salud_y_documentacion(client):
    assert client.get('/salud').json()['base_datos']=='conectada'
    spec=client.get('/openapi.json').json()
    assert '/disponibilidad-productos/{id_producto}/{id_sucursal}' in spec['paths']
    assert spec['paths']['/productos/']['get']['responses']['200']['content']['application/json']['schema']['$ref'].endswith('RespuestaPaginada_NuevoProductoRespuesta_')
