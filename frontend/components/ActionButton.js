'use client';

import { useId, useRef } from 'react';
import Link from 'next/link';
import Icon from './Icon';

export default function ActionButton({
  children = 'Comenzar mi prueba gratis',
  className = 'button button-primary',
  intent = 'registro',
  arrow = false,
}) {
  const dialog = useRef(null);
  const titleId = useId();
  const content = {
    contacto: {
      title: 'Hablemos de tu negocio.',
      description:
        'El canal de contacto estará disponible próximamente. Mientras tanto, puedes explorar las funciones y los precios de Turno Group.',
    },
    terminos: {
      title: 'Términos de servicio.',
      description: 'Los términos de servicio están pendientes de publicación.',
    },
    privacidad: {
      title: 'Política de privacidad.',
      description: 'La política de privacidad está pendiente de publicación.',
    },
  }[intent];
  if (intent === 'acceso' || intent === 'registro') {
    return (
      <Link className={className} href={intent === 'acceso' ? '/login' : '/registro'}>
        {children}
        {arrow && <Icon name="arrow" size={17} />}
      </Link>
    );
  }
  return (
    <>
      <button className={className} onClick={() => dialog.current.showModal()}>
        {children}
        {arrow && <Icon name="arrow" size={17} />}
      </button>
      <dialog
        ref={dialog}
        className="access-dialog"
        aria-labelledby={titleId}
        onClick={(event) => {
          if (event.target === dialog.current) dialog.current.close();
        }}
      >
        <button
          className="dialog-close"
          aria-label="Cerrar ventana"
          onClick={() => dialog.current.close()}
        >
          <Icon name="close" />
        </button>
        <span className="dialog-mark">
          <Icon name="coffee" size={28} />
        </span>
        <p className="eyebrow">Turno Group</p>
        <h2 id={titleId}>{content.title}</h2>
        <p className="muted">{content.description}</p>
        <a
          className="button button-primary"
          href="#funciones"
          onClick={() => dialog.current.close()}
        >
          Conocer las funciones <Icon name="arrow" size={17} />
        </a>
      </dialog>
    </>
  );
}
