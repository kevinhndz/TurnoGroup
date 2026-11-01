'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import Icon from '../Icon';
import { AccesoPrivado, usarSesion } from './Sesion';
import { Mensaje } from './Controles';
import { api } from '../../lib/api';
import CarritoPendiente from './CarritoPendiente';

export function SelectorContexto() {
  const { sesion, cambiarContexto, version } = usarSesion();
  const [vinculos, setVinculos] = useState([]);
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState('');
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const refrescar = () => setRevision((valor) => valor + 1);
    window.addEventListener('turno-datos', refrescar);
    return () => window.removeEventListener('turno-datos', refrescar);
  }, []);
  useEffect(() => {
    let vigente = true;
    api('/sesiones/vinculos')
      .then((datos) => {
        if (vigente) setVinculos(datos);
      })
      .catch((fallo) => {
        if (vigente) setError(fallo.message);
      });
    return () => {
      vigente = false;
    };
  }, [version, revision, sesion.id_empresa]);
  const vinculo = vinculos.find((item) => item.id_empresa === sesion.id_empresa);

  async function elegir(id, sucursal) {
    setOcupado(true);
    setError('');
    try {
      await cambiarContexto(id, sucursal);
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setOcupado(false);
    }
  }

  if (sesion.usuario.rol_plataforma === 'Superadministrador')
    return <span className="tg-badge">Administración de plataforma</span>;
  return (
    <div className="tg-context">
      {sesion.rol_empresa === 'Gerente' ? (
        <label>
          <span>Sucursal</span>
          <select
            aria-label="Sucursal activa"
            value={sesion.id_sucursal || ''}
            disabled={ocupado || !vinculo?.sucursales.length}
            onChange={(event) => elegir(vinculo.id, event.target.value)}
          >
            <option value="" disabled>
              Seleccionar sucursal
            </option>
            {vinculo?.sucursales.map((item) => (
              <option value={item.id} key={item.id}>
                {item.nombre}
              </option>
            ))}
          </select>
        </label>
      ) : (
        <span className="tg-branch-name">
          {vinculo?.sucursales.find((item) => item.id === sesion.id_sucursal)?.nombre ||
            'Sin sucursal asignada'}
        </span>
      )}
      {error && <small role="alert">{error}</small>}
    </div>
  );
}

export default function Espacio({ children }) {
  return (
    <AccesoPrivado>
      <Interior>{children}</Interior>
    </AccesoPrivado>
  );
}

function Interior({ children }) {
  const { sesion, cerrar, version, mesasHabilitadas, reservasHabilitadas } = usarSesion();
  const router = useRouter();
  const pathname = usePathname();
  const [menu, setMenu] = useState(false);
  const [error, setError] = useState('');
  const [saliendo, setSaliendo] = useState(false);
  const [empresa, setEmpresa] = useState(null);
  const gerente = sesion.rol_empresa === 'Gerente';
  const superadmin = sesion.usuario.rol_plataforma === 'Superadministrador';
  useEffect(() => {
    let vigente = true;
    setEmpresa(null);
    if (sesion.id_empresa)
      api(`/empresas/${sesion.id_empresa}`)
        .then((dato) => {
          if (vigente) setEmpresa(dato);
        })
        .catch(() => {});
    return () => {
      vigente = false;
    };
  }, [sesion.id_empresa, version]);
  useEffect(() => {
    setMenu(false);
  }, [pathname]);

  const grupos = superadmin
    ? [
        {
          nombre: 'Inicio',
          icono: 'chart',
          enlaces: [
            ['Resumen', '/panel'],
            ['Registros', '/panel/bitacora'],
          ],
        },
        {
          nombre: 'Plataforma',
          icono: 'store',
          enlaces: [
            ['Empresas', '/panel/empresas'],
            ['Usuarios', '/panel/usuarios'],
            ['Asignar gerente', '/panel/asignar-gerente'],
          ],
        },
      ]
    : [
        {
          nombre: 'Inicio',
          icono: 'chart',
          enlaces: [
            ['Resumen', '/panel'],
            ['Registros', '/panel/bitacora'],
          ],
        },
        {
          nombre: 'Operación',
          icono: 'receipt',
          enlaces: [
            ['Pedidos', '/panel/pedidos'],
            ['Nuevo pedido', '/nuevo-pedido'],
            ...(mesasHabilitadas ? [['Mesas', '/panel/mesas']] : []),
            ...(reservasHabilitadas ? [['Reservas', '/panel/reservas']] : []),
          ],
        },
        {
          nombre: 'Catálogo',
          icono: 'coffee',
          enlaces: [
            ...(gerente
              ? [
                  ['Productos', '/panel/productos'],
                  ['Categorías', '/panel/categorias'],
                ]
              : []),
            ...(gerente || sesion.rol_empresa === 'Administrador'
              ? [['Disponibilidad por local', '/panel/disponibilidad']]
              : []),
          ],
        },
        {
          nombre: 'Administración',
          icono: 'store',
          enlaces: [
            ...(gerente
              ? [
                  ['Sucursales', '/panel/sucursales'],
                  ['Empleados', '/panel/equipo'],
                  ...(sesion.finanzas_habilitadas
                    ? [['Finanzas', '/panel/finanzas']]
                    : []),
                ]
              : []),
          ],
        },
      ];
  const grupoActual = grupos.find((grupo) =>
    grupo.enlaces.some(([, href]) => href === pathname),
  )?.nombre;
  const [grupoElegido, setGrupoElegido] = useState(null);
  const grupoAbierto =
    grupoElegido?.ruta === pathname ? grupoElegido.nombre : grupoActual;
  async function salir() {
    setSaliendo(true);
    try {
      await cerrar();
      router.replace('/login');
    } catch (fallo) {
      setError(fallo.message);
      setSaliendo(false);
    }
  }

  return (
    <div
      className="tg-app"
      onKeyDown={(event) => {
        if (event.key === 'Escape') setMenu(false);
      }}
    >
      {menu && (
        <button
          className="tg-nav-backdrop"
          aria-label="Cerrar navegación"
          onClick={() => setMenu(false)}
        />
      )}
      <aside className={`tg-sidebar ${menu ? 'is-open' : ''}`}>
        <Link href="/panel" className="tg-brand">
          Turno Group
          <span />
        </Link>
        <span className="tg-sidebar-caption">EL ORDEN DETRÁS DEL SERVICIO</span>
        <nav aria-label="Panel de gestión">
          {grupos
            .filter((grupo) => grupo.enlaces.length)
            .map((grupo, indice) => {
              const abierto = grupoAbierto === grupo.nombre;
              const activo = grupoActual === grupo.nombre;
              return (
                <div className="tg-nav-group" key={grupo.nombre}>
                  <button
                    type="button"
                    className={`tg-nav-group-button ${activo ? 'is-active' : ''}`}
                    aria-expanded={abierto}
                    aria-controls={`tg-nav-group-${indice}`}
                    onClick={() =>
                      setGrupoElegido({
                        ruta: pathname,
                        nombre: abierto ? null : grupo.nombre,
                      })
                    }
                  >
                    <Icon name={grupo.icono} size={19} />
                    <span>{grupo.nombre}</span>
                    <span className="tg-nav-chevron" aria-hidden="true">
                      ⌄
                    </span>
                  </button>
                  <div
                    id={`tg-nav-group-${indice}`}
                    className="tg-nav-children"
                    hidden={!abierto}
                  >
                    {grupo.enlaces.map(([label, href]) => (
                      <Link
                        href={href}
                        key={href}
                        aria-current={pathname === href ? 'page' : undefined}
                        className={pathname === href ? 'is-current' : ''}
                        onClick={() => setMenu(false)}
                      >
                        {label}
                      </Link>
                    ))}
                  </div>
                </div>
              );
            })}
        </nav>
        <div className="tg-sidebar-bottom">
          <Link href="/invitacion">Aceptar invitación</Link>
          <Link href="/panel/configuracion">Configuración</Link>
          <button onClick={salir} disabled={saliendo}>
            {saliendo ? 'Saliendo…' : 'Cerrar sesión'}
          </button>
          <Link href="/">Volver al inicio</Link>
        </div>
      </aside>
      <div className="tg-workspace">
        <header className="tg-app-header">
          <button
            className="tg-icon-button tg-nav-toggle"
            aria-label="Abrir navegación"
            aria-expanded={menu}
            onClick={() => setMenu(!menu)}
          >
            <Icon name="menu" />
          </button>
          <div className="tg-header-business">
            <strong>
              {superadmin
                ? 'Plataforma Turno Group'
                : empresa?.nombre || 'Tu espacio de trabajo'}
            </strong>
            <span>{empresa?.tipo_negocio || 'Gestión presencial'}</span>
          </div>
          {!superadmin && <CarritoPendiente />}
          <SelectorContexto />
          <details
            className="tg-profile"
            onKeyDown={(event) => {
              if (event.key === 'Escape') {
                event.currentTarget.open = false;
                event.currentTarget.querySelector('summary').focus();
              }
            }}
          >
            <summary className="tg-user">
              <span className="tg-avatar">
                {sesion.usuario.nombre.slice(0, 1).toUpperCase()}
              </span>
              <span>
                <strong>{sesion.usuario.nombre}</strong>
                <small>{sesion.rol_empresa || sesion.usuario.rol_plataforma}</small>
              </span>
            </summary>
            <div className="tg-profile-menu">
              <Link
                href="/panel/configuracion"
                onClick={(event) => {
                  event.currentTarget.closest('details').open = false;
                }}
              >
                Configuración
              </Link>
              <button onClick={salir} disabled={saliendo}>
                {saliendo ? 'Saliendo…' : 'Cerrar sesión'}
              </button>
            </div>
          </details>
        </header>
        <main
          id="contenido"
          className="tg-main"
          key={`${sesion.id_empresa}:${sesion.id_sucursal}:${version}`}
        >
          <Mensaje error={error} />
          {typeof children === 'function'
            ? children({ empresa, gerente, superadmin })
            : children}
        </main>
        <footer className="tg-app-footer">Turno Group · Cada local, en orden.</footer>
      </div>
    </div>
  );
}
