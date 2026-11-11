'use client';

import { useEffect, useRef } from 'react';
import Icon from '../Icon';

export function Mensaje({ error, aviso }) {
  if (!error && !aviso) return null;
  return (
    <div
      className={`tg-message ${error ? 'is-error' : 'is-success'}`}
      role={error ? 'alert' : 'status'}
    >
      {error || aviso}
    </div>
  );
}

export function Campo({ label, children, ayuda }) {
  return (
    <label className="tg-field">
      <span>{label}</span>
      {children}
      {ayuda && <small>{ayuda}</small>}
    </label>
  );
}

export function Vacio({
  titulo = 'Todavía no hay registros',
  detalle,
  children,
  icono = 'book',
}) {
  return (
    <div className="tg-empty">
      <span className="tg-empty-icon">
        <Icon name={icono} size={26} />
      </span>
      <h3>{titulo}</h3>
      {detalle && <p>{detalle}</p>}
      {children}
    </div>
  );
}

export function Modal({ titulo, children, cerrar }) {
  const dialogo = useRef(null);
  useEffect(() => {
    const nodo = dialogo.current;
    nodo.showModal();
    return () => nodo.close();
  }, []);
  return (
    <dialog
      ref={dialogo}
      className="tg-modal"
      aria-label={titulo}
      onCancel={(event) => {
        event.preventDefault();
        cerrar();
      }}
      onClick={(event) => {
        if (event.target === dialogo.current) cerrar();
      }}
    >
      <header>
        <h3>{titulo}</h3>
        <button
          type="button"
          className="tg-icon-button"
          onClick={cerrar}
          aria-label="Cerrar"
        >
          <Icon name="close" />
        </button>
      </header>
      {children}
    </dialog>
  );
}

export function Proximamente({ titulo, detalle }) {
  return (
    <section className="tg-card">
      <Vacio titulo={titulo} detalle={detalle} icono="receipt">
        <span className="tg-badge">Próximamente</span>
      </Vacio>
    </section>
  );
}
