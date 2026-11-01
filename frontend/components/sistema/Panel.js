'use client';

import Link from 'next/link';
import { modulos } from '../../lib/modulos';
import Espacio from './Espacio';
import { usarSesion } from './Sesion';
import { Proximamente, Vacio } from './Controles';
import Inicio from './Inicio';
import Crud from './Crud';
import Configuracion from './Configuracion';
import Disponibilidad from './Disponibilidad';
import Equipo from './Equipo';
import Cuenta from './Cuenta';
import Bitacora from './Bitacora';
import Pedidos from './Pedidos';
import Reservas from './Reservas';
import Finanzas from './Finanzas';
import Suscripcion from './Suscripcion';
import { EmpresasPlataforma, UsuariosPlataforma, AsignarGerente } from './Plataforma';

export default function Panel({ seccion }) {
  return (
    <Espacio>
      <Contenido seccion={seccion} />
    </Espacio>
  );
}

function Contenido({ seccion }) {
  const { sesion, mesasHabilitadas, reservasHabilitadas } = usarSesion();
  const superadmin = sesion.usuario.rol_plataforma === 'Superadministrador';
  const gerente = sesion.rol_empresa === 'Gerente';
  if (seccion === 'cuenta') return <Cuenta />;
  if (!seccion) return <Inicio />;
  if (superadmin) {
    if (seccion === 'bitacora') return <Bitacora />;
    if (seccion === 'empresas') return <EmpresasPlataforma />;
    if (seccion === 'usuarios') return <UsuariosPlataforma />;
    if (seccion === 'asignar-gerente') return <AsignarGerente />;
    return <SinPermiso />;
  }
  if (!sesion.id_empresa)
    return (
      <Vacio
        titulo="Todavía no has seleccionado una empresa"
        detalle="Crea tu negocio o acepta una invitación del equipo."
      >
        <Link href="/configuracion-inicial" className="tg-button tg-primary">
          Configurar mi negocio
        </Link>
      </Vacio>
    );
  if (
    [
      'productos',
      'categorias',
      'sucursales',
      'descuentos',
      'configuracion',
      'equipo',
    ].includes(seccion) &&
    !gerente
  )
    return <SinPermiso />;
  if (seccion === 'mesas' && !mesasHabilitadas)
    return (
      <Vacio
        titulo="La gestión de mesas está deshabilitada"
        detalle="El gerente puede habilitarla en los servicios de esta sucursal."
      />
    );
  if (modulos[seccion]) return <Crud key={seccion} modulo={seccion} />;
  if (seccion === 'disponibilidad')
    return gerente || sesion.rol_empresa === 'Administrador' ? (
      <Disponibilidad />
    ) : (
      <SinPermiso />
    );
  if (seccion === 'configuracion') return <Configuracion />;
  if (seccion === 'equipo') return <Equipo />;
  if (seccion === 'bitacora') return <Bitacora />;
  if (seccion === 'pedidos') return <Pedidos />;
  if (seccion === 'reservas')
    return reservasHabilitadas ? (
      <Reservas />
    ) : (
      <Vacio titulo="Las reservas están deshabilitadas" />
    );
  if (seccion === 'finanzas') return gerente ? <Finanzas /> : <SinPermiso />;
  if (seccion === 'suscripcion') return gerente ? <Suscripcion /> : <SinPermiso />;
  return <SinPermiso />;
}

function SinPermiso() {
  return (
    <Vacio
      titulo="Esta sección no está disponible para tu rol"
      detalle="Puedes volver al inicio para ver las opciones de tu cuenta."
    >
      <Link href="/panel" className="tg-button tg-secondary">
        Volver a mi panel
      </Link>
    </Vacio>
  );
}
