from datetime import datetime, timedelta
import re
import pytest
from backend.Usuarios.tabla import Usuarios
from backend.VinculosLaborales.tabla import VinculosLaborales, AsignacionesSucursales
from backend.Sucursales.tabla import Sucursales
from backend.Sesiones.tabla import Sesiones
from backend.Productos.tabla import Productos
from backend.Categorias.tabla import Categorias
from backend.DisponibilidadProductos.tabla import DisponibilidadProductos
from backend.InvitacionesLaborales.tabla import InvitacionesLaborales
from utils.token import proteger_token_sesion
from core.config import revision
from main import app


def usar_rol(client, db, datos, rol):
    usuario=db.get(Usuarios,datos['usuario_autorizado'])
    usuario.rol_plataforma='Superadministrador' if rol=='Superadministrador' else 'Usuario'
    vinculo=db.get(VinculosLaborales,datos['vinculo'])
    vinculo.rol='Gerente' if rol=='Superadministrador' else rol
    if rol not in ('Gerente','Superadministrador'):
        db.add(AsignacionesSucursales(id_vinculo_laboral=vinculo.id,id_sucursal=datos['sucursal']))
    db.commit()


@pytest.mark.parametrize('ruta',['/empresas/','/usuarios/','/categorias/','/productos/','/sucursales/',
    '/mesas/','/vinculos-laborales/','/configuracion-impuestos/','/descuentos/','/categorias-gastos/',
    '/tipos-servicio/','/metodos-pago/','/servicios-sucursales/','/pagos-sucursales/',
    '/disponibilidad-productos/','/invitaciones-laborales/','/sesiones/actual','/docs','/openapi.json'])
def test_rutas_privadas_requieren_sesion(client,ruta):
    client.cookies.clear()
    assert client.get(ruta).status_code==401


@pytest.mark.parametrize('rol',['Administrador','Mesero','Superadministrador'])
@pytest.mark.parametrize('ruta',['/configuracion-impuestos/','/categorias-gastos/','/vinculos-laborales/','/invitaciones-laborales/'])
def test_configuracion_y_empleados_solo_gerente(client,db,datos,rol,ruta):
    usar_rol(client,db,datos,rol)
    assert client.get(ruta).status_code==403
    esperado = 422 if ruta=='/vinculos-laborales/' and rol=='Superadministrador' else 403
    assert client.post(ruta,json={}).status_code==esperado


@pytest.mark.parametrize('rol',['Gerente','Administrador','Mesero'])
@pytest.mark.parametrize('ruta',['/usuarios/','/usuarios/999999/rol-plataforma'])
def test_roles_empresa_no_administran_plataforma(client,db,datos,rol,ruta):
    usar_rol(client,db,datos,rol)
    metodo='PATCH' if ruta.endswith('rol-plataforma') else 'GET'
    assert client.request(metodo,ruta,json={'rol_plataforma':'Superadministrador'}).status_code==403


@pytest.mark.parametrize('ruta',['/productos/','/categorias/','/mesas/','/disponibilidad-productos/','/servicios-sucursales/','/pagos-sucursales/'])
def test_superadministrador_no_opera_clientes(client,db,datos,ruta):
    usar_rol(client,db,datos,'Superadministrador')
    assert client.get(ruta).status_code==403
    assert client.post(ruta,json={}).status_code==403
    assert client.get('/empresas/').status_code==200
    assert client.get('/usuarios/').status_code==200


@pytest.mark.parametrize('rol',['Administrador','Mesero'])
def test_catalogo_solo_sucursal_asignada(client,db,datos,rol):
    usar_rol(client,db,datos,rol)
    segundo=Sucursales(id_empresa=datos['empresa'],nombre='Local no asignado',direccion='Direccion secundaria')
    categoria=Categorias(id_empresa=datos['empresa'],nombre='Categoria de otro local')
    db.add_all([segundo,categoria]);db.flush()
    producto=Productos(id_empresa=datos['empresa'],id_categoria=categoria.id,nombre='Producto solo segundo',precio=100)
    db.add(producto);db.flush()
    db.add_all([DisponibilidadProductos(id_producto=datos['producto'],id_sucursal=datos['sucursal']),
                DisponibilidadProductos(id_producto=producto.id,id_sucursal=segundo.id)])
    db.commit()
    assert [fila['id'] for fila in client.get('/productos/').json()['data']]==[datos['producto']]
    assert client.get('/productos/'+str(producto.id)).status_code==404
    assert client.get('/categorias/'+str(categoria.id)).status_code==404
    assert [fila['id'] for fila in client.get('/sucursales/').json()['data']]==[datos['sucursal']]
    assert client.get('/sucursales/'+str(segundo.id)).status_code==404
    assert client.patch('/sesiones/contexto',json={'id_vinculo_laboral':datos['vinculo'],'id_sucursal':segundo.id}).status_code==403
    assert client.post('/productos/',json={'nombre':'No autorizado','precio':1}).status_code==403


@pytest.mark.parametrize('modulo,campo',[('categorias','categoria'),('productos','producto'),('sucursales','sucursal')])
def test_ids_ajenos_y_ausentes_son_indistinguibles(client,datos,modulo,campo):
    externo=datos['otra_'+campo] if campo!='producto' else datos['otro_producto']
    if campo=='categoria':externo=datos['otra_categoria']
    for metodo,body in [('GET',None),('PATCH',{'nombre':'Intento ajeno'}),('POST',None)]:
        sufijo='/desactivar' if metodo=='POST' else ''
        ajeno=client.request(metodo,f'/{modulo}/{externo}'+sufijo,json=body)
        inexistente=client.request(metodo,f'/{modulo}/999999'+sufijo,json=body)
        assert ajeno.status_code==inexistente.status_code==404
        assert ajeno.json()==inexistente.json()


@pytest.mark.parametrize('modulo',['categorias','productos','sucursales','descuentos','configuracion-impuestos','categorias-gastos'])
def test_no_se_toma_empresa_del_navegador(client,datos,modulo):
    assert client.get('/'+modulo+'/',params={'id_empresa':datos['otra_empresa']}).status_code==403
    respuesta=client.post('/'+modulo+'/',json={'id_empresa':datos['otra_empresa']})
    assert respuesta.status_code==422
    assert all(parametro['name']!='id_empresa' for parametro in app.openapi()['paths']['/'+modulo+'/']['get'].get('parameters',[]))


def test_contexto_exige_vinculo_propio_y_rota_token(client,db,datos):
    usuario=Usuarios(correo='otra-persona@example.com',nombre='Otra persona')
    db.add(usuario);db.flush()
    ajeno=VinculosLaborales(id_usuario=usuario.id,id_empresa=datos['otra_empresa'],rol='Gerente')
    db.add(ajeno);db.commit()
    assert client.patch('/sesiones/contexto',json={'id_vinculo_laboral':ajeno.id}).status_code==403
    anterior=client.cookies.get('sesion_turnogroup')
    assert client.patch('/sesiones/contexto',json={'id_vinculo_laboral':datos['vinculo'],'id_sucursal':datos['sucursal']}).status_code==200
    assert client.cookies.get('sesion_turnogroup')!=anterior
    assert client.get('/sesiones/actual',headers={'cookie':'sesion_turnogroup='+anterior}).status_code==401


def test_desactivar_vinculo_quita_acceso_y_no_otorga_permiso_por_jwt(client,db,datos):
    db.get(VinculosLaborales,datos['vinculo']).activo=False
    db.commit()
    assert client.get('/productos/').status_code==403
    client.cookies.clear()
    assert client.get('/productos/',headers={'token':'inventado'}).status_code==401


def test_cambio_de_rol_se_aplica_en_la_siguiente_peticion(client,db,datos):
    usar_rol(client,db,datos,'Administrador')
    assert client.get('/vinculos-laborales/').status_code==403
    db.get(VinculosLaborales,datos['vinculo']).rol='Gerente'
    db.commit()
    assert client.get('/vinculos-laborales/').status_code==200


def preparar_correo(monkeypatch):
    for campo in ('SMTP_SERVIDOR','SMTP_USUARIO','SMTP_CLAVE','SMTP_REMITENTE'):
        monkeypatch.setattr(revision,campo,'valor-de-prueba')
    enviados=[]
    monkeypatch.setattr('backend.InvitacionesLaborales.service.enviar_invitacion',lambda correo,codigo: enviados.append((correo,codigo)))
    return enviados


def sesion_para(client,db,usuario):
    token='token-prueba-invitado-'+str(usuario.id)
    db.add(Sesiones(id_usuario=usuario.id,token_protegido=proteger_token_sesion(token),
                   fecha_inicio=datetime.utcnow(),vencimiento=datetime.utcnow()+timedelta(hours=1)))
    db.commit()
    client.cookies.clear()
    client.cookies.set('sesion_turnogroup',token,domain='testserver.local')


def test_invitacion_verifica_correo_y_se_acepta_una_vez(client,db,datos,monkeypatch):
    enviados=preparar_correo(monkeypatch)
    body={'correo':'invitado@example.com','rol':'Mesero','sucursales':[datos['sucursal']]}
    respuesta=client.post('/invitaciones-laborales/',json=body)
    assert respuesta.status_code==201,respuesta.text
    codigo=enviados[0][1]
    assert codigo not in respuesta.text and 'codigo_protegido' not in respuesta.text
    invitacion=db.query(InvitacionesLaborales).one()
    assert invitacion.codigo_protegido==proteger_token_sesion(codigo)
    assert client.post('/invitaciones-laborales/aceptar',json={'codigo':codigo}).status_code==400
    invitado=Usuarios(correo=body['correo'],nombre='Invitado')
    db.add(invitado);db.commit()
    sesion_para(client,db,invitado)
    aceptada=client.post('/invitaciones-laborales/aceptar',json={'codigo':codigo})
    assert aceptada.status_code==200,aceptada.text
    vinculo=aceptada.json()
    assert vinculo['id_empresa']==datos['empresa'] and vinculo['rol']=='Mesero'
    assert client.post('/invitaciones-laborales/aceptar',json={'codigo':codigo}).status_code==400
    assert client.patch('/sesiones/contexto',json={'id_vinculo_laboral':vinculo['id'],'id_sucursal':datos['sucursal']}).status_code==200
    assert client.patch('/sesiones/contexto',json={'id_vinculo_laboral':vinculo['id'],'id_sucursal':datos['otra_sucursal']}).status_code==403


@pytest.mark.parametrize('caso',['vencida','revocada','sustituida','gerente_inactivo','sucursal_inactiva','cuenta_invitante_inactiva','invitante_de_plataforma'])
def test_invitaciones_invalidas_no_crean_vinculos(client,db,datos,monkeypatch,caso):
    enviados=preparar_correo(monkeypatch)
    body={'correo':'nuevo-invitado@example.com','rol':'Mesero','sucursales':[datos['sucursal']]}
    creada=client.post('/invitaciones-laborales/',json=body)
    assert creada.status_code==201,creada.text
    codigo=enviados[0][1]
    invitacion=db.query(InvitacionesLaborales).one()
    if caso=='vencida':invitacion.vencimiento=datetime.utcnow()-timedelta(seconds=1)
    if caso=='revocada':assert client.post('/invitaciones-laborales/'+str(invitacion.id)+'/revocar').status_code==200
    if caso=='sustituida':assert client.post('/invitaciones-laborales/',json=body).status_code==201
    if caso=='gerente_inactivo':db.get(VinculosLaborales,datos['vinculo']).activo=False
    if caso=='sucursal_inactiva':db.get(Sucursales,datos['sucursal']).activo=False
    if caso=='cuenta_invitante_inactiva':db.get(Usuarios,datos['usuario_autorizado']).estado=False
    if caso=='invitante_de_plataforma':db.get(Usuarios,datos['usuario_autorizado']).rol_plataforma='Superadministrador'
    invitado=Usuarios(correo=body['correo'],nombre='Nuevo')
    db.add(invitado);db.commit()
    sesion_para(client,db,invitado)
    assert client.post('/invitaciones-laborales/aceptar',json={'codigo':codigo}).status_code==400
    assert db.query(VinculosLaborales).filter_by(id_usuario=invitado.id).count()==0


def test_invitacion_no_acepta_sucursal_de_otra_empresa(client,datos,monkeypatch):
    preparar_correo(monkeypatch)
    assert client.post('/invitaciones-laborales/',json={'correo':'nuevo@example.com','rol':'Mesero','sucursales':[datos['otra_sucursal']]}).status_code==404
    assert client.post('/invitaciones-laborales/',json={'correo':'nuevo@example.com','rol':'Superadministrador','sucursales':[]}).status_code==422
    assert client.post('/invitaciones-laborales/',json={'correo':'nuevo@example.com','rol':'Mesero','sucursales':[datos['sucursal'],datos['sucursal']]}).status_code==422


@pytest.mark.parametrize('rol', ['Mesero', 'Administrador'])
def test_personal_solo_tiene_una_sucursal_y_no_cambia_contexto(client, db, datos, monkeypatch, rol):
    preparar_correo(monkeypatch)
    local = Sucursales(id_empresa=datos['empresa'], nombre='Otra sucursal', direccion='Direccion secundaria')
    usuario = Usuarios(correo='personal-unico@example.com', nombre='Personal')
    db.add_all([local, usuario]); db.flush()
    vinculo = VinculosLaborales(id_usuario=usuario.id, id_empresa=datos['empresa'], rol=rol)
    db.add(vinculo); db.commit()
    ruta = f'/vinculos-laborales/{vinculo.id}/sucursales'
    assert client.post(ruta, json={'id_sucursal':datos['sucursal']}).status_code == 201
    assert client.post(ruta, json={'id_sucursal':local.id}).status_code == 409
    assert client.post('/invitaciones-laborales/', json={'correo':'otro-personal@example.com','rol':rol,'sucursales':[datos['sucursal'],local.id]}).status_code == 422
    usar_rol(client, db, datos, rol)
    db.add(AsignacionesSucursales(id_vinculo_laboral=datos['vinculo'], id_sucursal=local.id))
    db.commit()
    assert client.patch('/sesiones/contexto', json={'id_vinculo_laboral':datos['vinculo'],'id_sucursal':local.id}).status_code == 403


def test_gerente_puede_cambiar_sucursal_de_su_empresa(client, db, datos):
    local = Sucursales(id_empresa=datos['empresa'], nombre='Local del gerente', direccion='Direccion secundaria')
    db.add(local); db.commit()
    respuesta = client.patch('/sesiones/contexto', json={'id_vinculo_laboral':datos['vinculo'],'id_sucursal':local.id})
    assert respuesta.status_code == 200
    assert respuesta.json()['id_sucursal'] == local.id


def test_usuario_no_puede_crear_segunda_empresa_ni_recibir_otro_vinculo(client, db, datos):
    cuerpo = {'nombre':'Segunda empresa','tipo_negocio':'Otro','codigo_pais':'HN','zona_horaria':'America/Tegucigalpa','codigo_moneda':'HNL'}
    assert client.post('/empresas/', json=cuerpo).status_code == 409
    usar_rol(client, db, datos, 'Superadministrador')
    assert client.post('/vinculos-laborales/', json={'id_usuario':datos['usuario_autorizado'],'id_empresa':datos['otra_empresa'],'rol':'Gerente'}).status_code == 409


def test_no_invita_usuario_que_ya_tiene_otra_empresa(client, db, datos, monkeypatch):
    preparar_correo(monkeypatch)
    usuario = Usuarios(nombre='Otra persona', correo='otra-empresa@example.com')
    db.add(usuario); db.flush()
    db.add(VinculosLaborales(id_usuario=usuario.id, id_empresa=datos['otra_empresa'], rol='Gerente'))
    db.commit()
    respuesta = client.post('/invitaciones-laborales/', json={'correo':usuario.correo,'rol':'Mesero','sucursales':[datos['sucursal']]})
    assert respuesta.status_code == 409


def test_no_se_elimina_ultimo_gerente(client,datos):
    assert client.patch('/vinculos-laborales/'+str(datos['vinculo']),json={'activo':False}).status_code==409
    assert client.patch('/vinculos-laborales/'+str(datos['vinculo']),json={'rol':'Mesero'}).status_code==409


def test_alta_publica_no_permite_rol_de_plataforma(client,monkeypatch):
    assert client.post('/usuarios/registro-negocio',json={'rol_plataforma':'Superadministrador'}).status_code==422
    client.cookies.clear()
    monkeypatch.setattr(revision,'ALTA_PUBLICA_HABILITADA',False)
    assert client.post('/usuarios/',json={}).status_code==401


def test_todas_las_rutas_tienen_matriz():
    from utils.autorizacion import RUTAS_CON_PERMISO
    for ruta,operaciones in app.openapi()['paths'].items():
        for metodo in operaciones:
            if metodo in ('get','post','patch','delete','put'):
                assert (metodo.upper(), ruta) in RUTAS_CON_PERMISO


@pytest.mark.parametrize('rol',['Administrador','Mesero'])
def test_disponibilidad_edicion_segun_rol(client,db,datos,rol):
    usar_rol(client,db,datos,rol)
    db.add(DisponibilidadProductos(id_producto=datos['producto'],id_sucursal=datos['sucursal']))
    db.commit()
    ruta=f'/disponibilidad-productos/{datos["producto"]}/{datos["sucursal"]}'
    assert client.get(ruta).status_code==200
    respuesta=client.patch(ruta,json={'disponible':False})
    assert respuesta.status_code==(200 if rol=='Administrador' else 403)
    assert client.get(f'/disponibilidad-productos/{datos["otro_producto"]}/{datos["otra_sucursal"]}').status_code==404


def test_superadministrador_aprovisiona_solo_primer_gerente(client,db,datos):
    usar_rol(client,db,datos,'Superadministrador')
    body={'id_usuario':datos['usuario'],'id_empresa':datos['otra_empresa'],'rol':'Mesero'}
    assert client.post('/vinculos-laborales/',json=body).status_code==403
    body['rol']='Gerente'
    respuesta=client.post('/vinculos-laborales/',json=body)
    assert respuesta.status_code==201,respuesta.text
    assert client.post('/vinculos-laborales/',json=body).status_code==409
    assert client.get('/vinculos-laborales/').status_code==403


def test_ultimo_superadministrador_y_escalada(client,db,datos):
    usar_rol(client,db,datos,'Superadministrador')
    id=datos['usuario_autorizado']
    assert client.patch(f'/usuarios/{id}/rol-plataforma',json={'rol_plataforma':'Usuario'}).status_code==409
    assert client.post(f'/usuarios/{id}/desactivar').status_code==409
    otro=datos['usuario']
    assert client.patch(f'/usuarios/{otro}/rol-plataforma',json={'rol_plataforma':'Superadministrador'}).status_code==200
    assert db.get(Usuarios,otro).rol_plataforma=='Superadministrador'


def test_reactivacion_por_invitacion_reemplaza_asignaciones(client,db,datos,monkeypatch):
    enviados=preparar_correo(monkeypatch)
    local=Sucursales(id_empresa=datos['empresa'],nombre='Nuevo local asignado',direccion='Direccion del nuevo local')
    db.add(local);db.flush()
    usuario=db.get(Usuarios,datos['usuario'])
    vinculo=VinculosLaborales(id_usuario=usuario.id,id_empresa=datos['empresa'],rol='Mesero',activo=False)
    db.add(vinculo);db.flush()
    db.add(AsignacionesSucursales(id_vinculo_laboral=vinculo.id,id_sucursal=datos['sucursal']))
    db.commit()
    respuesta=client.post('/invitaciones-laborales/',json={'correo':usuario.correo,'rol':'Administrador','sucursales':[local.id]})
    assert respuesta.status_code==201,respuesta.text
    sesion_para(client,db,usuario)
    respuesta=client.post('/invitaciones-laborales/aceptar',json={'codigo':enviados[0][1]})
    assert respuesta.status_code==200,respuesta.text
    db.refresh(vinculo)
    assert vinculo.activo and vinculo.rol=='Administrador'
    asignadas=db.query(AsignacionesSucursales).filter_by(id_vinculo_laboral=vinculo.id).all()
    assert [fila.id_sucursal for fila in asignadas]==[local.id]


@pytest.mark.parametrize('modulo',['mesas','configuracion-impuestos','descuentos','categorias-gastos','vinculos-laborales','invitaciones-laborales'])
def test_detalles_ajenos_no_filtran_existencia(client,db,datos,modulo):
    from backend.Mesas.tabla import Mesas
    from backend.ConfiguracionImpuestos.tabla import ConfiguracionImpuestos
    from backend.Descuentos.tabla import Descuentos
    from backend.CategoriasGastos.tabla import CategoriasGastos
    modelos={
        'mesas': lambda: Mesas(id_sucursal=datos['otra_sucursal'],nombre='Mesa ajena'),
        'configuracion-impuestos': lambda: ConfiguracionImpuestos(id_empresa=datos['otra_empresa'],porcentaje=15,precios_incluyen_impuesto=False),
        'descuentos': lambda: Descuentos(id_empresa=datos['otra_empresa'],nombre='Descuento ajeno',tipo_descuento='Porcentaje',valor=10),
        'categorias-gastos': lambda: CategoriasGastos(id_empresa=datos['otra_empresa'],nombre='Gasto ajeno'),
        'vinculos-laborales': lambda: VinculosLaborales(id_usuario=datos['usuario'],id_empresa=datos['otra_empresa'],rol='Mesero'),
        'invitaciones-laborales': lambda: InvitacionesLaborales(id_empresa=datos['otra_empresa'],id_usuario_invitante=datos['usuario_autorizado'],correo='ajeno@example.com',rol='Mesero',codigo_protegido='x'*64,fecha_creacion=datetime.utcnow(),vencimiento=datetime.utcnow()+timedelta(days=1)),
    }
    fila=modelos[modulo]()
    db.add(fila);db.commit()
    ajeno=client.get(f'/{modulo}/{fila.id}')
    ausente=client.get(f'/{modulo}/999999')
    assert ajeno.status_code==ausente.status_code==404
    assert ajeno.json()==ausente.json()
    if modulo not in ('invitaciones-laborales',):
        body={'rol':'Mesero'} if modulo=='vinculos-laborales' else {'nombre':'Cambio ajeno'}
        assert client.patch(f'/{modulo}/{fila.id}',json=body).status_code==404


def test_perfil_propio_y_empresa_propia(client,db,datos):
    assert client.get('/usuarios/'+str(datos['usuario_autorizado'])).status_code==200
    assert client.patch('/usuarios/'+str(datos['usuario_autorizado']),json={'nombre':'Nombre propio'}).status_code==200
    assert client.get('/usuarios/'+str(datos['usuario'])).status_code==403
    assert client.get('/empresas/'+str(datos['empresa'])).status_code==200
    usar_rol(client,db,datos,'Mesero')
    assert client.get('/sucursales/'+str(datos['sucursal'])).status_code==200


def test_administrador_no_asigna_ni_retira_productos(client,db,datos):
    usar_rol(client,db,datos,'Administrador')
    db.add(DisponibilidadProductos(id_producto=datos['producto'],id_sucursal=datos['sucursal']))
    db.commit()
    assert client.post('/disponibilidad-productos/',json={'id_producto':datos['producto']}).status_code==403
    assert client.delete(f'/disponibilidad-productos/{datos["producto"]}/{datos["sucursal"]}').status_code==403


def test_alta_final_crea_cuenta_empresa_y_contexto(client):
    client.cookies.clear()
    cuenta={'correo':'propietario-nuevo@example.com','nombre':'Propietario nuevo','clave':'Clave propia de prueba 123'}
    assert client.post('/sesiones/iniciar',json={'correo':cuenta['correo'],'clave':cuenta['clave']}).status_code==401
    registro={'cuenta':cuenta,'negocio':{'nombre':'Empresa del propietario','tipo_negocio':'Otro','codigo_pais':'HN','zona_horaria':'America/Tegucigalpa','codigo_moneda':'HNL'},'sucursales':[{'id_local':1,'nombre':'Principal','direccion':'Direccion principal','es_principal':True,'servicios':{'comer_aqui':{'habilitado':True}},'pagos':['efectivo']}]}
    registro['tarjeta_suscripcion']={'tarjeta_prueba':'visa','titular':'Propietario nuevo','mes':12,'anio':2099}
    creada=client.post('/usuarios/registro-negocio',json=registro)
    assert creada.status_code==201,creada.text
    assert creada.json()['rol_empresa']=='Gerente'
    assert client.get('/productos/').status_code==200
    assert client.post('/categorias/',json={'nombre':'Categoria propia'}).status_code==201
    assert client.post('/sesiones/cerrar').status_code==204
    assert client.get('/productos/').status_code==401


def test_ruta_futura_se_denega_hasta_tener_permiso(client):
    @app.get('/productos/consulta/nueva')
    def nueva_ruta():
        return {'dato':'no debe salir'}
    ruta=app.routes[-1]
    try:
        assert client.get('/productos/consulta/nueva').status_code==403
    finally:
        app.router.routes.remove(ruta)


def test_selector_solo_enumera_sucursales_asignadas(client,db,datos):
    usar_rol(client,db,datos,'Mesero')
    respuesta=client.get('/sesiones/vinculos')
    assert respuesta.status_code==200
    assert respuesta.json()[0]['sucursales']==[{'id':datos['sucursal'],'nombre':'Local 0'}]
