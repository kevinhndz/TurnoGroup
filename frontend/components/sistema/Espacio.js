'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import Icon from '../Icon';
import { AccesoPrivado, usarSesion } from './Sesion';
import { Mensaje } from './Controles';
import { api } from '../../lib/api';

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
      <label>
        <span>Empresa</span>
        <select
          aria-label="Empresa activa"
          value={vinculo?.id || ''}
          disabled={ocupado || !vinculos.length}
          onChange={(event) => {
            const nuevo = vinculos.find((item) => item.id === Number(event.target.value));
            if (nuevo) elegir(nuevo.id, nuevo.sucursales[0]?.id || null);
          }}
        >
          <option value="" disabled>
            Seleccionar empresa
          </option>
          {vinculos.map((item) => (
            <option value={item.id} key={item.id}>
              {item.nombre_empresa || 'Empresa'} · {item.rol}
            </option>
          ))}
        </select>
      </label>
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

  const enlaces = superadmin
    ? [
        ['Inicio', '/panel', 'chart'],
        ['Empresas', '/panel/empresas', 'store'],
        ['Usuarios', '/panel/usuarios', 'team'],
        ['Asignar gerente', '/panel/asignar-gerente', 'team'],
      ]
    : [
        ['Inicio', '/panel', 'chart'],
        ['Pedidos', '/panel/pedidos', 'receipt'],
        ...(gerente
          ? [
              ['Productos', '/panel/productos', 'coffee'],
              ['Categorías', '/panel/categorias', 'book'],
            ]
          : []),
        ...(gerente || sesion.rol_empresa === 'Administrador'
          ? [['Disponibilidad por local', '/panel/disponibilidad', 'store']]
          : []),
        ...(gerente
          ? [
              ['Sucursales', '/panel/sucursales', 'store'],
              ['Empleados', '/panel/equipo', 'team'],
            ]
          : []),
        ...(mesasHabilitadas ? [['Mesas', '/panel/mesas', 'table']] : []),
        ...(gerente
          ? [
              ['Configuración', '/panel/configuracion', 'menu'],
              ['Categorías de gastos', '/panel/categorias-gastos', 'chart'],
            ]
          : []),
        ...(reservasHabilitadas ? [['Reservas', '/panel/reservas', 'table']] : []),
        ...(sesion.rol_empresa === 'Cajero' || gerente
          ? [['Caja diaria', '/panel/caja', 'money']]
          : []),
        ...(gerente ? [['Plan y facturación', '/panel/suscripcion', 'money']] : []),
        ...(gerente && sesion.finanzas_habilitadas
          ? [['Finanzas', '/panel/finanzas', 'chart']]
          : []),
      ];
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
          {enlaces.map(([label, href, icono]) => (
            <Link
              href={href}
              key={href}
              aria-current={pathname === href ? 'page' : undefined}
              className={pathname === href ? 'is-current' : ''}
            >
              <Icon name={icono} size={19} />
              {label}
            </Link>
          ))}
        </nav>
        <div className="tg-sidebar-bottom">
          {gerente && (
            <Link href="/configuracion-inicial" className="tg-setup-link">
              Configuración inicial <Icon name="arrow" size={16} />
            </Link>
          )}
          <Link href="/invitacion">Aceptar invitación</Link>
          <Link href="/panel/cuenta">Mi cuenta</Link>
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
          <SelectorContexto />
          <Link href="/panel/cuenta" className="tg-user">
            <span className="tg-avatar">
              {sesion.usuario.nombre.slice(0, 1).toUpperCase()}
            </span>
            <span>
              <strong>{sesion.usuario.nombre}</strong>
              <small>{sesion.rol_empresa || sesion.usuario.rol_plataforma}</small>
            </span>
          </Link>
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
