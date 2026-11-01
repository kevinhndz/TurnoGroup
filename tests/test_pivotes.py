import pytest
from backend.TiposServicio.tabla import TiposServicio
from backend.MetodosPago.tabla import MetodosPago
from backend.Sucursales.tabla import Sucursales
from backend.Productos.tabla import Productos


@pytest.mark.parametrize('catalogo,claves', [
    ('tipos-servicio', {'comer_aqui','para_llevar','domicilio'}),
    ('metodos-pago', {'efectivo','transferencia','tarjeta'}),
])
def test_catalogos_son_fijos_y_paginados(client, catalogo, claves):
    ruta='/' + catalogo + '/'
    respuesta=client.get(ruta)
    assert respuesta.status_code==200
    assert {item['clave_concepto'] for item in respuesta.json()['data']}==claves
    id=respuesta.json()['data'][0]['id']
    assert client.get(ruta+str(id)).status_code==200
    assert client.get(ruta+'2147483647').status_code==404
    assert client.get(ruta+'0').status_code==422
    assert client.get(ruta,params={'limite':0}).status_code==422
    assert len(client.get(ruta,params={'limite':2,'pagina_actual':2}).json()['data'])==1
    for metodo in ['POST','PATCH','DELETE']:
        objetivo=ruta if metodo=='POST' else ruta+str(id)
        assert client.request(metodo,objetivo,json={'nombre_visible':'Arbitrario'}).status_code==405


@pytest.mark.parametrize('modulo,modelo,campo', [
    ('servicios-sucursales',TiposServicio,'id_tipo_servicio'),
    ('pagos-sucursales',MetodosPago,'id_metodo_pago'),
])
def test_configuracion_por_sucursal(client,db,datos,modulo,modelo,campo):
    opcion=db.query(modelo).order_by(modelo.id).first().id
    ruta='/' + modulo + '/'
    params={'id_empresa':datos['empresa'],'id_sucursal':datos['sucursal']}
    body={campo:opcion}
    assert client.get(ruta,params=params).json()['total']==0
    creado=client.post(ruta,params={'id_empresa':datos['empresa']},json=body)
    assert creado.status_code==201,creado.text
    assert creado.json()['habilitado'] is False
    assert client.get(ruta,params=params).json()['total']==0
    assert client.get(ruta,params={**params,'solo_habilitados':False}).json()['total']==1
    assert client.post(ruta,params={'id_empresa':datos['empresa']},json=body).status_code==409
    detalle=ruta+f'{datos["sucursal"]}/{opcion}'
    scope={'id_empresa':datos['empresa']}
    assert client.get(detalle,params=scope).json()==creado.json()
    assert client.patch(detalle,params=scope,json={'habilitado':True}).status_code==200
    assert client.get(ruta,params=params).json()['total']==1
    assert client.get(ruta,params={'id_empresa':datos['otra_empresa'],'id_sucursal':datos['otra_sucursal']}).status_code==403
    ajeno={'id_empresa':datos['otra_empresa']}
    for method,sufijo,body_editar in [('GET','',None),('PATCH','',{'habilitado':False}),('POST','/desactivar',None)]:
        assert client.request(method,detalle+sufijo,params=ajeno,json=body_editar).status_code==403
    assert client.post(ruta,params=ajeno,json=body).status_code==403
    for body_invalido in [{},{'habilitado':None},{'id_sucursal':datos['otra_sucursal']}]:
        assert client.patch(detalle,params=scope,json=body_invalido).status_code==422
    assert client.post(detalle+'/desactivar',params=scope).json()['habilitado'] is False
    assert client.get(detalle,params=scope).status_code==200
    assert client.get(ruta,params=params).json()['total']==0
    assert client.patch(detalle,params=scope,json={'habilitado':True}).status_code==200
    assert client.post(ruta,params=scope,json={**body,campo:2147483647}).status_code==404
    assert client.get(ruta+f'{datos["sucursal"]}/2147483647',params=scope).status_code==404
    assert client.patch(ruta+f'{datos["sucursal"]}/2147483647',params=scope,json={'habilitado':True}).status_code==404
    assert client.post(ruta+f'{datos["sucursal"]}/2147483647/desactivar',params=scope).status_code==404
    assert client.get(ruta,params={**params,'limite':101}).status_code==422
    assert client.post(ruta,params=scope,json={}).status_code==422
    catalogo=db.get(modelo,opcion)
    catalogo.activo=False
    db.commit()
    assert client.get(ruta,params=params).json()['total']==0


def test_dependencias_mesas_y_reservas(client,db,datos):
    opciones={o.clave_concepto:o.id for o in db.query(TiposServicio).all()}
    scope={'id_empresa':datos['empresa']}
    body={'id_tipo_servicio':opciones['comer_aqui']}
    ruta='/servicios-sucursales/'
    assert client.post(ruta,params=scope,json={**body,'mesas_habilitadas':True}).status_code==422
    assert client.post(ruta,params=scope,json={**body,'habilitado':True,'reservas_habilitadas':True}).status_code==422
    assert client.post(ruta,params=scope,json={**body,'id_tipo_servicio':opciones['para_llevar'],'habilitado':True,'mesas_habilitadas':True}).status_code==422
    body.update(habilitado=True,mesas_habilitadas=True,reservas_habilitadas=True)
    assert client.post(ruta,params=scope,json=body).status_code==201
    detalle=ruta+f'{datos["sucursal"]}/{opciones["comer_aqui"]}'
    assert client.patch(detalle,params=scope,json={'mesas_habilitadas':False}).status_code==422
    respuesta=client.post(detalle+'/desactivar',params=scope)
    assert respuesta.status_code==200
    assert not any(respuesta.json()[campo] for campo in ['habilitado','mesas_habilitadas','reservas_habilitadas'])


def test_vinculos_y_asignaciones(client,datos,db):
    scope={'id_empresa':datos['empresa']}
    ajeno={'id_empresa':datos['otra_empresa']}
    body={'id_usuario':datos['usuario'],'id_empresa':datos['empresa'],'rol':'Mesero'}
    ruta='/vinculos-laborales/'
    from backend.VinculosLaborales.tabla import VinculosLaborales
    assert client.post(ruta,json=body).status_code==403
    vinculo=VinculosLaborales(id_usuario=datos['usuario'],id_empresa=datos['empresa'],rol='Mesero')
    db.add(vinculo);db.commit()
    id=vinculo.id
    assert client.get(ruta,params=scope).json()['total']==2
    assert client.get(ruta,params={**scope,'limite':0}).status_code==422
    assert client.get(ruta+str(id),params=ajeno).status_code==403
    assert client.get(ruta+'2147483647',params=scope).status_code==404
    asignaciones=ruta+str(id)+'/sucursales'
    body_asignacion={'id_sucursal':datos['sucursal']}
    assert client.post(asignaciones,params=ajeno,json=body_asignacion).status_code==403
    assert client.post(asignaciones,params=scope,json={'id_sucursal':datos['otra_sucursal']}).status_code==404
    assert client.post(asignaciones,params=scope,json={'id_sucursal':0}).status_code==422
    assert client.post(asignaciones,params=scope,json=body_asignacion).status_code==201
    assert client.post(asignaciones,params=scope,json=body_asignacion).status_code==409
    assert client.get(asignaciones,params=scope).json()['total']==1
    assert client.get(asignaciones,params=ajeno).status_code==403
    assert client.get(asignaciones,params={**scope,'pagina_actual':0}).status_code==422
    assert len(client.get(ruta+str(id),params=scope).json()['asignaciones_sucursales'])==1
    detalle=asignaciones+'/'+str(datos['sucursal'])
    assert client.delete(detalle,params=ajeno).status_code==403
    respuesta=client.delete(detalle,params=scope)
    assert respuesta.status_code==204 and respuesta.content==b''
    assert client.delete(detalle,params=scope).status_code==404
    assert client.get(asignaciones,params=scope).json()['data']==[]


def test_disponibilidad_producto_en_varias_sucursales(client,db,datos):
    local=Sucursales(id_empresa=datos['empresa'],nombre='Segundo local',direccion='Segunda direccion')
    db.add(local);db.commit()
    scope={'id_empresa':datos['empresa']}
    ajeno={'id_empresa':datos['otra_empresa']}
    ruta='/disponibilidad-productos/'
    body={'id_producto':datos['producto']}
    total_productos=db.query(Productos).count()
    creado=client.post(ruta,params=scope,json=body)
    assert creado.status_code==201,creado.text
    assert client.patch('/sesiones/contexto',json={'id_vinculo_laboral':datos['vinculo'],'id_sucursal':local.id}).status_code==200
    assert client.post(ruta,params=scope,json=body).status_code==201
    assert client.patch('/sesiones/contexto',json={'id_vinculo_laboral':datos['vinculo'],'id_sucursal':datos['sucursal']}).status_code==200
    assert db.query(Productos).count()==total_productos
    assert client.post(ruta,params=scope,json=body).status_code==409
    detalle=ruta+f'{datos["producto"]}/{datos["sucursal"]}'
    assert client.get(detalle,params=scope).json()==creado.json()
    assert client.get(ruta,params={**scope,'id_sucursal':datos['sucursal']}).json()['total']==1
    assert client.get(ruta,params={**scope,'id_sucursal':datos['otra_sucursal']}).status_code==404
    assert client.post(ruta,params=scope,json={**body,'id_producto':datos['otro_producto']}).status_code==404
    assert client.post(ruta,params=scope,json={**body,'id_sucursal':datos['otra_sucursal']}).status_code==422
    for method in ['GET','PATCH','DELETE']:
        kwargs={'json':{'disponible':False}} if method=='PATCH' else {}
        assert client.request(method,detalle,params=ajeno,**kwargs).status_code==403
    respuesta=client.patch(detalle,params=scope,json={'disponible':False})
    assert respuesta.status_code==200 and respuesta.json()['disponible'] is False
    assert respuesta.json()['disponible'] is False
    assert client.get(ruta,params={**scope,'id_sucursal':datos['sucursal']}).json()['total']==1
    for valor in ['-1','NaN','Infinity','0.001','10000000000']:
        assert client.patch(detalle,params=scope,json={'precio_especial':valor}).status_code==422
    for invalido in [{},{'disponible':None},{'id_producto':datos['otro_producto']}]:
        assert client.patch(detalle,params=scope,json=invalido).status_code==422
    assert client.patch(detalle,params=scope,json={'disponible':True}).status_code==200
    assert client.patch(detalle,params=scope,json={'precio_especial':0}).status_code==422
    assert client.delete(detalle,params=scope).status_code==204
    for method in ['GET','PATCH','DELETE']:
        kwargs={'json':{'disponible':False}} if method=='PATCH' else {}
        assert client.request(method,detalle,params=scope,**kwargs).status_code==404
    assert client.get(ruta+f'{datos["producto"]}/{local.id}',params=scope).status_code==404
    assert db.get(Productos,datos['producto']) is not None
    assert client.get(ruta,params={**scope,'id_sucursal':datos['sucursal'],'limite':0}).status_code==422
    assert client.post(ruta,params=scope,json={}).status_code==422
