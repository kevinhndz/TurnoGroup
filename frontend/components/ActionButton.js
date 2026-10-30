'use client';

import { useId, useRef } from 'react';
import Icon from './Icon';

export default function ActionButton({ children = 'Comenzar mi prueba gratis', className = 'button button-primary', intent = 'registro', arrow = false }) {
  const dialog = useRef(null);
  const titleId = useId();
  const isLogin = intent === 'acceso';
  return <>
    <button className={className} onClick={() => dialog.current.showModal()}>{children}{arrow && <Icon name="arrow" size={17} />}</button>
    <dialog ref={dialog} className="access-dialog" aria-labelledby={titleId} onClick={(event) => { if (event.target === dialog.current) dialog.current.close(); }}>
      <button className="dialog-close" aria-label="Cerrar ventana" onClick={() => dialog.current.close()}><Icon name="close" /></button>
      <span className="dialog-mark"><Icon name="coffee" size={28} /></span>
      <p className="eyebrow">Turno Group</p>
      <h2 id={titleId}>{isLogin ? 'Tu espacio de trabajo, muy pronto.' : 'Tu próximo turno empieza aquí.'}</h2>
      <p className="muted">{isLogin ? 'El acceso a tu cuenta estará disponible próximamente. Por ahora puedes conocer cómo Turno Group organiza la operación de tu negocio.' : 'Estamos preparando el registro de empresas. Pronto podrás configurar tu negocio y comenzar tu primer mes de prueba gratis.'}</p>
      <a className="button button-primary" href="#funciones" onClick={() => dialog.current.close()}>Conocer las funciones <Icon name="arrow" size={17} /></a>
    </dialog>
  </>;
}
