'use client';

import Link from 'next/link';
import { usarSesion } from './Sesion';
import { useDatos } from './Datos';
import { api } from '../../lib/api';
import { Mensaje, Vacio } from './Controles';
import Icon from '../Icon';

export default function Inicio() {
  const { sesion, mesasHabilitadas } = usarSesion();
  const superadmin = sesion.usuario.rol_plataforma === 'Superadministrador';
  const gerente = sesion.rol_empresa === 'Gerente';
  const tarjetas = superadmin
    ? [
        ['Empresas registradas', 'store', '/panel/empresas', '/empresas/'],
        ['Cuentas registradas', 'team', '/panel/usuarios', '/usuarios/'],
      ]
    : !sesion.id_empresa
      ? []
      : gerente
        ? [
            ['Sucursales registradas', 'store', '/panel/sucursales', '/sucursales/'],
            ['Productos en catálogo', 'coffee', '/panel/productos', '/productos/'],
            ['Categorías registradas', 'book', '/panel/categorias', '/categorias/'],
            ['Vínculos laborales', 'team', '/panel/equipo', '/vinculos-laborales/'],
          ]
        : mesasHabilitadas
          ? [['Mesas registradas', 'table', '/panel/mesas', '/mesas/']]
          : [];
  const datos = useDatos(
    () => Promise.all(tarjetas.map(([, , , ruta]) => api(`${ruta}?limite=1`))),
    [sesion.id_empresa, sesion.id_sucursal, mesasHabilitadas],
  );
  const pedidos = useDatos(
    () =>
      !superadmin && sesion.id_sucursal
        ? api('/pedidos/?estado=Abierto&limite=5')
        : Promise.resolve(null),
    [sesion.id_empresa, sesion.id_sucursal],
  );
  const accesos = superadmin
    ? [
        ['Empresas', '/panel/empresas', 'store'],
        ['Usuarios', '/panel/usuarios', 'team'],
        ['Asignar primer gerente', '/panel/asignar-gerente', 'team'],
      ]
    : [
        ['Pedidos', '/panel/pedidos', 'receipt'],
        ...(gerente
          ? [
              ['Productos y categorías', '/panel/productos', 'coffee'],
              ['Empleados', '/panel/equipo', 'team'],
              ['Configuración', '/panel/configuracion', 'menu'],
            ]
          : []),
        ...(mesasHabilitadas ? [['Mesas del local', '/panel/mesas', 'table']] : []),
      ];

  return (
    <>
      <div className="tg-section-heading">
        <div>
          <span className="tg-eyebrow">
            {new Intl.DateTimeFormat('es-HN', { dateStyle: 'full' }).format(new Date())}
          </span>
          <h1>
            {superadmin ? 'Administración de plataforma' : 'Resumen operativo de hoy'}
          </h1>
          <p>
            {superadmin
              ? 'Empresas y cuentas registradas en Turno Group.'
              : 'Resumen de tu empresa y de la sucursal seleccionada.'}
          </p>
        </div>
        {!superadmin && (
          <Link className="tg-button tg-primary" href="/nuevo-pedido">
            + Nuevo pedido
          </Link>
        )}
      </div>
      <Mensaje error={datos.error} />
      {!superadmin && !sesion.id_empresa ? (
        <section className="tg-card">
          <Vacio
            titulo="Prepara tu espacio de trabajo"
            detalle="Completa la configuración del negocio o acepta la invitación de tu equipo."
          >
            <Link href="/configuracion-inicial" className="tg-button tg-primary">
              Continuar configuración
            </Link>
          </Vacio>
        </section>
      ) : (
        <>
          {!!tarjetas.length && (
            <div className="tg-stats">
              {tarjetas.map(([titulo, icono, href], indice) => (
                <Link href={href} key={titulo} className="tg-card tg-stat">
                  <span className="tg-stat-label">
                    {titulo}
                    <Icon name={icono} />
                  </span>
                  <strong>
                    {datos.cargando
                      ? '…'
                      : datos.error
                        ? '—'
                        : (datos.datos?.[indice]?.total ?? '—')}
                  </strong>
                  <small>Ver registros →</small>
                </Link>
              ))}
            </div>
          )}
          <div className="tg-home-grid">
            <section className="tg-card">
              <span className="tg-eyebrow">
                {superadmin ? 'GESTIÓN DE PLATAFORMA' : 'PEDIDOS EN CURSO'}
              </span>
              <h2>
                {superadmin ? 'Cada empresa tiene su espacio' : 'Pedidos de la sucursal'}
              </h2>
              {pedidos.datos?.data?.length ? (
                <div className="tg-quick-links">
                  {pedidos.datos.data.map((pedido) => (
                    <Link key={pedido.id} href={`/panel/pedidos?pedido=${pedido.id}`}>
                      Pedido #TG-{pedido.id}
                      <span>{pedido.cliente || 'Sin nombre'}</span>
                      <span>{pedido.fecha_pago ? 'Pagado' : 'Pendiente de cobro'} →</span>
                    </Link>
                  ))}
                </div>
              ) : (
                <Vacio
                  titulo={
                    superadmin
                      ? 'Administra las cuentas de la plataforma'
                      : 'Todavía no hay pedidos abiertos'
                  }
                  detalle={
                    superadmin
                      ? 'El gerente administra el catálogo y la operación de su negocio.'
                      : 'Crea el primer pedido desde el catálogo de la sucursal.'
                  }
                  icono={superadmin ? 'store' : 'receipt'}
                />
              )}
            </section>
            <section className="tg-card">
              <span className="tg-eyebrow">ACCESOS RÁPIDOS</span>
              <h2>A un paso</h2>
              <div className="tg-quick-links">
                {accesos.map(([label, href, icono]) => (
                  <Link key={href} href={href}>
                    <Icon name={icono} />
                    {label}
                    <Icon name="arrow" size={16} />
                  </Link>
                ))}
              </div>
            </section>
          </div>
        </>
      )}
    </>
  );
}
