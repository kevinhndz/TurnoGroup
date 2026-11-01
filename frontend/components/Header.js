'use client';

import { useState } from 'react';
import ActionButton from './ActionButton';
import Icon from './Icon';
import { usarSesion } from './sistema/Sesion';

const links = [
  ['Funciones', '#funciones'],
  ['Precios', '#precios'],
  ['Contacto', '#contacto'],
];
export default function Header() {
  const { sesion } = usarSesion();
  const [open, setOpen] = useState(false);
  return (
    <header
      className="site-header"
      onKeyDown={(event) => {
        if (event.key === 'Escape') setOpen(false);
      }}
    >
      <div className="container header-inner">
        <a
          className="brand"
          href={sesion ? '/panel' : '#inicio'}
          aria-label={sesion ? 'Turno Group, resumen' : 'Turno Group, inicio'}
        >
          Turno Group
          <span className="brand-dot" />
        </a>
        <span className="brand-description">Operaciones & salón</span>
        <nav className="desktop-nav" aria-label="Navegación principal">
          {links.map(([label, href]) => (
            <a href={href} key={href}>
              {label}
            </a>
          ))}
        </nav>
        <div className="header-actions">
          <ActionButton className="login-button" intent="acceso">
            Iniciar sesión
          </ActionButton>
          <ActionButton className="button button-primary button-small">
            Iniciar prueba gratis
          </ActionButton>
        </div>
        <button
          className="menu-toggle"
          aria-label={open ? 'Cerrar menú' : 'Abrir menú'}
          aria-expanded={open}
          aria-controls="mobile-navigation"
          onClick={() => setOpen(!open)}
        >
          <Icon name={open ? 'close' : 'menu'} />
        </button>
      </div>
      {open && (
        <nav id="mobile-navigation" className="mobile-nav" aria-label="Navegación móvil">
          {links.map(([label, href]) => (
            <a href={href} key={href} onClick={() => setOpen(false)}>
              {label}
            </a>
          ))}
          <ActionButton intent="acceso" className="login-button">
            Iniciar sesión
          </ActionButton>
          <ActionButton className="button button-primary">
            Iniciar prueba gratis
          </ActionButton>
        </nav>
      )}
    </header>
  );
}
